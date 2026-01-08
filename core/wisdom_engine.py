"""
Wisdom Engine - Parses OSE SOPs to extract "Core Ideals" and "Wisdom Snippets".
"""

import os
import re
import random
from typing import List, Dict

class WisdomEngine:
    def __init__(self, sop_directory: str):
        self.sop_directory = sop_directory
        self.snippets = []
        self.ideals = []
        self.load_wisdom()

    def load_wisdom(self):
        """Scan SOPs and extract snippets marked with alerts or headers."""
        if not os.path.exists(self.sop_directory):
            print(f"⚠️ SOP directory not found: {self.sop_directory}")
            return

        for filename in os.listdir(self.sop_directory):
            if filename.endswith(".md"):
                path = os.path.join(self.sop_directory, filename)
                with open(path, 'r') as f:
                    content = f.read()
                    self.parse_markdown(content, filename)

    def parse_markdown(self, content: str, source: str):
        """Extract [!IMPORTANT], [!NOTE], and key headers."""
        # Extract GitHub-style alerts
        alerts = re.findall(r'> \[!(IMPORTANT|TIP|NOTE|WARNING|CAUTION)\]\s+> (.*?)\n', content, re.DOTALL)
        for alert_type, text in alerts:
            self.snippets.append({
                "type": alert_type,
                "text": text.strip().replace("\n> ", " "),
                "source": source
            })

        # Extract "Core Tenets" or "Ideals" sections
        tenets = re.search(r'## (Core Tenets|Core Ideals|The Logic of Life)(.*?)(##|\Z)', content, re.DOTALL)
        if tenets:
            tenet_text = tenets.group(2).strip()
            # Split by bullet points
            items = re.findall(r'[-\*]\s+(.*?)\n', tenet_text)
            for item in items:
                self.ideals.append({
                    "text": item.strip(),
                    "source": source
                })

    def get_random_wisdom(self) -> Dict:
        """Returns a random snippet or ideal for UI display."""
        pool = self.snippets + self.ideals
        if not pool:
            return {"text": "Build the future today.", "source": "Internal"}
        return random.choice(pool)

    def get_skill_tree(self) -> str:
        """Generates a Mermaid graph representation of the learning path."""
        return """
graph TD
    A["Scarcity Awareness"] --> B["Techno-Sovereignty"]
    B --> C["The Ark (Food/Power)"]
    B --> D["The Ledger (Tokenomics)"]
    C --> E["Dunbar Node (150 People)"]
    D --> E
    E --> F["Type 1 Civilization"]
    style F fill:#00ff00,stroke:#000,stroke-width:4px
"""

if __name__ == "__main__":
    # Test
    engine = WisdomEngine("/Volumes/Extreme SSD/Antigrav/OSE/CHRONICLE/SOP")
    print(f"Loaded {len(engine.snippets)} snippets and {len(engine.ideals)} ideals.")
    print("Random Wisdom:", engine.get_random_wisdom())
