import time
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("ArkOS.Founders")

class FoundersMove:
    """
    Organic Growth Engine: Proof of Referral.
    Incentivizes mesh expansion via time-limited multipliers.
    """
    
    def __init__(self, ledger_file: str = "founders_ledger.json"):
        self.ledger_file = ledger_file
        self.referrals = self._load_ledger()
        self.FOUNDERS_MULTIPLIER = 1.5 # 50% boost for founders
        self.CAMPAIGN_EXPIRY = 365 * 24 * 3600 # 1 year initial campaign
        
    def _load_ledger(self) -> Dict:
        try:
            with open(self.ledger_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": {}, "campaign_start": time.time()}

    def _save_ledger(self):
        with open(self.ledger_file, 'w') as f:
            json.dump(self.referrals, f, indent=4)

    def record_onboarding(self, referrer_id: str, new_user_id: str) -> bool:
        """
        Record a successful node onboarding.
        """
        if referrer_id not in self.referrals["users"]:
            self.referrals["users"][referrer_id] = {
                "referral_count": 0,
                "multiplier_expiry": time.time() + self.CAMPAIGN_EXPIRY
            }
        
        user_data = self.referrals["users"][referrer_id]
        user_data["referral_count"] += 1
        
        # Extend multiplier for every high-quality referral
        user_data["multiplier_expiry"] = max(
            user_data["multiplier_expiry"], 
            time.time() + (30 * 24 * 3600) # +30 days per referral
        )
        
        self._save_ledger()
        logger.info(f"🚀 [Founders] User {referrer_id} onboarded {new_user_id}. New Count: {user_data['referral_count']}")
        return True

    def get_current_multiplier(self, user_id: str) -> float:
        """
        Get the active multiplier for a user.
        """
        if user_id not in self.referrals["users"]:
            return 1.0
            
        user_data = self.referrals["users"][user_id]
        if time.time() < user_data["multiplier_expiry"]:
            return self.FOUNDERS_MULTIPLIER
            
        return 1.0

# Integration Demo
if __name__ == "__main__":
    fm = FoundersMove("founders_test.json")
    fm.record_onboarding("FounderAlpha", "NodeBeta")
    mult = fm.get_current_multiplier("FounderAlpha")
    print(f"User FounderAlpha Multiplier: {mult}x")
