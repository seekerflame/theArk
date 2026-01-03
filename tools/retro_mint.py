import json
import urllib.request
import time

# Heuristic: Each Wiki Link in a daily log is 1 Standard Task Unit (1 ST) unless specified.
# Rate: 10 AT/hr
BASE_RATE = 10 

API_URL = "http://localhost:3000/api/mint"

# Sample Data from Marcin's Log (Parsed from Wiki)
# Format: (Date, Task Title, URL)
LOG_ENTRIES = [
    ("Wed Nov 19, 2025", "5 Gallon Fuel Container", "https://wiki.opensourceecology.org/wiki/5_Gallon_Fuel_Conainer"),
    ("Wed Nov 19, 2025", "SEH FAQ", "https://wiki.opensourceecology.org/wiki/SEH_FAQ"),
    ("Wed Nov 19, 2025", "BCC", "https://wiki.opensourceecology.org/wiki/BCC"),
    ("Tue Dec 18, 2025", "Irresistible Offer", "https://wiki.opensourceecology.org/wiki/Irresistible_Offer"),
    ("Tue Dec 18, 2025", "Cut List Macro", "https://wiki.opensourceecology.org/wiki/Cut_List_Macro_in_FreeCAD"),
    ("Sun Dec 16, 2025", "Cost Reduction Collab", "https://wiki.opensourceecology.org/wiki/Cost_Reduction_Collaboration"),
    ("Wed Dec 11, 2025", "Heat Pump Sourcing", "https://wiki.opensourceecology.org/wiki/Heat_Pump_Sourcing"),
    ("Wed Dec 11, 2025", "Inverter Sourcing", "https://wiki.opensourceecology.org/wiki/Inverter_Sourcing"),
    ("Fri Dec 7, 2025", "Hangar Design", "https://wiki.opensourceecology.org/wiki/Hangar"),
    ("Fri Dec 7, 2025", "Truss Design", "https://wiki.opensourceecology.org/wiki/Truss_Design"),
    ("Thu Dec 6, 2025", "Wall Module Test", "https://wiki.opensourceecology.org/wiki/Wall_Module_Test"),
    ("Tue Dec 4, 2025", "Rapid Learning Pedagogy", "https://wiki.opensourceecology.org/wiki/OSE_Rapid_Learning_Pedagogy"),
    ("Mon Dec 3, 2025", "SH6 Finishing", "https://wiki.opensourceecology.org/wiki/SH6_Finishing")
]

def mint_entry(date, title, url):
    st = 1.0 # 1 hour standard time per major wiki log item
    reward = st * BASE_RATE
    
    payload = {
        "task": f"[RETRO] {title}",
        "hours": 1.0, 
        "standard_time": st,
        "efficiency": "100%",
        "complexity": 1.0,
        "proof": url,
        "reward": reward,
        "minter": "Marcin Jakubowski",
        "description": f"Retroactive minting for work logged on {date}"
    }
    
    req = urllib.request.Request(API_URL, 
                                 data=json.dumps(payload).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            print(f"Minted: {title} ({date}) -> {reward} AT | Hash: {res.get('hash', 'N/A')[:8]}...")
    except Exception as e:
        print(f"Failed to mint {title}: {e}")

def main():
    print(f"Starting Retroactive Minting for {len(LOG_ENTRIES)} entries...")
    total_minted = 0
    
    for date, title, url in LOG_ENTRIES:
        mint_entry(date, title, url)
        total_minted += 10 # 10 AT per task
        time.sleep(0.1) # Be nice to the server
        
    print(f"\nCompleted! Total Minted: {total_minted} AT for Marcin Jakubowski.")

if __name__ == "__main__":
    main()
