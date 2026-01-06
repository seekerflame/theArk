"""
Harvest Marketplace - Sell surplus produce, seeds, plants
Stop wasting food from unplucked trees!
"""

import time
from typing import Dict, List, Tuple, Optional

class HarvestMarketplace:
    """
    Local marketplace for garden produce, seeds, plants.
    Zero platform fees. Full provenance tracking.
    """
    
    CATEGORIES = ["vegetables", "fruits", "herbs", "seeds", "plants", "eggs", "honey", "other"]
    
    def __init__(self, ledger, inventory_system):
        self.ledger = ledger
        self.inventory = inventory_system
        self.listings = {}  # listing_id -> listing data
        
    def post_listing(self, seller: str, item_data: Dict) -> Tuple[bool, str]:
        """
        Post produce for sale.
        
        item_data:
            title: str
            description: str
            category: str
            quantity: str (e.g., "5 lbs", "1 dozen")
            price_at: float
            location: optional {lat, lon, description}
            pickup_instructions: str
            photo_url: optional str
            grown_by: str (if different from seller, e.g., child)
            organic: bool
            seed_source: optional str (provenance)
        """
        required = ["title", "category", "quantity", "price_at"]
        for field in required:
            if field not in item_data:
                return False, f"Missing: {field}"
        
        if item_data["category"] not in self.CATEGORIES:
            return False, f"Invalid category. Use: {self.CATEGORIES}"
        
        listing_id = f"harvest_{int(time.time())}_{seller[:4]}"
        
        listing = {
            "id": listing_id,
            "seller": seller,
            "title": item_data["title"],
            "description": item_data.get("description", ""),
            "category": item_data["category"],
            "quantity": item_data["quantity"],
            "price_at": item_data["price_at"],
            "location": item_data.get("location"),
            "pickup_instructions": item_data.get("pickup_instructions", "Contact seller"),
            "photo_url": item_data.get("photo_url"),
            "grown_by": item_data.get("grown_by", seller),
            "organic": item_data.get("organic", False),
            "seed_source": item_data.get("seed_source"),
            "status": "available",  # available, reserved, sold
            "created_at": time.time(),
            "provenance": [{
                "action": "listed",
                "by": seller,
                "at": time.time()
            }]
        }
        
        self.listings[listing_id] = listing
        
        # Log to ledger
        self.ledger.add_block('HARVEST_LISTED', {
            "listing_id": listing_id,
            "seller": seller,
            "title": listing["title"],
            "price_at": listing["price_at"],
            "timestamp": time.time()
        })
        
        return True, listing_id
    
    def buy_listing(self, listing_id: str, buyer: str) -> Tuple[bool, str]:
        """Purchase a listing."""
        if listing_id not in self.listings:
            return False, "Listing not found"
        
        listing = self.listings[listing_id]
        
        if listing["status"] != "available":
            return False, f"Listing is {listing['status']}"
        
        if listing["seller"] == buyer:
            return False, "Can't buy your own listing"
        
        # Check buyer balance
        buyer_balance = self.ledger.get_balance(buyer)
        if buyer_balance < listing["price_at"]:
            return False, f"Insufficient AT. Need {listing['price_at']}, have {buyer_balance}"
        
        # Transfer AT
        self.ledger.add_block('TRANSFER', {
            "from": buyer,
            "to": listing["seller"],
            "amount": listing["price_at"],
            "reason": f"Harvest purchase: {listing['title']}",
            "listing_id": listing_id,
            "timestamp": time.time()
        })
        
        # If grown_by is different (child), split payment
        if listing["grown_by"] != listing["seller"]:
            grower_share = listing["price_at"] * 0.7  # 70% to grower
            self.ledger.add_block('GROWER_SHARE', {
                "from": listing["seller"],
                "to": listing["grown_by"],
                "amount": grower_share,
                "reason": f"Grower share for: {listing['title']}",
                "timestamp": time.time()
            })
        
        # Update provenance
        listing["provenance"].append({
            "action": "sold",
            "to": buyer,
            "price": listing["price_at"],
            "at": time.time()
        })
        
        listing["status"] = "sold"
        listing["sold_to"] = buyer
        listing["sold_at"] = time.time()
        
        # Log to ledger
        self.ledger.add_block('HARVEST_SOLD', {
            "listing_id": listing_id,
            "seller": listing["seller"],
            "buyer": buyer,
            "grower": listing["grown_by"],
            "price_at": listing["price_at"],
            "timestamp": time.time()
        })
        
        return True, f"Purchase complete! Contact seller for pickup."
    
    def get_available(self, category: str = None, 
                      location: Dict = None, radius_km: float = 10) -> List[Dict]:
        """Get available listings, optionally filtered."""
        result = []
        for listing in self.listings.values():
            if listing["status"] != "available":
                continue
            if category and listing["category"] != category:
                continue
            # TODO: Add location filtering with Haversine
            result.append(listing)
        
        # Sort by freshest first
        result.sort(key=lambda x: x["created_at"], reverse=True)
        return result
    
    def get_my_listings(self, user: str) -> List[Dict]:
        """Get listings by user (as seller or grower)."""
        return [l for l in self.listings.values() 
                if l["seller"] == user or l["grown_by"] == user]
    
    def cancel_listing(self, listing_id: str, user: str) -> Tuple[bool, str]:
        """Cancel an available listing."""
        if listing_id not in self.listings:
            return False, "Listing not found"
        
        listing = self.listings[listing_id]
        
        if listing["seller"] != user:
            return False, "Only seller can cancel"
        
        if listing["status"] != "available":
            return False, "Can only cancel available listings"
        
        listing["status"] = "cancelled"
        listing["cancelled_at"] = time.time()
        
        return True, "Listing cancelled"
    
    def get_provenance(self, listing_id: str) -> Optional[List[Dict]]:
        """Get full history of a listing."""
        if listing_id not in self.listings:
            return None
        return self.listings[listing_id]["provenance"]


# Pre-built templates for common produce
HARVEST_TEMPLATES = {
    "lemons": {
        "title": "Fresh Lemons",
        "description": "Organic backyard lemons, never sprayed",
        "category": "fruits",
        "quantity": "5 lbs",
        "price_at": 0.5,
        "organic": True
    },
    "tomatoes": {
        "title": "Heirloom Tomatoes",
        "description": "Variety of heirloom tomatoes from the garden",
        "category": "vegetables",
        "quantity": "2 lbs",
        "price_at": 0.3,
        "organic": True
    },
    "eggs": {
        "title": "Fresh Eggs",
        "description": "Free-range backyard chickens",
        "category": "eggs",
        "quantity": "1 dozen",
        "price_at": 0.5
    },
    "herbs": {
        "title": "Fresh Herb Bundle",
        "description": "Basil, rosemary, thyme - freshly cut",
        "category": "herbs",
        "quantity": "mixed bundle",
        "price_at": 0.2
    },
    "seeds": {
        "title": "Saved Seeds",
        "description": "Open-pollinated seeds from this season",
        "category": "seeds",
        "quantity": "packet",
        "price_at": 0.1
    }
}
