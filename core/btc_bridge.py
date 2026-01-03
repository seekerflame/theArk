#!/usr/bin/env python3
"""
BTC Bridge - Phase 12: Economic Circularity
Enables AT <-> BTC exchange for external trade.

This is a STUB for future integration with:
- Bitcoin node (bitcoind RPC)
- Lightning Network (LND/CLN)
- Exchange rate oracle

Current Implementation: Simulation Mode
"""

import time
import json
import hashlib

class BTCBridge:
    def __init__(self):
        self.exchange_rate = 0.00001  # 1 AT = 0.00001 BTC (simulation)
        self.last_rate_update = time.time()
        self.pending_swaps = []
        
    def get_exchange_rate(self):
        """Get current AT/BTC exchange rate."""
        # In production: fetch from oracle or exchange API
        return {
            "rate": self.exchange_rate,
            "pair": "AT/BTC",
            "updated_at": self.last_rate_update,
            "source": "SIMULATION"
        }
    
    def calculate_btc_value(self, at_amount):
        """Calculate BTC equivalent for AT amount."""
        return {
            "at_amount": at_amount,
            "btc_amount": at_amount * self.exchange_rate,
            "rate": self.exchange_rate,
            "sats": int(at_amount * self.exchange_rate * 100_000_000)
        }
    
    def calculate_at_value(self, btc_amount):
        """Calculate AT equivalent for BTC amount."""
        return {
            "btc_amount": btc_amount,
            "at_amount": btc_amount / self.exchange_rate,
            "rate": self.exchange_rate
        }
    
    def request_swap(self, direction, amount, user_wallet):
        """Request a swap between AT and BTC."""
        swap_id = hashlib.sha256(f"{time.time()}{user_wallet}{amount}".encode()).hexdigest()[:16]
        
        swap = {
            "swap_id": swap_id,
            "direction": direction,  # "AT_TO_BTC" or "BTC_TO_AT"
            "amount": amount,
            "user_wallet": user_wallet,
            "status": "PENDING",
            "created_at": time.time(),
            "rate_locked": self.exchange_rate
        }
        
        if direction == "AT_TO_BTC":
            swap["btc_amount"] = amount * self.exchange_rate
            swap["at_amount"] = amount
        else:
            swap["at_amount"] = amount / self.exchange_rate
            swap["btc_amount"] = amount
        
        self.pending_swaps.append(swap)
        
        return {
            "status": "swap_queued",
            "swap_id": swap_id,
            "details": swap,
            "message": "Swap queued for processing. In production, this would interact with Lightning Network."
        }
    
    def get_status(self):
        """Get bridge status."""
        return {
            "status": "SIMULATION",
            "exchange_rate": self.exchange_rate,
            "pending_swaps": len(self.pending_swaps),
            "features": {
                "lightning": False,
                "onchain": False,
                "atomic_swaps": False
            },
            "message": "BTC Bridge is in simulation mode. Connect to Lightning for production."
        }


# Global instance
bridge = BTCBridge()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "status":
            print(json.dumps(bridge.get_status(), indent=2))
        
        elif cmd == "rate":
            print(json.dumps(bridge.get_exchange_rate(), indent=2))
        
        elif cmd == "calc":
            if len(sys.argv) > 2:
                at_amount = float(sys.argv[2])
                print(json.dumps(bridge.calculate_btc_value(at_amount), indent=2))
            else:
                print("Usage: btc_bridge.py calc <at_amount>")
        
        elif cmd == "swap":
            if len(sys.argv) > 4:
                direction = sys.argv[2]  # AT_TO_BTC or BTC_TO_AT
                amount = float(sys.argv[3])
                wallet = sys.argv[4]
                print(json.dumps(bridge.request_swap(direction, amount, wallet), indent=2))
            else:
                print("Usage: btc_bridge.py swap <direction> <amount> <wallet>")
        
        else:
            print("Usage: btc_bridge.py [status|rate|calc|swap]")
    else:
        print(json.dumps(bridge.get_status(), indent=2))
