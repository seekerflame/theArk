"""
Governance Engine - Central orchestrator for moderation and verification
Wraps VerificationPyramid, ContentFilter, and TransparencyLog
"""

import logging
from core.verification_pyramid import VerificationPyramid
from core.content_filter import ContentFilter, get_filter
from core.transparency_log import TransparencyLog

logger = logging.getLogger("ArkOS.Governance")

class GovernanceEngine:
    def __init__(self, ledger, identity):
        self.ledger = ledger
        self.identity = identity
        
        # Initialize sub-systems
        self.pyramid = VerificationPyramid(ledger, identity)
        self.filter = ContentFilter(ledger)
        self.transparency = TransparencyLog(ledger)
        
        # Set global filter instance
        global _filter
        _filter = self.filter
        
        logger.info("🏛️ Governance Engine initialized")

    # === REPORTING ===
    
    def submit_report(self, reporter_id, content_id, reason, category):
        """Submit a user report."""
        # 1. Deduct cost (prevent spam)
        cost = 0.1
        balance = self.ledger.get_balance(reporter_id)
        if balance < cost:
            return False, "Insufficient AT for reporting deposit"
            
        # 2. Log report to ledger
        import time
        report_id = f"report_{int(time.time())}_{reporter_id[:4]}"
        
        self.ledger.add_block('CONTENT_REPORTED', {
            "report_id": report_id,
            "reporter": reporter_id,
            "content_id": content_id,
            "reason": reason,
            "category": category,
            "deposit": cost,
            "status": "pending",
            "timestamp": time.time()
        })
        
        return True, report_id

    # === FILTERING ===
    
    def check_content(self, text, user_id=None):
        """Check content against violence filter."""
        return self.filter.filter_content(text, user_id=user_id)

    # === TRANSPARENCY ===
    
    def get_public_logs(self, limit=50, offset=0):
        """Get public transparency logs."""
        return self.transparency.get_logs(limit, offset)
