"""
Community Quest System
Enables public quest posting, claiming, and verification for the Community Bridge.
"""

import time
import json
from typing import Dict, List, Optional, Tuple

class QuestSystem:
    def __init__(self, ledger, identity):
        self.ledger = ledger
        self.identity = identity
        self.active_quests = {}  # quest_id -> quest data
        self.claimed_quests = {}  # quest_id -> claimant
        
    def post_quest(self, poster: str, quest_data: Dict) -> Tuple[bool, str]:
        """
        Post a new community quest.
        
        Args:
            poster: Username of quest poster
            quest_data: {
                "title": str,
                "description": str,
                "reward": float (AT amount),
                "tier": "physical"|"skill"|"social",
                "duration": int (estimated minutes),
                "location": optional dict with lat/lon,
                "required_skills": optional list of skills,
                "expires_at": optional timestamp
            }
        
        Returns:
            (success, quest_id or error message)
        """
        # Validate quest data
        required_fields = ["title", "description", "reward", "tier"]
        for field in required_fields:
            if field not in quest_data:
                return False, f"Missing required field: {field}"
        
        # Validate tier
        if quest_data["tier"] not in ["physical", "skill", "social"]:
            return False, "Tier must be 'physical', 'skill', or 'social'"
        
        # Check poster has sufficient AT to fund quest
        reward = float(quest_data["reward"])
        # Total cost includes witness rewards (3 * 0.15 = 0.45x)
        total_cost = reward * 1.45
        
        poster_balance = self.ledger.get_balance(poster)
        if poster_balance < total_cost:
            return False, f"Insufficient AT. Need {total_cost}, have {poster_balance}"
        
        # Create quest
        quest_id = f"quest_{int(time.time())}_{poster[:4]}"
        
        quest = {
            "id": quest_id,
            "poster": poster,
            "title": quest_data["title"],
            "description": quest_data["description"],
            "reward": reward,
            "tier": quest_data["tier"],
            "duration": quest_data.get("duration", 60),  # default 1 hour
            "location": quest_data.get("location"),
            "required_skills": quest_data.get("required_skills", []),
            "created_at": time.time(),
            "expires_at": quest_data.get("expires_at", time.time() + 604800),  # default 7 days
            "status": "open",
            "claimed_by": None
        }
        
        self.active_quests[quest_id] = quest
        
        # Escrow the funds (lock AT for quest)
        self.ledger.add_block('QUEST_POST', {
            "quest_id": quest_id,
            "poster": poster,
            "total_cost": total_cost,
            "escrowed": True,
            "timestamp": time.time()
        })
        
        return True, quest_id
    
    def claim_quest(self, quest_id: str, claimant: str) -> Tuple[bool, str]:
        """User claims a quest to work on it."""
        if quest_id not in self.active_quests:
            return False, "Quest not found"
        
        quest = self.active_quests[quest_id]
        
        # Check quest is still open
        if quest["status"] != "open":
            return False, f"Quest is {quest['status']}, not open"
        
        # Check not expired
        if time.time() > quest["expires_at"]:
            quest["status"] = "expired"
            return False, "Quest has expired"
        
        # Check claimant has required skills (if any)
        required_skills = quest.get("required_skills", [])
        if required_skills:
            claimant_data = self.identity.users.get(claimant, {})
            claimant_skills = claimant_data.get("skills", [])
            
            missing_skills = [s for s in required_skills if s not in claimant_skills]
            if missing_skills:
                return False, f"Missing required skills: {', '.join(missing_skills)}"
        
        # Claim quest
        quest["status"] = "claimed"
        quest["claimed_by"] = claimant
        quest["claimed_at"] = time.time()
        
        self.ledger.add_block('QUEST_CLAIM', {
            "quest_id": quest_id,
            "claimant": claimant,
            "timestamp": time.time()
        })
        
        return True, f"Quest claimed! Complete within {quest['duration']} minutes."
    
    def get_available_quests(self, user: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get all available quests for a user.
        
        Filters can include:
        - tier: physical/skill/social
        - location: {lat, lon, radius_km}
        - skills: list of user's skills
        - min_reward: minimum AT reward
        """
        result = []
        
        for quest_id, quest in self.active_quests.items():
            # Skip claimed/completed quests
            if quest["status"] != "open":
                continue
            
            # Skip expired
            if time.time() > quest["expires_at"]:
                quest["status"] = "expired"
                continue
            
            # Apply filters
            if filters:
                if "tier" in filters and quest["tier"] != filters["tier"]:
                    continue
                
                if "min_reward" in filters and quest["reward"] < filters["min_reward"]:
                    continue
                
                # Location filter (if quest has location and filter specifies location)
                if "location" in filters and quest.get("location"):
                    user_location = filters["location"]
                    quest_location = quest["location"]
                    distance = self._calculate_distance(
                        user_location["lat"], user_location["lon"],
                        quest_location["lat"], quest_location["lon"]
                    )
                    radius = filters["location"].get("radius_km", 10)
                    if distance > radius:
                        continue
            
            result.append(quest)
        
        # Sort by reward (highest first)
        result.sort(key=lambda q: q["reward"], reverse=True)
        
        return result
    
    def get_quest(self, quest_id: str) -> Optional[Dict]:
        """Get a specific quest by ID."""
        return self.active_quests.get(quest_id)
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates in kilometers.
        Uses Haversine formula.
        """
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        #Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    def cancel_quest(self, quest_id: str, user: str) -> Tuple[bool, str]:
        """Cancel a quest and refund escrowed AT."""
        if quest_id not in self.active_quests:
            return False, "Quest not found"
        
        quest = self.active_quests[quest_id]
        
        # Only poster can cancel
        if quest["poster"] != user:
            return False, "Only quest poster can cancel"
        
        # Can't cancel if already claimed
        if quest["status"] == "claimed":
            return False, "Quest is already claimed, cannot cancel"
        
        # Refund escrowed AT
        total_cost = quest["reward"] * 1.45
        self.ledger.add_block('QUEST_CANCEL', {
            "quest_id": quest_id,
            "poster": user,
            "refund": total_cost,
            "timestamp": time.time()
        })
        
        quest["status"] = "cancelled"
        
        return True, f"Quest cancelled. {total_cost} AT refunded."


class QuestTemplates:
    """Pre-built quest templates for common scenarios."""
    
    @staticmethod
    def bar_crawl_bingo() -> Dict:
        return {
            "title": "Bar Crawl Bingo",
            "description": "Visit 5 bars, complete micro-quests at each (learn bartender's name, try new drink, photo with 2 people)",
            "reward": 0.5,
            "tier": "social",
            "duration": 240,  # 4 hours
            "required_proof": ["photos", "bartender_verification"]
        }
    
    @staticmethod
    def photo_scavenger_hunt(location: str) -> Dict:
        return {
            "title": f"Photo Scavenger Hunt: {location}",
            "description": "Photograph 20 items: street art with blue, someone walking dog, handwritten sign, etc.",
            "reward": 0.3,
            "tier": "social",
            "duration": 90,
            "required_proof": ["photos_with_geotags"]
        }
    
    @staticmethod
    def skill_exchange(teach_skill: str, learn_skill: str) -> Dict:
        return {
            "title": f"Skill Exchange: {teach_skill} ↔ {learn_skill}",
            "description": f"1 hour exchange: I teach you {teach_skill}, you teach me {learn_skill}",
            "reward": 1.0,
            "tier": "skill",
            "duration": 60,
            "required_skills": [learn_skill]
        }
    
    @staticmethod
    def art_walk_discovery() -> Dict:
        return {
            "title": "Art Walk Discovery",
            "description": "Talk to 3 local artists, photograph your favorite piece, share why you like it",
            "reward": 0.3,
            "tier": "social",
            "duration": 60,
            "required_proof": ["artist_verification", "photo_with_reflection"]
        }
    
    @staticmethod
    def local_shop_support(shop_name: str, task: str) -> Dict:
        return {
            "title": f"{shop_name}: {task}",
            "description": f"Help {shop_name} with: {task}",
            "reward": 2.0,  # 2 hours of work
            "tier": "physical",
            "duration": 120,
            "required_proof": ["shop_owner_verification"]
        }
