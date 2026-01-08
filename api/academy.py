"""
Academy API - Learn-to-Earn endpoints.
"""

import time
import json
from typing import Dict, List

class AcademyAPI:
    def __init__(self, ledger, wisdom_engine):
        self.ledger = ledger
        self.wisdom = wisdom_engine
        self.syntheses = []

    # Complexity Multiplier Map
    COMPLEXITY_LEVELS = {
        "foundation": 1.0,  # Algebra, Basic Tools
        "core": 1.5,        # Physics, Chemistry, Basic Engineering
        "advanced": 3.0,    # Thermodynamics, BIM, System Design
        "mastery": 5.0      # GPM Meta-How-To, Civilization Arch
    }

    def submit_synthesis(self, user: str, data: Dict):
        """
        Record a learning synthesis and reward the user.
        Reward scales based on the complexity level of the subject.
        """
        text = data.get("text", "")
        source = data.get("source", "general")
        tags = data.get("tags", ["foundation"])
        
        # Determine multiplier based on highest tag
        multiplier = 1.0
        for tag in tags:
            if tag in self.COMPLEXITY_LEVELS:
                multiplier = max(multiplier, self.COMPLEXITY_LEVELS[tag])

        reward = 0.1 * multiplier
        
        synthesis = {
            "user": user,
            "text": text,
            "source": source,
            "complexity": multiplier,
            "timestamp": time.time()
        }
        self.syntheses.append(synthesis)

        # Reward: AT for synthesis
        self.ledger.add_block('MINT', {
            "to": user,
            "amount": reward,
            "reason": f"Wisdom Synthesis ({multiplier}x): {source}",
            "complexity": multiplier,
            "timestamp": time.time()
        })

        return {"status": "success", "reward": reward, "complexity": multiplier}

def register_academy_routes(router, academy, auth_decorator):
    @router.get('/api/academy/wisdom')
    def h_get_wisdom(h, p):
        h.send_json(academy.get_wisdom_snippet())

    @router.get('/api/academy/tree')
    def h_get_tree(h, p):
        h.send_json({"mermaid": academy.get_skill_tree()})

    @router.post('/api/academy/synthesis')
    @auth_decorator
    def h_submit_synthesis(h, user, p):
        result = academy.submit_synthesis(user['sub'], p)
        h.send_json(result)
