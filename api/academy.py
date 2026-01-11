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
        self.missions = [
            {
                "id": "genesis_01",
                "class": "BRONZE",
                "title": "Protocol Greeting",
                "description": "Welcome to the Ark. Verify your understanding of $0/month living.",
                "reward_at": 10.0,
                "reward_xp": 100,
                "requires_physical": False
            },
            {
                "id": "build_01",
                "class": "SILVER",
                "title": "Modular Frame Assembly",
                "description": "Learn the CEB press mechanics and frame welding basics.",
                "reward_at": 25.0,
                "reward_xp": 500,
                "requires_physical": True
            }
        ]

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

    def get_wisdom_snippet(self):
        """
        Retrieve a wisdom snippet from the wisdom engine or return a default.
        """
        if hasattr(self.wisdom, 'get_snippet'):
             return self.wisdom.get_snippet()
        
        # Fallback quotes if wisdom engine is simple or not ready
        import random
        quotes = [
            "The best time to plant a tree was 20 years ago. The second best time is now.",
            "Freedom is not given, it is built.",
            "Resilience is the ability to adapt to change.",
            "Community is the greatest form of wealth.",
            "Knowledge shared is power multiplied."
        ]
        return {"quote": random.choice(quotes), "author": "Anonymous"}

    def get_skill_tree(self):
        """
        Return the Mermaid JS definition for the skill tree.
        """
        return """
        graph TD
            A[Survivor] --> B(Builder)
            A --> C(Gardener)
            B --> D[Architect]
            B --> E[Engineer]
            C --> F[Botanist]
            C --> G[Healer]
        """

    def get_missions(self):
        return self.missions

    def claim_mission(self, user_id, mission_id):
        mission = next((m for m in self.missions if m['id'] == mission_id), None)
        if not mission:
            return False, "Mission not found"
        
        if mission['requires_physical']:
            return False, "This mission requires physical verification from a Mentor."

        # Reward AT
        self.ledger.add_block('ACADEMY_REWARD', {
            "user": user_id,
            "mission_id": mission_id,
            "reward_at": mission['reward_at'],
            "timestamp": time.time()
        })
        return True, mission['reward_at']

    def verify_physical(self, mentor_id, student_id, mission_id):
        # In a real scenario, check mentor_id role
        mission = next((m for m in self.missions if m['id'] == mission_id), None)
        if not mission:
            return False, "Mission not found"

        self.ledger.add_block('ACADEMY_PHYSICAL_VERIFY', {
            "mentor": mentor_id,
            "student": student_id,
            "mission_id": mission_id,
            "reward_at": mission['reward_at'],
            "timestamp": time.time()
        })
        return True, f"Verified {student_id} for {mission_id}"

def register_academy_routes(router, academy, auth_decorator):
    @router.get('/api/academy/wisdom')
    def h_get_wisdom(h):
        h.send_json(academy.get_wisdom_snippet())

    @router.get('/api/academy/tree')
    def h_get_tree(h):
        h.send_json({"mermaid": academy.get_skill_tree()})

    @router.post('/api/academy/synthesis')
    @auth_decorator
    def h_submit_synthesis(h, user, p):
        result = academy.submit_synthesis(user['sub'], p)
        h.send_json(result)

    @router.get('/api/academy/missions')
    def h_get_missions(h):
        h.send_json({"missions": academy.get_missions()})

    @router.post('/api/academy/claim')
    @auth_decorator
    def h_claim_mission(h, user, p):
        mission_id = p.get('mission_id')
        success, reward = academy.claim_mission(user['sub'], mission_id)
        if success:
            h.send_json({"status": "success", "reward_at": reward, "reward_xp": 100})
        else:
            h.send_json_error(reward)

    @router.post('/api/academy/verify_physical')
    @auth_decorator
    def h_verify_physical(h, user, p):
        student_id = p.get('student_id')
        mission_id = p.get('mission_id')
        success, message = academy.verify_physical(user['sub'], student_id, mission_id)
        if success:
            h.send_json({"status": "success", "message": message})
        else:
            h.send_json_error(message)
