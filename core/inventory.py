"""
Inventory System - Track personal items, reduce waste, highlight opportunities
Enables users to know where their stuff is and share/lend/trade with community
"""

import time
from typing import Dict, List, Optional, Tuple

class InventorySystem:
    def __init__(self, ledger, identity):
        self.ledger = ledger
        self.identity = identity
        self.items = {}  # item_id -> item data
        
    def add_item(self, owner: str, item_data: Dict) -> Tuple[bool, str]:
        """
        Add an item to owner's inventory.
        
        Args:
            owner: Username of item owner
            item_data: {
                "name": str,
                "description": str,
                "category": str (tools/clothing/electronics/food/other),
                "condition": str (new/like_new/good/fair/parts),
                "location": optional str (where is it stored),
                "available_for": list (lending/selling/trading/gifting),
                "estimated_value_at": optional float,
                "photo_url": optional str
            }
        
        Returns:
            (success, item_id or error message)
        """
        required = ["name", "category"]
        for field in required:
            if field not in item_data:
                return False, f"Missing required field: {field}"
        
        item_id = f"item_{int(time.time())}_{owner[:4]}"
        
        item = {
            "id": item_id,
            "owner": owner,
            "name": item_data["name"],
            "description": item_data.get("description", ""),
            "category": item_data["category"],
            "condition": item_data.get("condition", "good"),
            "location": item_data.get("location", ""),
            "available_for": item_data.get("available_for", []),
            "estimated_value_at": item_data.get("estimated_value_at", 0),
            "photo_url": item_data.get("photo_url"),
            "created_at": time.time(),
            "provenance": [{
                "action": "added",
                "by": owner,
                "at": time.time(),
                "notes": "Initial entry"
            }]
        }
        
        self.items[item_id] = item
        
        # Log to ledger
        self.ledger.add_block('INVENTORY_ADD', {
            "item_id": item_id,
            "owner": owner,
            "name": item["name"],
            "category": item["category"],
            "timestamp": time.time()
        })
        
        return True, item_id
    
    def transfer_item(self, item_id: str, from_user: str, to_user: str, 
                      transfer_type: str, at_amount: float = 0, notes: str = "") -> Tuple[bool, str]:
        """
        Transfer item ownership (sell, gift, lend, trade).
        
        transfer_type: sell | gift | lend | trade | return
        """
        if item_id not in self.items:
            return False, "Item not found"
        
        item = self.items[item_id]
        
        # Can only transfer if you own it (or returning borrowed item)
        if transfer_type == "return":
            if item.get("borrowed_by") != from_user:
                return False, "You don't have this item borrowed"
        else:
            if item["owner"] != from_user:
                return False, "You don't own this item"
        
        # Handle payment for sales
        if transfer_type == "sell" and at_amount > 0:
            # Check buyer has funds
            buyer_balance = self.ledger.get_balance(to_user)
            if buyer_balance < at_amount:
                return False, f"Buyer has insufficient AT ({buyer_balance} < {at_amount})"
            
            # Transfer AT
            self.ledger.add_block('TRANSFER', {
                "from": to_user,
                "to": from_user,
                "amount": at_amount,
                "reason": f"Item purchase: {item['name']}",
                "timestamp": time.time()
            })
        
        # Update provenance
        item["provenance"].append({
            "action": transfer_type,
            "from": from_user,
            "to": to_user,
            "at_amount": at_amount,
            "at": time.time(),
            "notes": notes
        })
        
        # Update ownership
        if transfer_type == "lend":
            item["borrowed_by"] = to_user
            item["lent_at"] = time.time()
        elif transfer_type == "return":
            del item["borrowed_by"]
            del item["lent_at"]
        else:
            item["owner"] = to_user
        
        # Log to ledger
        self.ledger.add_block('INVENTORY_TRANSFER', {
            "item_id": item_id,
            "from": from_user,
            "to": to_user,
            "type": transfer_type,
            "at_amount": at_amount,
            "timestamp": time.time()
        })
        
        return True, f"Item {transfer_type}ed successfully"
    
    def get_my_inventory(self, user: str) -> List[Dict]:
        """Get all items owned by user."""
        return [item for item in self.items.values() if item["owner"] == user]
    
    def get_my_borrowed(self, user: str) -> List[Dict]:
        """Get all items user has borrowed."""
        return [item for item in self.items.values() if item.get("borrowed_by") == user]
    
    def get_available_items(self, category: str = None, availability: str = None) -> List[Dict]:
        """
        Get items available for lending/selling/trading.
        
        availability: lending | selling | trading | gifting
        """
        result = []
        for item in self.items.values():
            if not item["available_for"]:
                continue
            
            if category and item["category"] != category:
                continue
            
            if availability and availability not in item["available_for"]:
                continue
            
            result.append(item)
        
        return result
    
    def get_provenance(self, item_id: str) -> Optional[List[Dict]]:
        """Get full history of an item."""
        if item_id not in self.items:
            return None
        return self.items[item_id]["provenance"]
    
    def search_items(self, query: str) -> List[Dict]:
        """Search items by name/description."""
        query_lower = query.lower()
        return [
            item for item in self.items.values()
            if query_lower in item["name"].lower() 
            or query_lower in item.get("description", "").lower()
        ]
    
    def highlight_opportunities(self, user: str) -> Dict:
        """
        Analyze user's inventory and highlight opportunities:
        - Items not used recently (maybe lend/sell?)
        - Items others are looking for
        - Items available nearby that user might need
        """
        my_items = self.get_my_inventory(user)
        
        # Items marked for nothing (could share)
        idle_items = [i for i in my_items if not i["available_for"]]
        
        # Items available from others
        community_lending = self.get_available_items(availability="lending")
        community_selling = self.get_available_items(availability="selling")
        
        return {
            "your_idle_items": len(idle_items),
            "could_share": idle_items[:5],  # Top 5 suggestions
            "community_lending": len(community_lending),
            "community_selling": len(community_selling),
            "suggestion": "Consider marking some idle items as available for lending!"
        }
