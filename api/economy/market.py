import time
import json
import os
import random

def register_market_routes(router, ledger, requires_auth):

    @router.get('/api/marketing/prompts')
    def h_marketing_prompts(h):
        """Get a random marketing prompt for Veo3 video generation."""
        try:
            # Note: Path adjustment might be needed depending on file location
            prompts_file = os.path.join(os.getcwd(), 'web', 'marketing_prompts.json')
            if not os.path.exists(prompts_file):
                 # Fallback/Retry logic or just relative path?
                 prompts_file = os.path.join(os.path.dirname(__file__), '..', '..', 'web', 'marketing_prompts.json')
            
            if os.path.exists(prompts_file):
                with open(prompts_file, 'r') as f:
                    data = json.load(f)
                prompts = data.get('prompts', [])
                if prompts:
                    selected = random.choice(prompts)
                    h.send_json(selected)
                else:
                    h.send_json_error("No prompts available")
            else:
                 h.send_json_error("Prompts file not found")
        except Exception as e:
            h.send_json_error(f"Error loading prompts: {str(e)}")

    @router.get('/api/store/list')
    def h_store_list(h):
        h.send_json([
            {"id": "ose_fbcc", "name": "FBCC Godzilla Ticket", "price": 2100, "icon": "🏎️", "desc": "2-for-1 Immersive Truck Build (Includes Food & Onsite Living)"},
            {"id": "ose_consult", "name": "AI/Lead Architect Consult", "price": 100, "icon": "🧠", "desc": "1 Hour technical strategy session"},
            {"id": "ose_cad", "name": "Ironworker CAD (Full)", "price": 50, "icon": "🛠️", "desc": "Complete technical design files"},
            {"id": "ose_seh", "name": "Seed Eco-Home Blueprints", "price": 150, "icon": "🏡", "desc": "Modular structural designs"},
            {"id": "ose_sticker", "name": "Civ-OS Sticker", "price": 10, "icon": "🏷️", "desc": "Proclaim your sovereignty"}
        ])

    @router.post('/api/store/buy')
    def h_purchase(h, p):
        u = h.get_auth_user()
        if not u: return h.send_json_error("Auth Required", status=401)
        sender = u['sub']
        item_id = p.get('item_id')
        prices = {
            "ose_fbcc": 2100,
            "ose_consult": 100,
            "ose_cad": 50,
            "ose_seh": 150,
            "ose_sticker": 10
        }
        price = prices.get(item_id)
        if not price: return h.send_json_error("Item not found")
        if ledger.get_balance(sender) < price: return h.send_json_error("Insufficient AT")
        
        h_res = ledger.add_block('PURCHASE', {'buyer': sender, 'item': item_id, 'amount': price, 'timestamp': time.time()})
        h.send_json({"hash": h_res, "status": "success"})
