#!/usr/bin/env python3
"""
OSE Wiki Knowledge Scraper → Ollama RAG Pipeline
Scrapes the Open Source Ecology Wiki and formats for Ollama ingestion.

Usage:
    python3 ose_wiki_scraper.py --scrape    # Scrape wiki pages
    python3 ose_wiki_scraper.py --ingest    # Feed to Ollama
"""

import json
import urllib.request
import urllib.parse
import re
import os
from datetime import datetime

# GVCS 50 Machines - categorized
GVCS_MACHINES = {
    "Habitat": [
        "CEB_Press", "Cement_Mixer", "Sawmill", "Bulldozer", "Backhoe"
    ],
    "Agriculture": [
        "LifeTrac", "Seeder", "Hay_Rake", "Well-Drilling_Rig", "MicroTrac",
        "Soil_Pulverizer", "Spader", "Hay_Cutter", "Trencher", "Bakery_Oven",
        "Dairy_Milker", "Microcombine", "Baler"
    ],
    "Industry": [
        "Multimachine", "Ironworker", "Laser_Cutter", "Welder", "Plasma_Cutter",
        "CNC_Torch_Table", "Metal_Roller", "Rod_and_Wire_Mill", "Press_Forge",
        "Universal_Rotor", "3D_Printer", "3D_Scanner", "CNC_Circuit_Mill",
        "Industrial_Robot", "Chipper_Hammermill", "Drill_Press", "Induction_Furnace"
    ],
    "Energy": [
        "Power_Cube", "Gasifier_Burner", "Solar_Concentrator", "Electric_Motor_Generator",
        "Hydraulic_Motor", "Steam_Engine", "Heat_Exchanger", "Wind_Turbine",
        "Pelletizer", "Universal_Power_Supply", "Nickel-Iron_Battery"
    ],
    "Materials": [
        "Aluminum_Extractor", "Bioplastic_Extruder"
    ],
    "Transportation": [
        "Open_Source_Car", "Open_Source_Truck"
    ]
}

# Additional key OSE concepts
OSE_CONCEPTS = [
    "Global_Village_Construction_Set",
    "Civilization_Starter_Kit",
    "Open_Source_Hardware",
    "Distributive_Enterprise",
    "Factor_e_Farm",
    "Open_Building_Institute",
    "Seed_Eco-Home"
]

WIKI_BASE_URL = "https://wiki.opensourceecology.org/wiki/"
OUTPUT_DIR = "knowledge_base"

def fetch_wiki_page(page_name):
    """Fetch a wiki page and extract clean text."""
    url = WIKI_BASE_URL + urllib.parse.quote(page_name)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            # Extract main content (between mw-parser-output divs)
            content_match = re.search(r'<div class="mw-parser-output">(.*?)</div>\s*<div', html, re.DOTALL)
            if content_match:
                content = content_match.group(1)
            else:
                content = html
            
            # Remove HTML tags
            text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Decode HTML entities
            text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            text = text.replace('&quot;', '"').replace('&#39;', "'")
            
            return {
                "title": page_name.replace("_", " "),
                "url": url,
                "content": text[:5000],  # Limit to 5000 chars per page
                "scraped_at": datetime.now().isoformat()
            }
    except Exception as e:
        print(f"  ⚠️ Failed to fetch {page_name}: {e}")
        return None

def scrape_all():
    """Scrape all GVCS machines and OSE concepts."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_knowledge = []
    
    # Scrape machines by category
    for category, machines in GVCS_MACHINES.items():
        print(f"\n📦 Scraping {category} machines...")
        for machine in machines:
            print(f"  → {machine}")
            data = fetch_wiki_page(machine)
            if data:
                data["category"] = category
                data["type"] = "machine"
                all_knowledge.append(data)
    
    # Scrape concepts
    print(f"\n📚 Scraping OSE concepts...")
    for concept in OSE_CONCEPTS:
        print(f"  → {concept}")
        data = fetch_wiki_page(concept)
        if data:
            data["category"] = "Core Concepts"
            data["type"] = "concept"
            all_knowledge.append(data)
    
    # Save to JSON
    output_file = os.path.join(OUTPUT_DIR, "ose_knowledge.json")
    with open(output_file, 'w') as f:
        json.dump(all_knowledge, f, indent=2)
    
    print(f"\n✅ Scraped {len(all_knowledge)} pages → {output_file}")
    return all_knowledge

def format_for_ollama(knowledge_data):
    """Format knowledge for Ollama fine-tuning (JSONL format)."""
    output_file = os.path.join(OUTPUT_DIR, "ose_ollama_training.jsonl")
    
    with open(output_file, 'w') as f:
        for item in knowledge_data:
            # Create Q&A style training examples
            entry = {
                "prompt": f"What is the {item['title']} in Open Source Ecology?",
                "response": f"The {item['title']} is part of the OSE {item.get('category', 'project')}. {item['content'][:1000]}"
            }
            f.write(json.dumps(entry) + "\n")
            
            # Add category-based prompt
            entry2 = {
                "prompt": f"Describe how {item['title']} fits into the Global Village Construction Set.",
                "response": f"{item['title']} is classified under {item.get('category', 'GVCS')} in the 50-machine set. {item['content'][:800]}"
            }
            f.write(json.dumps(entry2) + "\n")
    
    print(f"✅ Formatted {len(knowledge_data) * 2} training examples → {output_file}")
    return output_file

def ingest_to_ollama(training_file):
    """Send knowledge to Ollama for context."""
    # For RAG approach - create embeddings
    print("\n🤖 Preparing Ollama context...")
    
    # Create a system prompt with OSE context
    context_file = os.path.join(OUTPUT_DIR, "ose_system_context.txt")
    
    with open(os.path.join(OUTPUT_DIR, "ose_knowledge.json"), 'r') as f:
        knowledge = json.load(f)
    
    context_parts = [
        "# Open Source Ecology Knowledge Base",
        "You are an expert on the Open Source Ecology project and the Global Village Construction Set (GVCS).",
        "The GVCS consists of 50 industrial machines needed to build a small, sustainable civilization.",
        "",
        "## Key Machines by Category:",
    ]
    
    for category, machines in GVCS_MACHINES.items():
        context_parts.append(f"\n### {category}")
        context_parts.append(", ".join([m.replace("_", " ") for m in machines]))
    
    context_parts.append("\n## Detailed Knowledge:")
    for item in knowledge[:20]:  # Top 20 items for context window
        context_parts.append(f"\n**{item['title']}** ({item.get('category', 'General')})")
        context_parts.append(item['content'][:500])
    
    context = "\n".join(context_parts)
    
    with open(context_file, 'w') as f:
        f.write(context)
    
    print(f"✅ Created system context → {context_file}")
    print(f"\n💡 To use with Ollama:")
    print(f"   ollama run llama3.2 --system \"{context_file}\"")
    print(f"   OR add to Modelfile for permanent context")
    
    return context_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 ose_wiki_scraper.py [--scrape|--ingest|--all]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "--scrape":
        scrape_all()
    elif action == "--ingest":
        ingest_to_ollama(os.path.join(OUTPUT_DIR, "ose_ollama_training.jsonl"))
    elif action == "--all":
        knowledge = scrape_all()
        training_file = format_for_ollama(knowledge)
        ingest_to_ollama(training_file)
    else:
        print(f"Unknown action: {action}")
