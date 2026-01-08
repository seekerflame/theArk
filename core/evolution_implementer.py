"""
The Execution Loop (Left Brain Node)
Takes approved evolution proposals and implements them.
"""

import requests
import json
import subprocess
import os
import time

API_BASE = "http://localhost:3000/api/evolution"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def get_approved_proposals():
    try:
        res = requests.get(f"{API_BASE}/proposals?status=approved")
        return res.json().get("proposals", [])
    except:
        return []

def generate_code_patch(proposal):
    prompt = f"""
    You are the 'Left Brain' of Ark OS. 
    Implement the following approved evolution proposal:
    
    TITLE: {proposal['title']}
    DESCRIPTION: {proposal['description']}
    TYPE: {proposal['type']}
    LOGIC: {proposal['logic_proof']}
    
    Provide the implementation as a Python script or a diff.
    Output ONLY the code block.
    """
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        res = requests.post(OLLAMA_URL, json=payload)
        return res.json().get("response", "")
    except:
        return None

def apply_and_verify(patch, proposal_id):
    # In a real environment, we'd use a sandboxed execution or git apply
    # For now, we save it as a 'candidate' for review or auto-apply if safe
    if not patch: return False
    
    filename = f"evolution/candidates/{proposal_id}.patch"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "w") as f:
        f.write(patch)
        
    print(f"✅ Patch saved to {filename}")
    
    # Run tests
    test_res = subprocess.run(["pytest", "tests/"], capture_output=True)
    if test_res.returncode == 0:
        print("✅ Tests passed.")
        return True
    else:
        print("❌ Tests failed.")
        return False

def push_to_git(proposal_id):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Evolution: Implemented {proposal_id}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Pushed to GitHub.")
        return True
    except:
        print("❌ Git push failed.")
        return False

def run_once():
    print("🧠 Left Brain Waking Up...")
    proposals = get_approved_proposals()
    
    if not proposals:
        print("💤 No approved proposals found.")
        return
        
    for p in proposals:
        print(f"🛠️ Implementing: {p['title']}...")
        patch = generate_code_patch(p)
        if patch:
            if apply_and_verify(patch, p['id']):
                # push_to_git(p['id']) # Disabled by default for safety, can be enabled via flag
                
                # Mark as executed in API
                requests.post(f"{API_BASE}/review", json={
                    "proposal_id": p['id'],
                    "decision": "executed",
                    "note": "Autonomous implementation successful."
                })
        else:
            print("❌ Failed to generate patch.")

if __name__ == "__main__":
    run_once()
