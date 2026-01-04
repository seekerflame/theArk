import time
import logging

logger = logging.getLogger("ArkOS.Justice")

class JusticeSteward:
    """
    Handles disputes, flags, and safety grades for the village economy.
    """
    def __init__(self, ledger, identity):
        self.ledger = ledger
        self.identity = identity

    def dispute_block(self, block_hash, disputer, reason):
        """Flags a specific ledger block for investigation."""
        # Check if block exists
        block = next((b for b in self.ledger.blocks if b['hash'] == block_hash), None)
        if not block:
            return False, "Block not found"
        
        # Record dispute block
        dispute_data = {
            "target_hash": block_hash,
            "disputer": disputer,
            "reason": reason,
            "timestamp": time.time(),
            "status": "OPEN"
        }
        self.ledger.add_block('DISPUTE', dispute_data)
        logger.info(f"Block {block_hash} disputed by {disputer}: {reason}")
        return True, "Dispute recorded. An Oracle will review shortly."

    def resolve_dispute(self, dispute_hash, resolution, oracle, findings):
        """Resolves an open dispute."""
        # Find the dispute block
        dispute_block = next((b for b in self.ledger.blocks if b['hash'] == dispute_hash), None)
        if not dispute_block or dispute_block['type'] != 'DISPUTE':
            return False, "Dispute not found"

        target_hash = dispute_block['data']['target_hash']
        
        # Record resolution
        res_data = {
            "dispute_hash": dispute_hash,
            "target_hash": target_hash,
            "resolution": resolution, # MISTAKE | MALICE | VALID
            "oracle": oracle,
            "findings": findings,
            "timestamp": time.time()
        }
        self.ledger.add_block('RESOLUTION', res_data)
        
        # Adjust Safety Grade if Malice or Mistake
        target_user = self.get_target_user(target_hash)
        if target_user:
            self.adjust_safety_grade(target_user, resolution)

        logger.info(f"Dispute {dispute_hash} resolved by {oracle} as {resolution}")
        return True, "Dispute resolved."

    def get_target_user(self, block_hash):
        block = next((b for b in self.ledger.blocks if b['hash'] == block_hash), None)
        if not block: return None
        return block['data'].get('minter') or block['data'].get('worker') or block['data'].get('owner')

    def adjust_safety_grade(self, username, resolution):
        """Updates the user's safety grade in identity based on justice findings."""
        if username not in self.identity.users: return
        
        user = self.identity.users[username]
        if 'safety_grade' not in user: user['safety_grade'] = 100.0 # Start at 100
        
        if resolution == 'MISTAKE':
            user['safety_grade'] -= 5.0
        elif resolution == 'MALICE':
            user['safety_grade'] -= 20.0
            # If grade too low, strip some roles
            if user['safety_grade'] < 50:
                user['roles'] = [r for r in user.get('roles', []) if r not in ['ORACLE', 'ADMIN']]
        
        self.identity.save()

    def get_safety_grade(self, username):
        user = self.identity.users.get(username, {})
        grade = user.get('safety_grade', 100.0)
        
        if grade >= 90: return "A+ (Sovereign)"
        if grade >= 80: return "A (Trusted)"
        if grade >= 70: return "B (Reliable)"
        if grade >= 60: return "C (Developing)"
        return "D (Flagged)"

    def audit_code_contribution(self, username, lines_changed, diff_content=None):
        """
        Proactively audits a code contribution for 'BS content' or manipulation.
        Returns (is_valid, score, reason).
        """
        # 1. Check for basic manipulation (extreme line counts)
        if lines_changed > 5000:
            return False, 0, "Massive diff rejected. Break into smaller PRs for audit."
        
        # 2. Value Density Analysis (if diff provided)
        score = 1.0
        if diff_content:
            score = self._calculate_value_density(diff_content)
            
        # 3. User Reputation Check
        user_grade = self.identity.users.get(username, {}).get('safety_grade', 100.0)
        if user_grade < 60:
            score *= 0.5 # Penalty for flagged users
            
        # Decision: Reject if score is too low (e.g., mostly comments or empty lines)
        if score < 0.2:
            return False, score, f"Low value density ({score:.2f}). Mostly comments or noise."
            
        return True, score, "Logic audit passed."

    def _calculate_value_density(self, diff):
        """
        Heuristic to separate logic from noise.
        - Ignores lines starting with #, //, or empty.
        - Rewards lines with complex characters (brackets, operators).
        """
        lines = diff.split('\n')
        total_lines = len(lines)
        if total_lines == 0: return 0
        
        logic_lines = 0
        for line in lines:
            clean = line.strip()
            if not clean: continue
            if clean.startswith(('#', '//', '*', '"', "'")): continue # Comments/Strings
            if len(clean) < 3: continue # Trivial lines
            
            # Check for "Logic Markers"
            if any(char in clean for char in ['=', '(', '{', '[', ':', 'import']):
                logic_lines += 1
                
        density = logic_lines / total_lines
        return density
