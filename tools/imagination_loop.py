"""
Perpetual Imagination Loop - Demo Script
Connects Ollama (Local Right Brain) to Ark OS Evolution API
"""

import requests
import json
import time

ARK_API_URL = "http://localhost:3000/api/evolution/propose"
OLLAMA_URL = "http://localhost:11434/api/generate"

def get_ollama_idea(prompt):
    """Ask local Ollama for an OSE evolution idea."""
    payload = {
        "model": "llama3",
        "prompt": f"You are the Gaia Architect. Imagine one specific technischen or economic upgrade for the OSE Ark OS. Output ONLY JSON with: title, description, type (technical/economic/social), impact (1-10), estimated_labor (AT), and logic_proof. Context: {prompt}",
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code == 200:
            return json.loads(response.json()['response'])
    except Exception as e:
        print(f"⚠️ Ollama error: {e}")
        return None

def submit_to_ark(proposal):
    """Post the idea to the Ark Evolution API."""
    payload = {
        "source": "ollama_local",
        **proposal
    }
    
    try:
        response = requests.post(ARK_API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"✅ Proposal submitted: {proposal['title']}")
            print(f"   ID: {response.json().get('proposal_id')}")
        else:
            print(f"❌ API error: {response.text}")
    except Exception as e:
        print(f"⚠️ Ark API error: {e}. (Is the server running?)")

if __name__ == "__main__":
    print("🚀 Starting Imagination Loop...")
    
    # 1. Imagine
    idea = get_ollama_idea("We need better food sovereignty mechanics.")
    
    if idea:
        print(f"💡 Ollama imagined: {idea['title']}")
        # 2. Execute (Submit for review)
        submit_to_ark(idea)
    else:
        print("❌ Could not get idea from Ollama.")
