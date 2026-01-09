import time
import json
import os
import logging

logger = logging.getLogger("ArkOS.Marketplace")

class MarketplaceItem:
    def __init__(self, item_id, owner, title, description, price_at, location=None, category="GOODS"):
        self.item_id = item_id
        self.owner = owner
        self.title = title
        self.description = description
        self.price_at = price_at
        self.location = location # {"lat": 0, "lng": 0, "address": ""}
        self.category = category # GOODS, SERVICES, LESSONS, RENTAL
        self.created_at = time.time()
        self.status = "AVAILABLE"

class UniversalMarketplace:
    """
    Searchable P2P Exchange for high-density nodes.
    Links 'Open Source Everything' to physical coordinates.
    """
    def __init__(self, ledger, storage_path="ledger/marketplace_state.json"):
        self.ledger = ledger
        self.storage_path = storage_path
        self.items = {}
        self._load_state()

    def list_item(self, owner, title, description, price_at, location=None, category="GOODS", is_surplus=False):
        item_id = f"ITEM-{int(time.time())}-{os.urandom(2).hex()}"
        if is_surplus:
            title = f"[SURPLUS] {title}"
            category = "SURPLUS"
        
        item = MarketplaceItem(item_id, owner, title, description, price_at, location, category)
        self.items[item_id] = item
        self._save_state()
        return {"status": "success", "item_id": item_id}

    def list_surplus(self, owner, title, description, price_at=0.1, location=None):
        """Special listing for leftovers (bread, materials) at near-zero cost."""
        return self.list_item(owner, title, description, price_at, location, is_surplus=True)

    def search(self, query=None, category=None, max_distance=None, current_loc=None):
        results = []
        for item in self.items.values():
            if item.status != "AVAILABLE": continue
            
            # Simple keyword search
            if query and query.lower() not in (item.title + item.description).lower():
                continue
            
            # Category filter
            if category and item.category != category:
                continue
            
            # Distance filter (Stubbed - would use haversine in prod)
            if max_distance and current_loc and item.location:
                 # Real distance logic goes here
                 pass
            
            results.append(vars(item))
        
        return results

    def purchase_item(self, buyer, item_id):
        if item_id not in self.items:
            return {"status": "error", "message": "Item not found"}
        
        item = self.items[item_id]
        if item.status != "AVAILABLE":
            return {"status": "error", "message": "Item no longer available"}
        
        # 1. Verify Funds
        balance = self.ledger.get_balance(buyer)
        if balance < item.price_at:
            return {"status": "error", "message": "Insufficient AT balance"}
        
        # 2. Multi-Sig / Atomic Swap (Simplified for MVP)
        self.ledger.add_transaction(sender=buyer, recipient=item.owner, amount=item.price_at, task=f"Marketplace Purchase: {item.title}")
        
        # 3. Mark sold
        item.status = "SOLD"
        self._save_state()
        
        return {"status": "success", "transaction": "ledger_updated"}

    def _save_state(self):
        try:
            state = {jid: vars(j) for jid, j in self.items.items()}
            with open(self.storage_path, 'w') as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save marketplace state: {e}")

    def _load_state(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    state = json.load(f)
                    for jid, j_data in state.items():
                        item = MarketplaceItem(
                            j_data['item_id'], j_data['owner'], j_data['title'], 
                            j_data['description'], j_data['price_at'], 
                            j_data.get('location'), j_data.get('category', "GOODS")
                        )
                        item.status = j_data['status']
                        item.created_at = j_data['created_at']
                        self.items[jid] = item
            except Exception as e:
                logger.error(f"Failed to load marketplace state: {e}")
