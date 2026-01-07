"""
The Imagination Loop (Right Brain Node)
Automates the cycle: Observe -> Ideate -> Propose -> Sleep
Incorporates "Sacred Math" for timing (Tesla 3-6-9 / Fibonacci).
"""

import time
import json
import subprocess
import requests
import random
import os

# Configuration
API_URL = "http://localhost:3000/api/evolution/propose"
MODEL = "llama3"  # or 'deepseek-coder' if available
SACRED_NUMBERS = [3, 6, 9]

class RightBrain:
    def __init__(self):
        self.cycle_count = 0
        
    def get_sacred_interval(self):
        """Returns a sleep time based on Tesla/Fibonacci."""
        # Cycle 1=3min, 2=6min, 3=9min, then loop
        base_minutes = SACRED_NUMBERS[self.cycle_count % 3]
        return base_minutes * 60

    def query_ollama(self, prompt):
        """Query local Ollama instance."""
        try:
            # We use subprocess to call 'ollama run'
            # In production, use the HTTP API (localhost:11434)
            cmd = ["ollama", "run", MODEL, prompt]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip()
        except FileNotFoundError:
            print("❌ Ollama not found. Is it installed?")
            return None

    def perceive_world(self):
        """Read context to ground the imagination."""
        # Read task.md to see what's missing
        try:
            with open("task.md", "r") as f:
                tasks = f.read()
            return f"Current Task List:\n{tasks[:1000]}..." # Truncate for prompt
        except:
            return "No task list found."

    def ideate(self, context):
        """Ask the model for a breakthrough."""
        prompt = f"""
        {context}
        
        You are the 'Right Brain' of Ark OS. 
        Your goal is "Human Flourishing" via Universal Harmony.
        
        Based on the tasks above, propose ONE "Queen Idea" (High Impact, Low Effort).
        Output JSON only:
        {{
            "title": "...",
            "description": "...",
            "type": "technical|social|economic",
            "impact": 1-10,
            "logic_proof": "Why this aligns with nature/math/harmony"
        }}
        """
        response = self.query_ollama(prompt)
        return self.parse_json(response)

    def parse_json(self, text):
        """Extract JSON from potential chatty output."""
        try:
            # Simple extraction strategy
            start = text.find('{')
            end = text.rfind('}') + 1
            if start == -1 or end == 0: return None
            return json.loads(text[start:end])
        except:
            return None

    def run_cycle(self):
        print(f"🌀 Cycle {self.cycle_count}: Waking up...")
        
        # 1. Perceive
        context = self.perceive_world()
        
        # 2. Ideate
        print("🤔 Dreaming...")
        idea = self.ideate(context)
        
        if idea:
            print(f"💡 Idea: {idea.get('title')}")
            
            # 3. Propose (Submit to Ark)
            try:
                # Add source
                payload = idea
                payload['source'] = 'right_brain_ollama'
                
                res = requests.post(API_URL, json=payload)
                if res.status_code == 200:
                    print("✅ Proposal recorded on Ledger.")
                else:
                    print(f"❌ API Error: {res.text}")
            except Exception as e:
                print(f"❌ Connection Error: {e}")
        else:
            print("❌ No valid idea generated.")

        # 4. Sleep (Sacred Timing)
        sleep_sec = self.get_sacred_interval()
        print(f"🌙 Sleeping for {sleep_sec/60} minutes (Tesla Pattern)...")
        time.sleep(sleep_sec)
        
        self.cycle_count += 1

if __name__ == "__main__":
    import sys
    brain = RightBrain()
    print("🧠 Right Brain Online. Integrating Mathematics of Flourishing.")
    
    if "--once" in sys.argv:
        brain.run_cycle()
        sys.exit(0)
        
    while True:
        brain.run_cycle()
