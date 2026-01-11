"""
Verification Pyramid - Recursive verification with inverted incentive
From MODERATION_TRIPLE_ELEPHANT.md
"""

import random
import time
import threading
import logging

logger = logging.getLogger("ArkOS.VerificationPyramid")

class VerificationPyramid:
    """
    Users earn by doing work
    Oracles earn by verifying work
    Meta-oracles earn by auditing oracles
    
    KEY: Higher level = Higher scrutiny (inverted incentive)
    """
    
    def __init__(self, ledger, identity, oracle_stake_required=100.0):
        self.ledger = ledger
        self.identity = identity
        self.oracle_stats = {}  # oracle_id -> {verifications: int, accuracy: float, staked: float}
        self.pending_audits = {}  # audit_id -> {oracle_id, meta_oracles, votes}
        self.ORACLE_STAKE_REQUIRED = oracle_stake_required  # AT required to become oracle
        self._lock = threading.Lock()

        self.META_ORACLE_MIN_VERIFICATIONS = 100
        self.META_ORACLE_MIN_ACCURACY = 0.95
    
    # === INVERTED INCENTIVE ===
    
    def calculate_audit_frequency(self, oracle_id):
        """
        The more you verify, the more YOU get verified.
        Power doesn't scale without accountability.
        """
        stats = self.oracle_stats.get(oracle_id, {"verifications": 0})
        verified_count = stats.get("verifications", 0)
        
        if verified_count < 10:
            return 0.1   # 10% of verifications audited
        elif verified_count < 100:
            return 0.5   # 50% audited
        elif verified_count < 1000:
            return 0.9   # 90% audited
        else:
            return 1.0   # EVERY verification audited
    
    # === ORACLE STAKING ===
    
    def stake_oracle(self, user_id, amount):
        """Lock AT to become an oracle. Stake forfeited on abuse."""
        with self._lock:
            if amount < self.ORACLE_STAKE_REQUIRED:
                return False, f"Must stake at least {self.ORACLE_STAKE_REQUIRED} AT"
            
            balance = self.ledger.get_balance(user_id)
            if balance < amount:
                return False, "Insufficient AT balance"
            
            # Record stake on ledger
            self.ledger.add_block('ORACLE_STAKE', {
                'oracle': user_id,
                'amount': amount,
                'timestamp': time.time()
            })
            
            # Initialize oracle stats
            self.oracle_stats[user_id] = {
                "verifications": 0,
                "accuracy": 1.0,
                "staked": amount,
                "active": True
            }
            
            logger.info(f"🔮 {user_id} staked {amount} AT to become oracle")
            return True, "Oracle status activated"

    
    def slash_stake(self, oracle_id, reason, slash_percent=0.5):
        """Punish bad actor by slashing their stake."""
        stats = self.oracle_stats.get(oracle_id)
        if not stats:
            return False, "Oracle not found"
        
        slash_amount = stats["staked"] * slash_percent
        stats["staked"] -= slash_amount
        
        # Record slash on ledger
        self.ledger.add_block('ORACLE_SLASHED', {
            'oracle': oracle_id,
            'amount': slash_amount,
            'reason': reason,
            'timestamp': time.time()
        })
        
        # Deactivate if stake too low
        if stats["staked"] < self.ORACLE_STAKE_REQUIRED * 0.5:
            stats["active"] = False
            logger.warning(f"⚠️ Oracle {oracle_id} deactivated due to insufficient stake")
        
        logger.info(f"⚔️ Slashed {slash_amount} AT from {oracle_id}: {reason}")
        return True, f"Slashed {slash_amount} AT"
    
    # === META-ORACLE SELECTION ===
    
    def get_eligible_meta_oracles(self, exclude_oracle=None):
        """Get oracles eligible to be meta-oracles (high verification + accuracy)."""
        eligible = []
        for oracle_id, stats in self.oracle_stats.items():
            if oracle_id == exclude_oracle:
                continue
            if not stats.get("active"):
                continue
            if stats["verifications"] >= self.META_ORACLE_MIN_VERIFICATIONS:
                if stats["accuracy"] >= self.META_ORACLE_MIN_ACCURACY:
                    eligible.append(oracle_id)
        return eligible
    
    def select_meta_oracles(self, oracle_id, count=3):
        """Randomly select meta-oracles to audit an oracle."""
        eligible = self.get_eligible_meta_oracles(exclude_oracle=oracle_id)
        if len(eligible) < count:
            logger.warning(f"Only {len(eligible)} meta-oracles available")
            return eligible
        return random.sample(eligible, count)
    
    # === AUDIT PROCESS ===
    
    def queue_audit(self, oracle_id, verification_id):
        """Queue an oracle's verification for audit based on frequency."""
        frequency = self.calculate_audit_frequency(oracle_id)
        
        if random.random() > frequency:
            return None  # Not selected for audit
        
        meta_oracles = self.select_meta_oracles(oracle_id)
        if not meta_oracles:
            logger.warning("No meta-oracles available for audit")
            return None
        
        audit_id = f"audit_{oracle_id}_{int(time.time())}"
        self.pending_audits[audit_id] = {
            "oracle_id": oracle_id,
            "verification_id": verification_id,
            "meta_oracles": meta_oracles,
            "votes": {},
            "created_at": time.time(),
            "status": "pending"
        }
        
        logger.info(f"📋 Queued audit {audit_id} with {len(meta_oracles)} meta-oracles")
        return audit_id
    
    def submit_audit_vote(self, audit_id, meta_oracle_id, approved, note=""):
        """Meta-oracle submits their audit decision."""
        with self._lock:
            audit = self.pending_audits.get(audit_id)
            if not audit:
                return False, "Audit not found"
            
            if meta_oracle_id not in audit["meta_oracles"]:
                return False, "You are not assigned to this audit"
            
            audit["votes"][meta_oracle_id] = {
                "approved": approved,
                "note": note,
                "timestamp": time.time()
            }
            
            # Check if all votes in
            if len(audit["votes"]) == len(audit["meta_oracles"]):
                return self._resolve_audit(audit_id)
            
            return True, "Vote recorded"

    
    def _resolve_audit(self, audit_id):
        """Resolve audit when all votes are in."""
        audit = self.pending_audits[audit_id]
        
        approved_count = sum(1 for v in audit["votes"].values() if v["approved"])
        total_count = len(audit["votes"])
        
        # Majority required
        if approved_count > total_count / 2:
            audit["status"] = "approved"
            self._reward_oracle(audit["oracle_id"])
            result = "Oracle verification approved"
        else:
            audit["status"] = "rejected"
            self._penalize_oracle(audit["oracle_id"], audit_id)
            result = "Oracle verification rejected - stake slashed"
        
        # Record result on ledger
        self.ledger.add_block('AUDIT_RESULT', {
            "audit_id": audit_id,
            "oracle_id": audit["oracle_id"],
            "result": audit["status"],
            "votes": audit["votes"],
            "timestamp": time.time()
        })
        
        return True, result
    
    def _reward_oracle(self, oracle_id):
        """Reward oracle for good verification."""
        stats = self.oracle_stats.get(oracle_id, {})
        stats["verifications"] = stats.get("verifications", 0) + 1
        # Accuracy improves slightly
        stats["accuracy"] = min(1.0, stats.get("accuracy", 0.9) * 1.01)
        self.oracle_stats[oracle_id] = stats
    
    def _penalize_oracle(self, oracle_id, audit_id):
        """Penalize oracle for bad verification."""
        stats = self.oracle_stats.get(oracle_id, {})
        # Accuracy drops
        stats["accuracy"] = max(0.5, stats.get("accuracy", 0.9) * 0.9)
        self.oracle_stats[oracle_id] = stats
        
        # Slash stake (10% per failed audit)
        self.slash_stake(oracle_id, f"Failed audit {audit_id}", slash_percent=0.1)
    
    # === ROTATION LIMIT ===
    
    def can_verify(self, oracle_id):
        """Check if oracle can verify (max 10 cases/week)."""
        # v1.0: Uncapped verification for rapid growth.
        # Future: Implement weekly limit tracking to prevent inflation.
        stats = self.oracle_stats.get(oracle_id, {})
        if not stats.get("active"):
            return False, "Oracle not active"
        return True, "OK"
    
    # === TRANSPARENCY ===
    
    def get_oracle_stats(self, oracle_id):
        """Get public stats for an oracle."""
        stats = self.oracle_stats.get(oracle_id, {})
        return {
            "verifications": stats.get("verifications", 0),
            "accuracy": stats.get("accuracy", 0),
            "staked": stats.get("staked", 0),
            "active": stats.get("active", False),
            "audit_frequency": self.calculate_audit_frequency(oracle_id)
        }
    
    def get_all_oracles(self):
        """Get list of all active oracles with stats."""
        return [
            {"oracle_id": oid, **self.get_oracle_stats(oid)}
            for oid, stats in self.oracle_stats.items()
            if stats.get("active")
        ]
