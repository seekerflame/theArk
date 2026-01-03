import os
import sys
import argparse

OVERCLOCK_FILE = "overclock.flag"

def toggle_overclock(state):
    if state:
        with open(OVERCLOCK_FILE, 'w') as f:
            f.write("ENABLED")
        print("⚡ [ANTIGRAVITY] OVERCLOCK MODE: ENGAGED")
        print("   > Power Limit: UNLOCKED (250W+)")
        print("   > Stability:   CRITICAL")
        print("   > Cooling:     MAXIMUM")
    else:
        if os.path.exists(OVERCLOCK_FILE):
            os.remove(OVERCLOCK_FILE)
        print("🟢 [ANTIGRAVITY] System Stabilized. Returning to nominal baseline.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Overclock Controller")
    parser.add_argument("action", choices=["on", "off", "status"], help="Set overclock state")

    args = parser.parse_args()

    if args.action == "on":
        toggle_overclock(True)
    elif args.action == "off":
        toggle_overclock(False)
    elif args.action == "status":
        if os.path.exists(OVERCLOCK_FILE):
            print("⚡ OVERCLOCK: ACTIVE")
        else:
            print("🟢 OVERCLOCK: INACTIVE")
