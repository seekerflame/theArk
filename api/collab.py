import json
import time
import threading

# In-memory store for the collaboration state
# Structure: { "source": string, "version": int, "last_update": float }
COLLAB_STATE = {
    "source": """graph TD
    subgraph "GVCS Modular Blueprint (Patent v2026)"
        PC[Power Cube: US 2,604,176A] --> QC[Quick Connect: US 2,510,486]
        QC --> LT[LifeTrac Chassis]
        QC --> MT[MicroTrac chassis]
        FD[Final Drive: US 2,987,129] --> LT
        FD --> MT
    end

    subgraph "Active Ark Quests"
        Q1[Refactor Power Cube Interface]
        Q2[Implement Modular Hydrolines]
        Q3[Verify Hub Motor Torque]
    end

    PC -.-> Q1
    QC -.-> Q2
    FD -.-> Q3""",
    "version": 1,
    "last_update": time.time()
}

state_lock = threading.Lock()

def register_collab_routes(router, ledger):
    
    @router.get('/api/collab/state')
    def h_get_state(h):
        """Returns the current state of the board, dynamically injected with quests."""
        with state_lock:
            # Injecting open quests dynamically
            open_quests = []
            for b in ledger.blocks:
                if b['type'] == 'QUEST':
                    # Simplified quest state check
                    qid = b['data'].get('quest_id')
                    status = 'OPEN'
                    for update in ledger.blocks:
                        if update['type'] == 'QUEST_UPDATE' and update['data'].get('quest_id') == qid:
                            status = update['data'].get('status', status)
                    
                    if status == 'OPEN':
                        open_quests.append(f"Q{len(open_quests)+1}[{b['data']['title'][:20]}...]")

            quest_mermaid = "\n    subgraph \"Active Ark Quests\"\n        " + "\n        ".join(open_quests) + "\n    end" if open_quests else ""
            
            # Rebuild source if it's the default one to include live quests
            if "GVCS Modular Blueprint" in COLLAB_STATE['source']:
                # Update the Quests subgraph part
                import re
                current_source = COLLAB_STATE['source']
                new_source = re.sub(r'subgraph "Active Ark Quests".*?end', quest_mermaid.strip(), current_source, flags=re.DOTALL)
                COLLAB_STATE['source'] = new_source

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
