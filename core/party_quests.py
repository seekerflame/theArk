"""
Party Quest System - Multi-person quests for families and groups
Enables: Parent+child garden visits, group harvests, community service parties
"""

import time
from typing import Dict, List, Tuple, Optional

class PartyQuestSystem:
    """
    Quest system for groups: families, friends, community parties.
    
    Types:
    - duo: Parent + child (garden lessons, skill teaching)
    - party: 3-10 people (cleanups, events)
    - raid: 10-50 people (barn raising, community builds)
    """
    
    QUEST_TYPES = {
        "solo": {"min": 1, "max": 1, "bonus": 1.0},
        "duo": {"min": 2, "max": 2, "bonus": 1.2},      # 20% bonus
        "party": {"min": 3, "max": 10, "bonus": 1.5},   # 50% bonus
        "raid": {"min": 10, "max": 50, "bonus": 2.0}    # 100% bonus
    }
    
    # Age-appropriate quest categories
    CHILD_SAFE_CATEGORIES = ["garden", "education", "art", "social", "cleanup"]
    
    def __init__(self, ledger, identity, quest_system):
        self.ledger = ledger
        self.identity = identity
        self.quest_system = quest_system
        self.parties = {}  # party_id -> party data
        self.child_wallets = {}  # child_id -> parent_id link
        
    def create_party_quest(self, leader: str, quest_data: Dict) -> Tuple[bool, str]:
        """
        Create a multi-person quest.
        
        quest_data:
            title: str
            description: str
            reward_per_person: float
            quest_type: solo|duo|party|raid
            category: str
            location: optional {lat, lon}
            child_friendly: bool
            max_duration_hours: float
        """
        quest_type = quest_data.get("quest_type", "solo")
        if quest_type not in self.QUEST_TYPES:
            return False, f"Invalid quest type: {quest_type}"
        
        # Calculate total escrow needed
        type_info = self.QUEST_TYPES[quest_type]
        max_participants = type_info["max"]
        reward_per = quest_data.get("reward_per_person", 1.0)
        bonus = type_info["bonus"]
        leader_bonus = reward_per * 0.2  # Extra for organizer
        
        total_escrow = (reward_per * max_participants * bonus) + leader_bonus
        
        # Check leader has enough AT
        leader_balance = self.ledger.get_balance(leader)
        if leader_balance < total_escrow:
            return False, f"Insufficient AT. Need {total_escrow}, have {leader_balance}"
        
        party_id = f"party_{int(time.time())}_{leader[:4]}"
        
        party = {
            "id": party_id,
            "leader": leader,
            "title": quest_data["title"],
            "description": quest_data.get("description", ""),
            "reward_per_person": reward_per,
            "quest_type": quest_type,
            "category": quest_data.get("category", "general"),
            "location": quest_data.get("location"),
            "child_friendly": quest_data.get("child_friendly", False),
            "max_duration_hours": quest_data.get("max_duration_hours", 2),
            "escrow": total_escrow,
            "participants": [leader],
            "status": "open",  # open, in_progress, pending_verification, completed
            "created_at": time.time(),
            "verified_at": None
        }
        
        # Escrow the AT
        self.ledger.add_block('PARTY_ESCROW', {
            "party_id": party_id,
            "leader": leader,
            "amount": total_escrow,
            "timestamp": time.time()
        })
        
        self.parties[party_id] = party
        return True, party_id
    
    def join_party(self, party_id: str, user: str, is_child: bool = False, 
                   parent_id: str = None) -> Tuple[bool, str]:
        """Join a party quest."""
        if party_id not in self.parties:
            return False, "Party not found"
        
        party = self.parties[party_id]
        
        if party["status"] != "open":
            return False, "Party is not accepting new members"
        
        type_info = self.QUEST_TYPES[party["quest_type"]]
        if len(party["participants"]) >= type_info["max"]:
            return False, "Party is full"
        
        if user in party["participants"]:
            return False, "Already in party"
        
        # Child safety check
        if is_child:
            if not party["child_friendly"]:
                return False, "This quest is not child-friendly"
            if not parent_id:
                return False, "Children must have parent_id"
            if parent_id not in party["participants"]:
                return False, "Parent must join before child"
            
            # Link child wallet to parent
            self.child_wallets[user] = {
                "parent_id": parent_id,
                "created_at": time.time(),
                "daily_limit": 5.0  # Max 5 AT/day
            }
        
        party["participants"].append(user)
        
        # Check if minimum reached
        if len(party["participants"]) >= type_info["min"]:
            party["status"] = "ready"  # Can start anytime
        
        return True, f"Joined party! ({len(party['participants'])}/{type_info['max']})"
    
    def start_party(self, party_id: str, leader: str) -> Tuple[bool, str]:
        """Leader starts the party quest."""
        if party_id not in self.parties:
            return False, "Party not found"
        
        party = self.parties[party_id]
        
        if party["leader"] != leader:
            return False, "Only leader can start"
        
        type_info = self.QUEST_TYPES[party["quest_type"]]
        if len(party["participants"]) < type_info["min"]:
            return False, f"Need at least {type_info['min']} participants"
        
        party["status"] = "in_progress"
        party["started_at"] = time.time()
        
        return True, "Party quest started! Complete within " + \
               f"{party['max_duration_hours']} hours"
    
    def complete_party(self, party_id: str, leader: str, 
                       proof: Dict) -> Tuple[bool, str]:
        """Submit party for verification."""
        if party_id not in self.parties:
            return False, "Party not found"
        
        party = self.parties[party_id]
        
        if party["leader"] != leader:
            return False, "Only leader can submit completion"
        
        if party["status"] != "in_progress":
            return False, "Party not in progress"
        
        # Check duration
        elapsed = (time.time() - party["started_at"]) / 3600
        if elapsed > party["max_duration_hours"]:
            party["status"] = "expired"
            return False, "Party quest expired"
        
        party["status"] = "pending_verification"
        party["proof"] = proof
        party["submitted_at"] = time.time()
        
        return True, "Submitted for verification"
    
    def verify_party(self, party_id: str, verifier: str, 
                     approved: bool) -> Tuple[bool, str]:
        """Oracle/admin verifies party completion."""
        if party_id not in self.parties:
            return False, "Party not found"
        
        party = self.parties[party_id]
        
        if party["status"] != "pending_verification":
            return False, "Not pending verification"
        
        if approved:
            return self._distribute_party_rewards(party_id)
        else:
            party["status"] = "rejected"
            # Refund escrow to leader
            self.ledger.add_block('PARTY_REFUND', {
                "party_id": party_id,
                "leader": party["leader"],
                "amount": party["escrow"],
                "reason": "verification_rejected",
                "timestamp": time.time()
            })
            return False, "Party verification rejected, escrow refunded"
    
    def _distribute_party_rewards(self, party_id: str) -> Tuple[bool, str]:
        """Distribute rewards to all party members."""
        party = self.parties[party_id]
        type_info = self.QUEST_TYPES[party["quest_type"]]
        
        base_reward = party["reward_per_person"]
        bonus = type_info["bonus"]
        leader_extra = base_reward * 0.2
        
        rewards = {}
        
        for participant in party["participants"]:
            # Check if child
            is_child = participant in self.child_wallets
            
            if participant == party["leader"]:
                reward = (base_reward * bonus) + leader_extra
            elif is_child:
                reward = base_reward * bonus * 0.5  # Kids get half
            else:
                reward = base_reward * bonus
            
            # Mint reward
            self.ledger.add_block('PARTY_REWARD', {
                "party_id": party_id,
                "user": participant,
                "reward": reward,
                "is_child": is_child,
                "role": "leader" if participant == party["leader"] else "member",
                "timestamp": time.time()
            })
            
            rewards[participant] = reward
        
        party["status"] = "completed"
        party["verified_at"] = time.time()
        party["reward_distribution"] = rewards
        
        return True, f"Party complete! Rewards: {rewards}"
    
    def get_family_quests(self, location: Dict = None) -> List[Dict]:
        """Get child-friendly quests, optionally filtered by location."""
        result = []
        for party in self.parties.values():
            if party["child_friendly"] and party["status"] == "open":
                result.append(party)
        return result
    
    def get_child_wallet_info(self, child_id: str) -> Optional[Dict]:
        """Get child wallet with parental controls."""
        if child_id not in self.child_wallets:
            return None
        
        link = self.child_wallets[child_id]
        balance = self.ledger.get_balance(child_id)
        
        return {
            "child_id": child_id,
            "parent_id": link["parent_id"],
            "balance": balance,
            "daily_limit": link["daily_limit"],
            "created_at": link["created_at"]
        }


