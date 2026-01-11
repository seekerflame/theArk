"""
Triple Verification Protocol (3-Witness System)
Prevents fraud while rewarding honest verifiers.

Core Principle: Every community quest requires 3 independent witnesses to verify completion.
All 4 parties earn rewards: doer + 3 verifiers.
"""

import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple

class TripleVerification:
    def __init__(self, ledger, identity):
        self.ledger = ledger
        self.identity = identity
        self.pending_verifications = {}  # quest_id -> verification data
        self.verification_stakes = {}     # user -> staked reputation
        
    def request_verification(self, quest_id: str, doer: str, witnesses: List[str], proof: Dict) -> Tuple[bool, str]:
        """
        Doer requests verification from 3 witnesses after completing a quest.
        
        Args:
            quest_id: Unique quest identifier
            doer: Username of person who completed the quest
            witnesses: List of 3 usernames to verify
            proof: Evidence dict (photos, geolocation, video, etc.)
        
        Returns:
            (success, message)
        """
        # Validation
        if len(witnesses) != 3:
            return False, "Exactly 3 witnesses required"
        
        if doer in witnesses:
            return False, "Cannot verify your own work"
        
        # Check witnesses exist and have minimum reputation
        for witness in witnesses:
            if witness not in self.identity.users:
                return False, f"Witness {witness} not found"
            
            # Anti-collusion: Check if witness is in doer's social graph
            if self._are_connected(doer, witness):
                return False, f"Witness {witness} is in your social network (collusion risk)"
            
            # Check witness has minimum reputation and stake
            if not self._can_verify(witness):
                return False, f"Witness {witness} lacks verification privileges (reputation too low)"
        
        # Create verification request
        verification_id = hashlib.sha256(f"{quest_id}{doer}{time.time()}".encode()).hexdigest()[:16]
        
        self.pending_verifications[verification_id] = {
            "quest_id": quest_id,
            "doer": doer,
            "witnesses": witnesses,
            "proof": proof,
            "verifications": {},  # witness -> {approved, timestamp, note}
            "created_at": time.time(),
            "status": "pending",
            "expires_at": time.time() + 86400  # 24 hour expiry
        }
        
        return True, verification_id
    
    def submit_verification(self, verification_id: str, witness: str, approved: bool, note: str = "", witness_type: str = "HUMAN") -> Tuple[bool, str]:
        """
        A witness (Human, Sensor, or AI) submits their verification decision.
        
        Returns:
            (success, message)
        """
        if verification_id not in self.pending_verifications:
            return False, "Verification request not found"
        
        v_req = self.pending_verifications[verification_id]
        
        # Check expiry
        if time.time() > v_req["expires_at"]:
            v_req["status"] = "expired"
            return False, "Verification window expired (24h)"
        
        # Check witness is authorized (for HUMAN witnesses only)
        if witness_type == "HUMAN" and witness not in v_req["witnesses"]:
            return False, "You are not an authorized witness for this quest"
        
        # Check witness hasn't already verified
        if witness in v_req["verifications"]:
            return False, "This witness/sensor has already submitted verification"
        
        # Record verification
        v_req["verifications"][witness] = {
            "approved": approved,
            "timestamp": time.time(),
            "note": note,
            "type": witness_type
        }
        
        # Check if consensus threshold is met
        # Reality Witnessing: We can now have 1 Human + 1 Sensor + 1 AI as witnesses
        if len(v_req["verifications"]) >= 3:
            return self._finalize_verification(verification_id)
        
        return True, f"Verification recorded ({len(v_req['verifications'])}/3 complete)"

    def submit_sensor_verification(self, verification_id: str, sensor_id: str, data: Dict) -> Tuple[bool, str]:
        """Automated verification from a Hardware Bridge sensor."""
        # Logic to verify data values (e.g., 'solar_voltage' > threshold)
        approved = data.get('verified', False)
        return self.submit_verification(verification_id, sensor_id, approved, note=f"Sensor Data Input: {list(data.keys())}", witness_type="SENSOR")

    def submit_ai_verification(self, verification_id: str, ai_agent_id: str, analysis: str, confidence: float) -> Tuple[bool, str]:
        """Automated verification from an AI Auditor (e.g., image analysis)."""
        approved = confidence > 0.95
        return self.submit_verification(verification_id, ai_agent_id, approved, note=f"AI Analysis: {analysis} (Conf: {confidence})", witness_type="AI")
    
    def _finalize_verification(self, verification_id: str) -> Tuple[bool, str]:
        """
        Called when all 3 witnesses have submitted their decision.
        Calculates consensus and distributes rewards.
        """
        v_req = self.pending_verifications[verification_id]
        
        # Count approvals
        approvals = sum(1 for v in v_req["verifications"].values() if v["approved"])
        
        # Consensus threshold: 2 out of 3 (66%)
        quest_approved = approvals >= 2
        
        if quest_approved:
            # Distribute rewards
            reward_tx = self._distribute_rewards(v_req)
            v_req["status"] = "approved"
            v_req["reward_tx"] = reward_tx
            
            # Issue digital badge/stamp to doer
            self._issue_badge(v_req["doer"], v_req["quest_id"])
            
            return True, f"Quest verified! Rewards distributed: {reward_tx}"
        else:
            # Quest failed verification
            v_req["status"] = "rejected"
            
            # Penalize dishonest witnesses if applicable
            self._audit_witnesses(v_req)
            
            return False, "Quest verification failed (insufficient witness approval)"
    
    def _distribute_rewards(self, v_req: Dict) -> Dict:
        """
        Distribute rewards to doer and witnesses.
        
        Distribution:
        - Doer: Base quest reward (full AT amount)
        - Each witness: 15% of base reward (0.15x)
        
        Total cost: 1.45x base reward
        """
        # Get quest details to determine base reward
        quest_data = self._get_quest_data(v_req["quest_id"])
        base_reward = quest_data.get("reward", 1.0)  # Default 1 AT if not specified
        
        # Calculate tier multiplier based on quest category
        tier = quest_data.get("tier", "physical")  # physical, skill, social
        tier_multipliers = {
            "physical": 1.0,    # Full value for physical labor
            "skill": 0.5,       # Half value for skill transfer
            "social": 0.2       # Lower value for social capital
        }
        tier_mult = tier_multipliers.get(tier, 1.0)
        
        doer_reward = base_reward * tier_mult
        witness_reward = doer_reward * 0.15
        
        # Mint rewards
        rewards = {}
        
        # Mint for doer
        self.ledger.add_block('QUEST_COMPLETION', {
            "user": v_req["doer"],
            "quest_id": v_req["quest_id"],
            "reward": doer_reward,
            "tier": tier,
            "verification_id": v_req.get("quest_id"),
            "timestamp": time.time()
        })
        rewards[v_req["doer"]] = doer_reward
        
        # Mint for witnesses who approved
        for witness, v_data in v_req["verifications"].items():
            if v_data["approved"]:
                self.ledger.add_block('WITNESS_REWARD', {
                    "witness": witness,
                    "quest_id": v_req["quest_id"],
                    "doer": v_req["doer"],
                    "reward": witness_reward,
                    "timestamp": time.time()
                })
                rewards[witness] = witness_reward
        
        return rewards
    
    def _issue_badge(self, user: str, quest_id: str):
        """Issue a digital badge/stamp NFT to user's profile."""
        user_data = self.identity.users.get(user, {})
        
        if "badges" not in user_data:
            user_data["badges"] = []
        
        badge = {
            "quest_id": quest_id,
            "earned_at": time.time(),
            "type": "quest_completion",
            "verified": True
        }
        
        user_data["badges"].append(badge)
        self.identity.save()
    
    def _can_verify(self, user: str) -> bool:
        """Check if user has sufficient reputation to act as witness."""
        user_data = self.identity.users.get(user, {})
        
        # Minimum requirements:
        # - At least 3 completed quests
        # - Verification accuracy > 90% (if they've verified before)
        # - Not currently penalized
        
        completed_quests = len(user_data.get("badges", []))
        if completed_quests < 3:
            return False
        
        # Check verification history
        accuracy = self._get_verification_accuracy(user)
        if accuracy < 0.90:
            return False
        
        # Check if penalized
        if user_data.get("verification_banned", False):
            return False
        
        return True
    
    def _get_verification_accuracy(self, user: str) -> float:
        """
        Calculate historical accuracy of user's verifications.
        
        Accuracy = (Correct verifications) / (Total verifications)
        """
        # Query ledger for user's verification history
        blocks = self.ledger.blocks
        
        total_verifications = 0
        correct_verifications = 0
        
        for v_id, v_req in self.pending_verifications.items():
            if v_req["status"] not in ["approved", "rejected"]:
                continue
            
            if user in v_req.get("verifications", {}):
                total_verifications += 1
                user_vote = v_req["verifications"][user]["approved"]
                final_result = v_req["status"] == "approved"
                
                # User was correct if their vote aligned with final consensus
                if user_vote == final_result:
                    correct_verifications += 1
        
        if total_verifications == 0:
            return 1.0  # Benefit of the doubt for new verifiers
        
        return correct_verifications / total_verifications
    
    def _are_connected(self, user1: str, user2: str) -> bool:
        """
        Check if two users are connected in social graph (anti-collusion).
        
        For now, simple implementation: check if they've transacted recently.
        # v1.0 Baseline: Transaction proximity check.
        # Future: High-order spectral clustering of social graph.
        """
        # Check recent transactions between users
        blocks = self.ledger.blocks[-500:]  # Last 500 blocks
        
        tx_count = 0
        for block in blocks:
            if block["type"] == "TX":
                data = block["data"]
                if (data.get("sender") == user1 and data.get("receiver") == user2) or \
                   (data.get("sender") == user2 and data.get("receiver") == user1):
                    tx_count += 1
        
        # If more than 5 transactions in recent history, consider them connected
        return tx_count > 5
    
    def _audit_witnesses(self, v_req: Dict):
        """
        Audit witnesses if verification failed.
        Penalize witnesses who consistently vote incorrectly.
        """
        # If quest failed but some witnesses approved, investigate
        for witness, v_data in v_req["verifications"].items():
            accuracy = self._get_verification_accuracy(witness)
            
            # If accuracy drops below 70%, suspend verification privileges
            if accuracy < 0.70:
                user_data = self.identity.users.get(witness, {})
                user_data["verification_banned"] = True
                user_data["ban_reason"] = "Low verification accuracy"
                user_data["banned_at"] = time.time()
                self.identity.save()
    
    def _get_quest_data(self, quest_id: str) -> Dict:
        """Retrieve quest details from ledger or quest system."""
        # v1.0: Using hardcoded quest tiers.
        # Future: Dynamic lookup from QuestSystem via quest_id.
        # For now, return mock data
        return {
            "id": quest_id,
            "reward": 1.0,
            "tier": "physical"
        }
    
    def get_pending_verifications_for_user(self, user: str) -> List[Dict]:
        """Get all verification requests where user is a witness."""
        result = []
        
        for v_id, v_req in self.pending_verifications.items():
            if user in v_req["witnesses"] and user not in v_req["verifications"]:
                # User hasn't verified yet and is a witness
                if time.time() < v_req["expires_at"]:
                    result.append({
                        "verification_id": v_id,
                        "quest_id": v_req["quest_id"],
                        "doer": v_req["doer"],
                        "proof": v_req["proof"],
                        "expires_in": v_req["expires_at"] - time.time()
                    })
        
        return result
