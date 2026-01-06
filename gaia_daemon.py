#!/usr/bin/env python3
"""
GAIA NEXUS DAEMON - Autonomous Background Worker
Runs continuously, executing improvement cycles every 6 hours.
Survives system restarts via launchd/cron.
"""
import os
import time
import sys
import logging
import json
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ai_orchestrator import GaiaNexus

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [DAEMON] %(message)s',
    handlers=[
        logging.FileHandler('gaia_daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DAEMON")

CYCLE_INTERVAL = 6 * 60 * 60  # 6 hours in seconds
QUICK_CYCLE = 60 * 60  # 1 hour for testing
HEARTBEAT_FILE = "daemon_heartbeat.json"

def write_heartbeat():
    """Write heartbeat file so user knows daemon is alive"""
    with open(HEARTBEAT_FILE, 'w') as f:
        json.dump({
            'last_heartbeat': datetime.now().isoformat(),
            'status': 'alive',
            'pid': os.getpid()
        }, f, indent=2)

def check_should_run():
    """Check if enough time has passed since last run"""
    if not os.path.exists(HEARTBEAT_FILE):
        return True
    
    try:
        with open(HEARTBEAT_FILE, 'r') as f:
            data = json.load(f)
            last = datetime.fromisoformat(data['last_heartbeat'])
            elapsed = (datetime.now() - last).total_seconds()
            return elapsed > QUICK_CYCLE  # Run every hour in daemon mode
    except:
        return True

def run_daemon():
    """Main daemon loop"""
    logger.info("=" * 60)
    logger.info("🌌 GAIA NEXUS DAEMON STARTING")
    logger.info(f"   PID: {os.getpid()}")
    logger.info(f"   Cycle Interval: {CYCLE_INTERVAL / 3600} hours")
    logger.info("=" * 60)
    
    # Get config from environment
    ARK_URL = os.environ.get('ARK_API_URL', 'http://localhost:3000')
    AI_TOKEN = os.environ.get('AI_AGENT_TOKEN', 'daemon_token')
    
    # Initialize GAIA NEXUS
    gaia = GaiaNexus(ARK_URL, AI_TOKEN)
    
    while True:
        try:
            write_heartbeat()
            
            if check_should_run():
                logger.info("🔄 Starting autonomous cycle...")
                gaia.run_autonomous_cycle()
                logger.info("✅ Cycle complete!")
            else:
                logger.info("⏳ Skipping cycle (ran recently)")
            
            # Sleep for interval
            logger.info(f"😴 Sleeping for {CYCLE_INTERVAL / 3600} hours...")
            time.sleep(CYCLE_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("🛑 Daemon stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Cycle error: {e}")
            # Sleep shorter on error, then retry
            time.sleep(300)  # 5 min

def main():
    """Entry point with daemonization option"""
    import argparse
    parser = argparse.ArgumentParser(description='GAIA NEXUS Daemon')
    parser.add_argument('--test', action='store_true', help='Run one cycle and exit')
    parser.add_argument('--status', action='store_true', help='Check daemon status')
    args = parser.parse_args()
    
    if args.status:
        if os.path.exists(HEARTBEAT_FILE):
            with open(HEARTBEAT_FILE, 'r') as f:
                data = json.load(f)
                print(f"Status: {data['status']}")
                print(f"Last Heartbeat: {data['last_heartbeat']}")
                print(f"PID: {data['pid']}")
        else:
            print("Daemon has never run or heartbeat missing")
        return
    
    if args.test:
        ARK_URL = os.environ.get('ARK_API_URL', 'http://localhost:3000')
        AI_TOKEN = os.environ.get('AI_AGENT_TOKEN', 'test_token')
        gaia = GaiaNexus(ARK_URL, AI_TOKEN)
        gaia.run_autonomous_cycle()
        return
    
    run_daemon()

if __name__ == '__main__':
    main()
