#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def setup():
    print("🚀 ARK OS - Initialize Environment")
    print("==================================")
    
    base_dir = Path(__file__).resolve().parent
    env_file = base_dir / ".env"
    env_local = base_dir / ".env.local"
    env_template = base_dir / ".env.template"

    # 1. Create .env from template if not exists
    if not env_local.exists():
        if env_template.exists():
            print(f"📝 Creating .env.local from template...")
            with open(env_template, 'r') as f:
                content = f.read()
            
            # Auto-populate some defaults
            content = content.replace("ARK_API_URL=http://localhost:3001", "ARK_API_URL=http://localhost:3000")
            
            with open(env_local, 'w') as f:
                f.write(content)
            print("✅ .env.local created.")
        else:
            print("⚠️  .env.template not found. Creating basic .env.local...")
            with open(env_local, 'w') as f:
                f.write("PORT=3000\nHOST=0.0.0.0\nARK_API_URL=http://localhost:3000\n")
            print("✅ Minimal .env.local created.")

    # 2. Ensure directories exist
    dirs = ["ledger", "logs", "storage", "storage/inbox"]
    for d in dirs:
        p = base_dir / d
        if not p.exists():
            print(f"📁 Creating directory: {d}")
            p.mkdir(parents=True, exist_ok=True)

    # 3. Check for Python deps
    print("📦 Checking dependencies...")
    try:
        import requests
        print("✅ Dependencies look good.")
    except ImportError:
        print("⚠️  Missing dependencies. Run: pip install -r requirements.txt")

    print("\n🎯 Setup complete. You can now run ./ark_start.sh")

if __name__ == "__main__":
    setup()
