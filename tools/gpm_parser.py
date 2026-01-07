#!/usr/bin/env python3
import os
import re
import datetime

SOP_PATH = "../docs/SOP/GPM_001.md"
MERMAID_OUTPUT_PATH = "../mermaid-diagram-20260107.md"

def parse_sop(file_path):
    """
    Parses the SOP markdown file to extract labeled steps or lists.
    We look for numbered lists in the 'Execution Logic' section or generic sections.
    """
    tasks = []
    with open(file_path, 'r') as f:
        lines = f.readlines()

    capture = False
    for line in lines:
        if "Execution Logic" in line or "Algorithm" in line:
            capture = True
        elif line.startswith("##") and capture:
            capture = False # Stop if new section starts
        
        if capture:
            # Match "1. **Title**: Description" or "1. Title"
            match = re.match(r"^\d+\.\s+\*\*?(.*?)\*\*?[:\.]\s*(.*)", line.strip())
            if match:
                title = match.group(1).strip()
                desc = match.group(2).strip()
                tasks.append({"title": title, "desc": desc})
    
    return tasks

def generate_mermaid(tasks):
    """
    Generates a Mermaid graph from the extracted tasks.
    """
    mermaid = ["\n# Global Problemsolving Method Flow\n", "```mermaid", "graph TD"]
    
    previous_node = None
    
    for i, task in enumerate(tasks):
        node_id = f"GPM{i+1}"
        node_label = f"{task['title']}"
        # Escape quotes
        node_label = node_label.replace('"', "'")
        
        mermaid.append(f'    {node_id}["{node_label}"]')
        
        if previous_node:
            mermaid.append(f"    {previous_node} --> {node_id}")
        
        previous_node = node_id

    mermaid.append("```\n")
    
    # Add Nodes Explained table
    mermaid.append("## Nodes Explained (GPM)\n")
    mermaid.append("| Node | Description |")
    mermaid.append("|------|-------------|")
    for task in tasks:
         mermaid.append(f"| **{task['title']}** | {task['desc']} |")
         
    return "\n".join(mermaid)

def main():
    # Resolve absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sop_abs_path = os.path.join(script_dir, SOP_PATH)
    output_abs_path = os.path.join(script_dir, MERMAID_OUTPUT_PATH)

    if not os.path.exists(sop_abs_path):
        print(f"Error: SOP file not found at {sop_abs_path}")
        return

    print("Parsing SOP...")
    tasks = parse_sop(sop_abs_path)
    
    if not tasks:
        # Fallback if parsing fails (hardcoded based on user input for reliability)
        print("Parsing returned no results, using fallback defaults from GPM.")
        tasks = [
            {"title": "Analysis", "desc": "Identify best players and standards."},
            {"title": "Wiki Literacy", "desc": "Investigative journalism."},
            {"title": "System Integration", "desc": "Open-source missing links."},
            {"title": "Team Building", "desc": "Stewardship and Advisor contracts."},
            {"title": "Cross-Subsidize", "desc": "Earned revenue + scale charity."},
            {"title": "Scale OSE", "desc": "Launch Open Sector Enterprise."},
            {"title": "Execute", "desc": "Solutions for democracy/justice."}
        ]

    print(f"Found {len(tasks)} tasks.")
    
    mermaid_content = generate_mermaid(tasks)
    
    # Append or Write
    # We will create a new file or append to the existing daily file. 
    # Since the file name is new (20260107), we create it.
    
    with open(output_abs_path, 'w') as f:
        f.write(mermaid_content)
        
    print(f"Generated Mermaid diagram at {output_abs_path}")

if __name__ == "__main__":
    main()
