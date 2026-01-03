import json
import os
import glob

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return []

py_data = load_json('village_ledger_py.json')
rust_data = load_json('village_ledger.json')

with open('LEDGER_EXPORT.md', 'w') as f:
    f.write('# 📒 Full Ledger Export\n\n')
    f.write(f'Generated on: {os.popen("date").read().strip()}\n\n')

    f.write('## 🐍 Active Python Ledger (Live)\n')
    f.write(f'*Source: village_ledger_py.json*\n')
    f.write(f'*Total Blocks: {len(py_data)}*\n\n')
    f.write('```json\n')
    json.dump(py_data, f, indent=2)
    f.write('\n```\n\n')
    
    f.write('## 🦀 Legacy Rust Ledger\n')
    f.write(f'*Source: village_ledger.json*\n')
    f.write(f'*Total Blocks: {len(rust_data)}*\n\n')
    f.write('```json\n')
    json.dump(rust_data, f, indent=2)
    f.write('\n```\n\n')

    # Backups & Other Stores
    backups = sorted(glob.glob("village_ledger_backup_*.json"), reverse=True)
    other_ledgers = [
        "source_code/ledger/abundance-dag/village_ledger.json"
    ]
    
    # Filter existing
    archives = []
    for f_path in backups + other_ledgers:
        if os.path.exists(f_path):
            archives.append(f_path)
            
    f.write(f'## 📦 Archives ({len(archives)} Files)\n\n')
    
    for archive in archives:
        data = load_json(archive)
        f.write(f'### 📄 {archive}\n')
        f.write(f'*Blocks: {len(data)}*\n')
        f.write('```json\n')
        json.dump(data, f, indent=2)
        f.write('\n```\n\n')

print(f"Exported to {os.path.abspath('LEDGER_EXPORT.md')}")
