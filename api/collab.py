import json
import time
import threading

# In-memory store for the collaboration state
# Structure: { "source": string, "version": int, "last_update": float }
COLLAB_STATE = {
    "source": "graph TD\n    A[Start] --> B[Collaborate]\n    B --> C[Profit]",
    "version": 0,
    "last_update": time.time()
}

state_lock = threading.Lock()

def register_collab_routes(router):
    
    @router.get('/api/collab/state')
    def h_get_state(h):
        """Returns the current state of the board."""
        with state_lock:
            h.send_json(COLLAB_STATE)

    @router.post('/api/collab/update')
    def h_update_state(h, payload):
        """
        Updates the mermaid source.
        Expected payload: { "action": "update_source", "source": "..." }
        """
        action = payload.get('action')
        source = payload.get('source')
        
        if not action or source is None:
            return h.send_json_error("Invalid payload")

        with state_lock:
            if action == 'update_source':
                COLLAB_STATE['source'] = source
                COLLAB_STATE['version'] += 1
                COLLAB_STATE['last_update'] = time.time()
            
            h.send_json({"status": "success", "new_version": COLLAB_STATE['version']})