# Pre-built family quest templates
FAMILY_TEMPLATES = [
    {
        "title": "Garden Learning Day",
        "description": "Take your child to a community garden. Teach them where food comes from.",
        "reward_per_person": 1.0,
        "quest_type": "duo",
        "category": "garden",
        "child_friendly": True,
        "max_duration_hours": 3,
        "verification": "Photo of parent and child at garden"
    },
    {
        "title": "Home Harvest Sale",
        "description": "Kid harvests produce from home garden and posts for sale.",
        "reward_per_person": 0.5,
        "quest_type": "solo",
        "category": "garden",
        "child_friendly": True,
        "max_duration_hours": 24,
        "verification": "Photo of harvest + marketplace listing"
    },
    {
        "title": "Family Cleanup Crew",
        "description": "Bring the family for a neighborhood cleanup. Make it fun!",
        "reward_per_person": 1.5,
        "quest_type": "party",
        "category": "cleanup",
        "child_friendly": True,
        "max_duration_hours": 2,
        "verification": "Before/after photos"
    },
    {
        "title": "OSE Movie Night",
        "description": "Watch an OSE educational video together as a family.",
        "reward_per_person": 0.3,
        "quest_type": "party",
        "category": "education",
        "child_friendly": True,
        "max_duration_hours": 2,
        "verification": "Screenshot of completion"
    },
    {
        "title": "Skill Share: Kid Teaches Adult",
        "description": "Child teaches parent something (game, app, craft, etc.)",
        "reward_per_person": 1.0,
        "quest_type": "duo",
        "category": "education",
        "child_friendly": True,
        "max_duration_hours": 1,
        "verification": "Video clip of teaching moment"
    }
]
