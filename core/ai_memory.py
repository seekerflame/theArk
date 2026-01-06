"""
AI Memory System - Ledger-based learning
Enables Antigravity to remember and learn from every block
"""
import json
import hashlib
from datetime import datetime
from collections import defaultdict

class AIMemory:
    """Persistent memory system integrated with ledger"""
    
    def __init__(self, ledger):
        self.ledger = ledger
        self.knowledge_graph = defaultdict(list)
        self.patterns = {}
        self.last_indexed_block = 0
        
    def index_ledger(self):
        """Index all blocks for learning"""
        new_blocks = []
        for i, block in enumerate(self.ledger.blocks):
            if i > self.last_indexed_block:
                new_blocks.append(block)
                self.learn_from_block(block)
        
        self.last_indexed_block = len(self.ledger.blocks) - 1
        return len(new_blocks)
    
    def learn_from_block(self, block):
        """Extract knowledge from a single block"""
        block_type = block.get('type')
        data = block.get('data', {})
        
        # Learn patterns by type
        if block_type not in self.patterns:
            self.patterns[block_type] = {
                'count': 0,
                'common_fields': set(),
                'examples': []
            }
        
        pattern = self.patterns[block_type]
        pattern['count'] += 1
        pattern['common_fields'].update(data.keys())
        
        if len(pattern['examples']) < 5:
            pattern['examples'].append(data)
        
        # Build knowledge graph connections
        if 'username' in data:
            user = data['username']
            self.knowledge_graph[f"user:{user}"].append({
                'type': block_type,
                'timestamp': block.get('timestamp'),
                'data': data
            })
        
        if 'quest_id' in data:
            quest = data['quest_id']
            self.knowledge_graph[f"quest:{quest}"].append({
                'type': block_type,
                'timestamp': block.get('timestamp'),
                'data': data
            })
    
    def recall(self, query_type, query_value):
        """Recall relevant information"""
        key = f"{query_type}:{query_value}"
        return self.knowledge_graph.get(key, [])
    
    def get_user_history(self, username):
        """Get all blocks related to a user"""
        return self.recall('user', username)
    
    def get_quest_history(self, quest_id):
        """Get all blocks related to a quest"""
        return self.recall('quest', quest_id)
    
    def analyze_patterns(self):
        """Analyze learned patterns"""
        analysis = {}
        for block_type, pattern in self.patterns.items():
            analysis[block_type] = {
                'total_count': pattern['count'],
                'fields': list(pattern['common_fields']),
                'sample': pattern['examples'][0] if pattern['examples'] else None
            }
        return analysis
    
    def suggest_improvements(self):
        """AI suggests system improvements based on patterns"""
        suggestions = []
        
        # Check for error patterns
        if 'ERROR' in self.patterns:
            error_count = self.patterns['ERROR']['count']
            if error_count > 10:
                suggestions.append({
                    'type': 'error_reduction',
                    'severity': 'HIGH',
                    'message': f'{error_count} errors detected. Suggest implementing error prevention.',
                    'action': 'Review error patterns and add validation'
                })
        
        # Check for quest completion rates
        if 'QUEST' in self.patterns and 'QUEST_UPDATE' in self.patterns:
            total_quests = self.patterns['QUEST']['count']
            completions = sum(1 for ex in self.patterns['QUEST_UPDATE']['examples'] 
                            if ex.get('status') == 'COMPLETED')
            
            if total_quests > 0:
                completion_rate = completions / total_quests
                if completion_rate < 0.5:
                    suggestions.append({
                        'type': 'quest_optimization',
                        'severity': 'MEDIUM',
                        'message': f'Low quest completion rate ({completion_rate:.0%}). Suggest simplifying quests.',
                        'action': 'Review quest difficulty and requirements'
                    })
        
        return suggestions

def create_ai_memory_api(router, ledger, requires_auth):
    """API endpoints for AI memory system"""
    
    ai_memory = AIMemory(ledger)
    
    @router.post('/api/ai/index')
    def h_index_ledger(h):
        """Trigger AI to index ledger"""
        count = ai_memory.index_ledger()
        h.send_json({'indexed': count, 'total_blocks': len(ledger.blocks)})
    
    @router.get('/api/ai/patterns')
    def h_get_patterns(h):
        """Get learned patterns"""
        patterns = ai_memory.analyze_patterns()
        h.send_json(patterns)
    
    @router.get('/api/ai/suggestions')
    def h_get_suggestions(h):
        """Get AI improvement suggestions"""
        suggestions = ai_memory.suggest_improvements()
        h.send_json({'suggestions': suggestions, 'count': len(suggestions)})
    
    @router.get('/api/ai/recall/<query_type>/<query_value>')
    def h_recall(h, query_type, query_value):
        """Recall information about an entity"""
        results = ai_memory.recall(query_type, query_value)
        h.send_json({'query': f"{query_type}:{query_value}", 'results': results})
