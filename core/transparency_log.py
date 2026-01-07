"""
Transparency Log - Public access to governance events
From MODERATION_TRIPLE_ELEPHANT.md

"Sunlight is the best disinfectant."
"""

import logging
import time

logger = logging.getLogger("ArkOS.TransparencyLog")

class TransparencyLog:
    """
    Provides read-only access to governance actions on the ledger.
    Ensures all bans, audits, and content removals are public.
    """
    
    GOVERNANCE_TYPES = [
        'CONTENT_BLOCKED',
        'CONTENT_REVIEWED',
        'ORACLE_STAKE',
        'ORACLE_SLASHED',
        'AUDIT_RESULT',
        'USER_BANNED',   # Hypothetical future type
        'USER_RESTORED', # Hypothetical future type
        'APPEAL_FILED',
        'APPEAL_RESOLVED'
    ]
    
    def __init__(self, ledger):
        self.ledger = ledger
    
    def get_logs(self, limit=100, offset=0, filter_type=None, filter_oracle=None):
        """
        Get paginated goverance logs.
        """
        # In a real SQL DB, we'd query efficienty. 
        # With list-based ledger, we filter in memory (fine for prototype).
        
        # 1. Filter by governance types
        relevant_blocks = [
            b for b in self.ledger.blocks 
            if b['type'] in self.GOVERNANCE_TYPES
        ]
        
        # 2. Apply filters
        filtered = []
        for b in reversed(relevant_blocks): # Newest first
            data = b['data']
            
            # Type filter
            if filter_type and b['type'] != filter_type:
                continue
                
            # Oracle filter (check various fields where oracle ID might be)
            if filter_oracle:
                authors = [
                    data.get('oracle_id'), 
                    data.get('oracle'), 
                    data.get('user_id') # Sometimes the actor
                ]
                if filter_oracle not in authors:
                    continue
            
            # sanitize data for public view (remove strict PII if any, though ledger should be clean)
            public_entry = {
                "id": b.get("id", b.get("hash")[:8]),
                "type": b['type'],
                "timestamp": b['timestamp'],
                "data": data, # Assume data on ledger is already appropriate for public (pseudonymous)
                "hash": b.get("hash")
            }
            
            filtered.append(public_entry)
        
        # 3. Pagination
        total = len(filtered)
        paged = filtered[offset : offset + limit]
        
        return {
            "logs": paged,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def get_oracle_report_card(self, oracle_id):
        """
        Compile public history for a specific oracle.
        """
        logs = self.get_logs(limit=1000, filter_oracle=oracle_id)
        
        # Calculate derived stats
        reviews_done = 0
        audits_passed = 0
        audits_failed = 0
        slashed_amount = 0
        
        for entry in logs['logs']:
            t = entry['type']
            d = entry['data']
            
            if t == 'CONTENT_REVIEWED' and d.get('oracle_id') == oracle_id:
                reviews_done += 1
            elif t == 'AUDIT_RESULT' and d.get('oracle_id') == oracle_id:
                if d.get('result') == 'approved':
                    audits_passed += 1
                else:
                    audits_failed += 1
            elif t == 'ORACLE_SLASHED' and d.get('oracle') == oracle_id:
                slashed_amount += d.get('amount', 0)
        
        return {
            "oracle_id": oracle_id,
            "history_entries": len(logs['logs']),
            "metrics": {
                "reviews_done": reviews_done,
                "audits_participated": audits_passed + audits_failed,
                "audits_passed": audits_passed,
                "slashes": slashed_amount
            }
        }
