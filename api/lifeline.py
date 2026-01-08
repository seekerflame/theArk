"""
Lifeline API - Stress Reduction and Daily Living Management
Handles Memories, Life Ops, and Future Self favors.
"""

import time
import json
import os
import logging

LIFELINE_FILE = os.path.join('ledger', 'lifeline_data.json')
logger = logging.getLogger("ArkOS.Lifeline")

def load_lifeline_data():
    if os.path.exists(LIFELINE_FILE):
        try:
            with open(LIFELINE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load lifeline data: {e}")
            return {}
    return {}

def save_lifeline_data(data):
    try:
        os.makedirs(os.path.dirname(LIFELINE_FILE), exist_ok=True)
        with open(LIFELINE_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save lifeline data: {e}")

def register_lifeline_routes(router, ledger, auth_decorator):
    
    @router.get('/api/lifeline/data')
    @auth_decorator
    def h_get_lifeline_data(h, user, p):
        data = load_lifeline_data()
        user_data = data.get(user['sub'], {
            "memories": [],
            "ops": {
                "cleaning": [],
                "bills": [],
                "meals": []
            },
            "favors": [],
            "zen_cycles": 0
        })
        h.send_json(user_data)

    @router.post('/api/lifeline/memories/add')
    @auth_decorator
    def h_add_memory(h, user, p):
        content = p.get('content')
        if not content: return h.send_json_error("Memory content required")
        
        data = load_lifeline_data()
        user_id = user['sub']
        if user_id not in data: 
            data[user_id] = {"memories": [], "ops": {"cleaning":[], "bills":[], "meals":[]}, "favors": [], "zen_cycles": 0}
        
        memory = {
            "id": f"mem_{int(time.time())}",
            "content": content,
            "timestamp": time.time()
        }
        data[user_id].setdefault("memories", []).append(memory)
        save_lifeline_data(data)
        h.send_json({"status": "added", "memory": memory})

    @router.post('/api/lifeline/ops/add')
    @auth_decorator
    def h_add_op(h, user, p):
        op_type = p.get('type') # cleaning, bills, meals
        content = p.get('content')
        if not op_type or not content: return h.send_json_error("Type and content required")
        
        data = load_lifeline_data()
        user_id = user['sub']
        if user_id not in data: 
            data[user_id] = {"memories": [], "ops": {"cleaning":[], "bills":[], "meals":[]}, "favors": [], "zen_cycles": 0}
        
        op_list = data[user_id]["ops"].get(op_type, [])
        new_op = {
            "id": f"op_{int(time.time())}",
            "content": content,
            "status": "pending",
            "timestamp": time.time()
        }
        op_list.append(new_op)
        data[user_id]["ops"][op_type] = op_list
        save_lifeline_data(data)
        h.send_json({"status": "added", "op": new_op})

    @router.post('/api/lifeline/ops/toggle')
    @auth_decorator
    def h_toggle_op(h, user, p):
        op_id = p.get('id')
        op_type = p.get('type')
        if not op_id or not op_type: return h.send_json_error("ID and type required")
        
        data = load_lifeline_data()
        user_id = user['sub']
        if user_id in data and op_type in data[user_id]["ops"]:
            for op in data[user_id]["ops"][op_type]:
                if op["id"] == op_id:
                    op["status"] = "done" if op["status"] == "pending" else "pending"
                    save_lifeline_data(data)
                    return h.send_json({"status": "toggled", "new_status": op["status"]})
        
        h.send_json_error("Op not found")

    @router.post('/api/lifeline/favors/add')
    @auth_decorator
    def h_add_favor(h, user, p):
        content = p.get('content')
        if not content: return h.send_json_error("Favor content required")
        
        data = load_lifeline_data()
        user_id = user['sub']
        if user_id not in data: 
            data[user_id] = {"memories": [], "ops": {"cleaning":[], "bills":[], "meals":[]}, "favors": [], "zen_cycles": 0}
        
        favor = {
            "id": f"favor_{int(time.time())}",
            "content": content,
            "status": "pending",
            "timestamp": time.time()
        }
        data[user_id].setdefault("favors", []).append(favor)
        save_lifeline_data(data)
        h.send_json({"status": "added", "favor": favor})

    @router.post('/api/lifeline/zen/complete')
    @auth_decorator
    def h_complete_zen(h, user, p):
        data = load_lifeline_data()
        user_id = user['sub']
        if user_id not in data: 
            data[user_id] = {"memories": [], "ops": {"cleaning":[], "bills":[], "meals":[]}, "favors": [], "zen_cycles": 0}
        
        data[user_id]["zen_cycles"] = data[user_id].get("zen_cycles", 0) + 1
        
        # Reward small XP for stress relief focus
        from core.identity import IdentityManager
        # Logic to add XP would go here, but we'll keep it simple for now
        
        save_lifeline_data(data)
        h.send_json({"status": "completed", "total_cycles": data[user_id]["zen_cycles"]})
