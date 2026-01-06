#!/usr/bin/env python3
"""
System Health Dashboard
Generates a real-time status report of The Ark
"""
import json
import sys
import os
from datetime import datetime

def load_ledger():
    """Load the main ledger"""
    ledger_paths = [
        'ledger/village_ledger.json',
        '../ledger/village_ledger.json',
        '../../ledger/village_ledger.json'
    ]
    for path in ledger_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    return []

def analyze_ledger(ledger):
    """Extract key metrics from ledger"""
    stats = {
        'total_blocks': len(ledger),
        'users': 0,
        'quests': 0,
        'labor_blocks': 0,
        'total_at_minted': 0,
        'code_contributions': 0,
        'hardware_events': 0,
        'latest_block': None
    }
    
    for block in ledger:
        block_type = block.get('type', '')
        
        if block_type == 'USER_REGISTRATION':
            stats['users'] += 1
        elif block_type == 'QUEST':
            stats['quests'] += 1
        elif block_type == 'LABOR':
            stats['labor_blocks'] += 1
            stats['total_at_minted'] += block.get('data', {}).get('reward', 0)
        elif block_type == 'CODE_CONTRIBUTION':
            stats['code_contributions'] += 1
        elif block_type == 'HARDWARE':
            stats['hardware_events'] += 1
    
    if ledger:
        stats['latest_block'] = ledger[-1]
    
    return stats

def check_services():
    """Check if critical services are running"""
    import subprocess
    
    services = {
        'ark': False,
        'n8n': False
    }
    
    try:
        # Check if The Ark is running
        result = subprocess.run(['curl', '-s', 'http://localhost:3000/api/health'],
                              capture_output=True, timeout=2)
        if result.returncode == 0:
            services['ark'] = True
    except:
        pass
    
    try:
        # Check if n8n is running
        result = subprocess.run(['curl', '-s', 'http://localhost:5678/healthz'],
                              capture_output=True, timeout=2)
        if result.returncode == 0:
            services['n8n'] = True
    except:
        pass
    
    return services

def print_dashboard(stats, services):
    """Print a pretty dashboard"""
    print("=" * 60)
    print("🌍 THE ARK - SYSTEM HEALTH DASHBOARD")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Services
    print("📡 SERVICES")
    print(f"  The Ark (localhost:3000): {'✅ RUNNING' if services['ark'] else '❌ STOPPED'}")
    print(f"  n8n (localhost:5678):      {'✅ RUNNING' if services['n8n'] else '❌ STOPPED'}")
    print()
    
    # Ledger Stats
    print("📊 LEDGER STATISTICS")
    print(f"  Total Blocks:        {stats['total_blocks']}")
    print(f"  Registered Users:    {stats['users']}")
    print(f"  Total Quests:        {stats['quests']}")
    print(f"  Labor Validations:   {stats['labor_blocks']}")
    print(f"  Total AT Minted:     {stats['total_at_minted']:.2f} AT")
    print(f"  Code Contributions:  {stats['code_contributions']}")
    print(f"  Hardware Events:     {stats['hardware_events']}")
    print()
    
    # Latest Activity
    if stats['latest_block']:
        latest = stats['latest_block']
        print("🔄 LATEST ACTIVITY")
        print(f"  Type: {latest.get('type', 'UNKNOWN')}")
        print(f"  Hash: {latest.get('hash', 'N/A')[:16]}...")
        print(f"  Timestamp: {latest.get('timestamp', 'N/A')}")
    print()
    
    # Health Status
    all_services_up = all(services.values())
    has_activity = stats['total_blocks'] > 0
    
    print("🏥 OVERALL HEALTH")
    if all_services_up and has_activity:
        print("  Status: ✅ HEALTHY")
    elif all_services_up:
        print("  Status: ⚠️  OPERATIONAL (No ledger activity)")
    else:
        print("  Status: ❌ DEGRADED (Services down)")
    
    print("=" * 60)

def main():
    try:
        ledger = load_ledger()
        stats = analyze_ledger(ledger)
        services = check_services()
        print_dashboard(stats, services)
        
        # Exit code based on health
        if all(services.values()):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()
