import json
import subprocess
import time

def register_steward_routes(router, ledger, energy, requires_auth):
    
    @router.post('/api/steward/think')
    def h_steward_think(h, p):
        prompt = p.get('prompt', 'System status audit. Propose next technical upgrade.')
        context = p.get('context', {})
        
        full_prompt = f"System Status: {json.dumps(context)}\n\nGoal: Propose a technical upgrade for the Ark OS. Format as JSON with 'title' and 'description'.\n\nPrompt: {prompt}"
        
        # Energy: AI thinking spike
        energy.get_current_power(is_thinking=True)
        
        try:
            ollama_data = {
                "model": "deepseek-r1:1.5b",
                "prompt": full_prompt,
                "stream": False,
                "format": "json"
            }
            
            cmd = ["curl", "-s", "-X", "POST", "http://localhost:11434/api/generate", 
                   "-d", json.dumps(ollama_data)]
            res = subprocess.check_output(cmd)
            ollama_res = json.loads(res)
            
            response_text = ollama_res.get('response', '{}').strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            if "{" in response_text and "}" in response_text and not (response_text.startswith("{") and response_text.endswith("}")):
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                response_text = response_text[start:end]
                
            try:
                proposal = json.loads(response_text)
            except:
                proposal = {"title": "Raw Proposal", "description": response_text}
            
            h.send_json({
                "status": "success",
                "proposal": proposal,
                "raw": response_text
            })
        except Exception as e:
            h.send_json_error(f"Steward Brain Error: {str(e)}")

    @router.post('/api/mission/propose')
    def h_mission_propose(h, p):
        title = p.get('title')
        desc = p.get('description', p.get('desc'))
        if not title: return h.send_json_error("Mission title required")
        
        data = {
            "mission_id": f"mission_{int(time.time())}",
            "title": title,
            "description": desc,
            "proposer": "Steward_AI",
            "timestamp": time.time(),
            "status": "PROPOSED"
        }
        block_hash = ledger.add_block('MISSION', data)
        h.send_json({"status": "success", "mission_id": data['mission_id'], "hash": block_hash})

    @router.get('/api/mission/list')
    def h_mission_list(h):
        h.send_json([b['data'] for b in ledger.blocks if b['type'] == 'MISSION'])

    @router.post('/api/steward/chat')
    def h_steward_chat(h, p):
        msg = p.get('message', '')
        h.send_json({"output": f"[STEWARD] Intelligence received. Analyzing: '{msg[:20]}...'. Directive: Continue Evolution Cycle."})
