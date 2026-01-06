"""
Genesis Airdrop Script - FBCC7 Participants + First Friday Users
Creates initial AT distribution to bootstrap the economy
"""

import time
import json
import os

# FBCC7 Participants (Past Future Builders Crash Course attendees)
# Add real usernames/wallet IDs as they register
FBCC7_PARTICIPANTS = [
    # {"name": "participant_name", "wallet": "wallet_id", "amount": 10}
    # To be populated with actual FBCC7 participant data
]

# First Friday Early Adopters
FIRST_FRIDAY_POOL = {
    "total_genesis_at": 500,  # Total AT to distribute
    "per_user_airdrop": 5,    # 5 AT per early user
    "max_users": 100          # First 100 users
}

def run_genesis_airdrop(ledger, participants, reason="FBCC7_GENESIS"):
    """
    Distribute genesis AT to participants.
    
    This is a one-time bootstrap - creates AT from nothing
    to kickstart the economy. After this, all AT must be earned.
    """
    results = []
    
    for p in participants:
        name = p.get("name", "unknown")
        wallet = p.get("wallet", name)
        amount = p.get("amount", 10)
        
        # Genesis mint - no labor required (bootstrap only)
        block_hash = ledger.add_block('GENESIS_AIRDROP', {
            "recipient": wallet,
            "amount": amount,
            "reason": reason,
            "cohort": "FBCC7",
            "timestamp": time.time(),
            "note": "Bootstrap AT for early community builders"
        })
        
        results.append({
            "name": name,
            "wallet": wallet,
            "amount": amount,
            "block_hash": block_hash
        })
        
        print(f"✅ Airdropped {amount} AT to {name}")
    
    return results

def create_first_friday_vouchers(count=100, amount_each=5):
    """
    Generate voucher codes for First Friday distribution.
    Users scan QR code or enter code to claim their AT.
    """
    import hashlib
    import secrets
    
    vouchers = []
    for i in range(count):
        code = secrets.token_urlsafe(8)  # Short, URL-safe code
        voucher = {
            "code": code,
            "amount": amount_each,
            "status": "available",  # available, claimed, expired
            "created_at": time.time(),
            "claimed_by": None,
            "claimed_at": None
        }
        vouchers.append(voucher)
    
    # Save to file
    voucher_file = "ledger/genesis_vouchers.json"
    with open(voucher_file, "w") as f:
        json.dump(vouchers, f, indent=2)
    
    print(f"✅ Created {count} vouchers worth {count * amount_each} AT total")
    print(f"   Saved to: {voucher_file}")
    
    return vouchers

def claim_voucher(ledger, code, user_wallet):
    """
    User claims a voucher code.
    """
    voucher_file = "ledger/genesis_vouchers.json"
    
    if not os.path.exists(voucher_file):
        return False, "No vouchers available"
    
    with open(voucher_file, "r") as f:
        vouchers = json.load(f)
    
    for v in vouchers:
        if v["code"] == code:
            if v["status"] != "available":
                return False, f"Voucher already {v['status']}"
            
            # Claim it
            v["status"] = "claimed"
            v["claimed_by"] = user_wallet
            v["claimed_at"] = time.time()
            
            # Save updated vouchers
            with open(voucher_file, "w") as f:
                json.dump(vouchers, f, indent=2)
            
            # Mint AT to user
            ledger.add_block('VOUCHER_CLAIM', {
                "recipient": user_wallet,
                "amount": v["amount"],
                "voucher_code": code[:4] + "****",  # Partial for privacy
                "timestamp": time.time()
            })
            
            return True, f"Claimed {v['amount']} AT!"
    
    return False, "Invalid voucher code"

def print_voucher_qr_codes(vouchers, output_dir="tools/voucher_qrcodes"):
    """
    Generate QR codes for each voucher (for printing on flyers).
    Uses qrcode library if available, otherwise prints text.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        import qrcode
        for i, v in enumerate(vouchers[:20]):  # First 20 for testing
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(f"arkat://claim/{v['code']}")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(f"{output_dir}/voucher_{i+1}.png")
        print(f"✅ QR codes saved to {output_dir}/")
    except ImportError:
        print("⚠️  qrcode library not installed. Run: pip install qrcode[pil]")
        print("   Voucher codes (text):")
        for i, v in enumerate(vouchers[:10]):
            print(f"   {i+1}. {v['code']} - {v['amount']} AT")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python genesis_airdrop.py create_vouchers [count] [amount_each]")
        print("  python genesis_airdrop.py list_vouchers")
        print("  python genesis_airdrop.py print_qr")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create_vouchers":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        amount = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        create_first_friday_vouchers(count, amount)
    
    elif command == "list_vouchers":
        if os.path.exists("ledger/genesis_vouchers.json"):
            with open("ledger/genesis_vouchers.json", "r") as f:
                vouchers = json.load(f)
            available = sum(1 for v in vouchers if v["status"] == "available")
            claimed = sum(1 for v in vouchers if v["status"] == "claimed")
            print(f"📊 Voucher Status: {available} available, {claimed} claimed")
        else:
            print("No vouchers created yet")
    
    elif command == "print_qr":
        if os.path.exists("ledger/genesis_vouchers.json"):
            with open("ledger/genesis_vouchers.json", "r") as f:
                vouchers = json.load(f)
            print_voucher_qr_codes(vouchers)
        else:
            print("Create vouchers first")
    
    else:
        print(f"Unknown command: {command}")
