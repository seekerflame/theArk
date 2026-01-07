"""
Content Filter - Violence detection and pre-moderation
From MODERATION_TRIPLE_ELEPHANT.md
"""

import re
import logging
import time

logger = logging.getLogger("ArkOS.ContentFilter")

class ContentFilter:
    """
    Pre-screen content for violence and other harmful patterns.
    Human override always required for final action.
    """
    
    # Hard-coded violence keywords (expandable)
    VIOLENCE_KEYWORDS = [
        # Direct violence
        "kill", "murder", "assassinate", "slaughter", "execute",
        # Physical harm
        "hurt", "attack", "beat", "assault", "punch", "stab", "shoot",
        # Weapons
        "bomb", "explosive", "weapon", "gun", "knife",
        # Threats
        "threat", "threaten", "die", "death threat",
        # Coordination
        "let's hurt", "help me hurt", "find and hurt"
    ]
    
    # Phrases that indicate direct threats (higher severity)
    THREAT_PATTERNS = [
        r"i('m| am) going to (kill|hurt|attack)",
        r"let('s| us) (kill|hurt|attack)",
        r"help me (find|hurt|attack)",
        r"(someone|you) should (die|be killed)",
        r"i('ll| will) (kill|murder|hurt) (you|him|her|them)"
    ]
    
    # Context modifiers (reduce severity)
    SAFE_CONTEXTS = [
        "video game", "movie", "book", "story", "fiction",
        "metaphor", "joke", "kidding", "just kidding"
    ]
    
    def __init__(self, ledger=None):
        self.ledger = ledger
        self.filter_log = []  # In-memory log for quick access
    
    def filter_content(self, text, content_id=None, user_id=None):
        """
        Analyze text for harmful content.
        Returns: (is_safe, severity, triggers, recommendation)
        """
        if not text:
            return True, 0, [], "empty"
        
        text_lower = text.lower()
        triggers = []
        severity = 0
        
        # Check for threat patterns (high severity)
        for pattern in self.THREAT_PATTERNS:
            if re.search(pattern, text_lower):
                triggers.append(f"THREAT_PATTERN: {pattern}")
                severity = max(severity, 0.9)
        
        # Check for violence keywords
        for keyword in self.VIOLENCE_KEYWORDS:
            if keyword in text_lower:
                triggers.append(f"VIOLENCE_KEYWORD: {keyword}")
                severity = max(severity, 0.5)
        
        # Check for safe context (reduces severity)
        for context in self.SAFE_CONTEXTS:
            if context in text_lower:
                severity *= 0.5  # Reduce by half
                triggers.append(f"SAFE_CONTEXT: {context}")
        
        # Determine recommendation
        if severity >= 0.9:
            recommendation = "BLOCK"  # Immediate block, escalate to human
        elif severity >= 0.5:
            recommendation = "REVIEW"  # Queue for oracle review
        elif severity >= 0.2:
            recommendation = "FLAG"  # Flag but allow
        else:
            recommendation = "ALLOW"
        
        is_safe = recommendation in ["ALLOW", "FLAG"]
        
        # Log the filter action
        self._log_action(content_id, user_id, text, triggers, severity, recommendation)
        
        return is_safe, severity, triggers, recommendation
    
    def _log_action(self, content_id, user_id, text, triggers, severity, recommendation):
        """Log filter action for transparency and auditing."""
        action = {
            "content_id": content_id,
            "user_id": user_id,
            "text_preview": text[:100] if text else "",
            "triggers": triggers,
            "severity": severity,
            "recommendation": recommendation,
            "timestamp": time.time()
        }
        
        self.filter_log.append(action)
        
        # Also log to ledger if available and content was blocked
        if self.ledger and recommendation == "BLOCK":
            self.ledger.add_block('CONTENT_BLOCKED', {
                "content_id": content_id,
                "user_id": user_id,
                "severity": severity,
                "triggers": triggers,
                "timestamp": time.time()
            })
            logger.warning(f"🚨 Content blocked: severity={severity}, triggers={triggers}")
    
    def escalate_to_oracles(self, content_id, text, user_id):
        """Escalate content to oracle review queue."""
        if self.ledger:
            self.ledger.add_block('CONTENT_ESCALATED', {
                "content_id": content_id,
                "user_id": user_id,
                "text_preview": text[:200] if text else "",
                "status": "pending_review",
                "timestamp": time.time()
            })
        logger.info(f"📋 Escalated content {content_id} to oracle review")
        return True
    
    def get_pending_reviews(self):
        """Get all content pending oracle review."""
        if not self.ledger:
            return []
        
        escalated = [
            b['data'] for b in self.ledger.blocks 
            if b['type'] == 'CONTENT_ESCALATED'
        ]
        
        # Filter out already reviewed
        reviewed_ids = {
            b['data']['content_id'] for b in self.ledger.blocks
            if b['type'] == 'CONTENT_REVIEWED'
        }
        
        return [e for e in escalated if e['content_id'] not in reviewed_ids]
    
    def submit_review(self, content_id, oracle_id, decision, note=""):
        """Oracle submits their review decision."""
        if self.ledger:
            self.ledger.add_block('CONTENT_REVIEWED', {
                "content_id": content_id,
                "oracle_id": oracle_id,
                "decision": decision,  # "approve", "remove", "warn"
                "note": note,
                "timestamp": time.time()
            })
        logger.info(f"✅ Content {content_id} reviewed by {oracle_id}: {decision}")
        return True
    
    # === BATCH OPERATIONS ===
    
    def scan_batch(self, texts):
        """Scan multiple texts, return those needing review."""
        results = []
        for i, text in enumerate(texts):
            is_safe, severity, triggers, rec = self.filter_content(text, content_id=f"batch_{i}")
            if not is_safe or rec == "REVIEW":
                results.append({
                    "index": i,
                    "severity": severity,
                    "triggers": triggers,
                    "recommendation": rec
                })
        return results
    
    # === STATISTICS ===
    
    def get_stats(self):
        """Get filter statistics."""
        total = len(self.filter_log)
        if total == 0:
            return {"total": 0}
        
        by_rec = {}
        for log in self.filter_log:
            rec = log["recommendation"]
            by_rec[rec] = by_rec.get(rec, 0) + 1
        
        return {
            "total": total,
            "by_recommendation": by_rec,
            "block_rate": by_rec.get("BLOCK", 0) / total,
            "review_rate": by_rec.get("REVIEW", 0) / total
        }


# Global instance for quick access
_filter = None

def get_filter(ledger=None):
    """Get or create the global ContentFilter instance."""
    global _filter
    if _filter is None:
        _filter = ContentFilter(ledger)
    return _filter


def quick_check(text):
    """Quick check if text is safe (doesn't log)."""
    f = ContentFilter()
    is_safe, severity, triggers, rec = f.filter_content(text)
    return is_safe, rec
