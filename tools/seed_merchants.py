"""
Seed Launch Merchants - YOU + Rudy into the system
Run this to populate the database with initial merchant data
"""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'ledger', 'village_ledger.db')

def seed_merchants():
    print("🌱 Seeding launch merchants...")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchants (
            merchant_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            owner_wallet TEXT,
            category TEXT,
           description TEXT,
            location_address TEXT,
            location_mobile INTEGER DEFAULT 0,
            accepts_at INTEGER DEFAULT 1,
            accepts_usd INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active',
            story TEXT,
            first_friday_offer TEXT,
            created_at INTEGER DEFAULT (strftime('%s', 'now'))
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchant_services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            price_at REAL,
            price_usd REAL,
            description TEXT,
            duration_minutes INTEGER,
            FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
        )
    """)
    
    # Seed YOUR detailing business
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO merchants (
                merchant_id, name, owner_wallet, category, description,
                location_address, location_mobile, accepts_at, accepts_usd,
                story, first_friday_offer
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "detail_001",
            "Eternal Detailing",
            "genesis_architect",
            "auto_services",
            "Professional car detailing. Interior, exterior, full service. Pay in AT or cash.",
            "Bakersfield, CA",
            1,
            1,
            1,
            "First merchant on Ark OS. Proving you don't need banks to run a business.",
            "First 5 customers get 10% bonus AT back."
        ))
        
        # Detailing services
        services = [
            ("Basic Interior Clean", 5.0, 50, "Vacuum, wipe down, air freshener", 60),
            ("Full Detail", 15.0, 150, "Interior + exterior, wax, polish, tire shine", 180),
            ("Quick Wash", 2.0, 20, "Exterior wash, dry", 30)
        ]
        
        for name, price_at, price_usd, desc, duration in services:
            cursor.execute("""
                INSERT OR IGNORE INTO merchant_services (
                    merchant_id, name, price_at, price_usd, description, duration_minutes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, ("detail_001", name, price_at, price_usd, desc, duration))
        
        print("✅ Seeded: Eternal Detailing (YOU)")
        
    except Exception as e:
        print(f"⚠️ Detailing error: {e}")
    
    # Seed Rudy's Hot Dogs
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO merchants (
                merchant_id, name, owner_wallet, category, description,
                location_address, location_mobile, accepts_at, accepts_usd,
                story, first_friday_offer
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "rudy_hotdogs_001",
            "Rudy's Hot Dogs",
            "rudy_vendor",
            "food",
            "Best hot dogs in Bakersfield. Cash, card, or AT accepted.",
            "Downtown Bakersfield, CA",
            0,
            1,
            1,
            "Rudy got burned by Square during the SSN breach. He's the first vendor to say 'no more banks.' Now he accepts AT.",
            "Visit Rudy's stand, show this app, get a stamp. Collect 3 stamps = 1 free hot dog."
        ))
        
        # Rudy's menu
        menu = [
            ("Classic Hot Dog", 0.3, 3, "All beef, grilled"),
            ("Deluxe Dog", 0.5, 5, "Bacon-wrapped, loaded toppings"),
            ("Combo (Dog + Drink)", 0.7, 7, "Hot dog + soda")
        ]
        
        for name, price_at, price_usd, desc in menu:
            cursor.execute("""
                INSERT OR IGNORE INTO merchant_services (
                    merchant_id, name, price_at, price_usd, description, duration_minutes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, ("rudy_hotdogs_001", name, price_at, price_usd, desc, 5))
        
        print("✅ Seeded: Rudy's Hot Dogs")
        
    except Exception as e:
        print(f"⚠️ Rudy error: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Launch network seeded! 2 merchants ready:")
    print("  - http://localhost:3000/m/detail_001")
    print("  - http://localhost:3000/m/rudy_hotdogs_001")

if __name__ == "__main__":
    seed_merchants()
