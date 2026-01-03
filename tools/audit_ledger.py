import json
import sys
import os

LEDGER_FILE = "THE_ARK_v0.7/village_ledger_py.json"

def audit_ledger():
    if not os.path.exists(LEDGER_FILE):
        return "NO LEDGER FOUND", []

    try:
        with open(LEDGER_FILE, 'r') as f:
            ledger = json.load(f)
    except Exception as e:
        return f"LEDGER CORRUPT: {e}", []

    # If ledger is a list (blocks), wrap it
    if isinstance(ledger, list):
        blocks = ledger
    else:
        blocks = ledger.get('nodes', [])

    suspicious = []
    
    for block in blocks:
        data = block.get('data', {})
        
        # Check 1: Verified but no Proof (for standard tasks)
        if data.get('verified') and not data.get('proof') and data.get('standard_time', 0) > 0:
             suspicious.append(f"Block {block.get('hash')[:8]} VERIFIED but NO PROOF")

        # Check 2: Impossibly High Efficiency (> 500%)
        eff_str = data.get('efficiency', '0%').replace('%', '')
        try:
            eff = float(eff_str)
            if eff > 500:
                suspicious.append(f"Block {block.get('hash')[:8]} SUSPICIOUS EFFICIENCY: {eff}%")
        except:
             pass

    status = "SECURE" if not suspicious else "FLAGGED"
    return status, suspicious

if __name__ == "__main__":
    status, flags = audit_ledger()
    print(status)
    if flags:
        print(" | ".join(flags))
