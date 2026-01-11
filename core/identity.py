import json
import os
import time
import base64
import hmac
import hashlib
import logging

logger = logging.getLogger("ArkOS.Identity")

class IdentityManager:
    def __init__(self, users_file, jwt_key):
        self.users_file = users_file
        self.jwt_key = jwt_key
        self.users = {}
        self.load()

    def load(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f: self.users = json.load(f)
            except: pass
        else:
            # Default admin creation (replaces hardcoded password with env lookup)
            from core.config import Config
            admin_pwd = Config.get('ARK_ADMIN_PWD', 'ark_admin_default')
            self.users = {"admin": {"password": admin_pwd, "role": "ADMIN", "created_at": time.time()}}
            self.save()

    def save(self):
        user_dir = os.path.dirname(self.users_file)
        if user_dir:
            os.makedirs(user_dir, exist_ok=True)
        with open(self.users_file, 'w') as f: json.dump(self.users, f, indent=2)

    def generate_mnemonic(self):
        """Simulates BIP39 mnemonic generation for sovereign identity."""
        words = ["ark", "seed", "node", "labor", "mint", "value", "gaia", "tribe", "build", "grid", "power", "earth", "flow", "truth", "life", "open", "source", "core", "spirit", "hand", "mind", "soul", "bond", "path"]
        import random
        selected = random.sample(words, 12)
        return " ".join(selected)

    def register(self, username, password):
        if username in self.users: return False, "User exists"
        
        mnemonic = self.generate_mnemonic()
        
        self.users[username] = {
            "password": password, 
            "mnemonic": mnemonic,
            "role": "WORKER", 
            "roles": ["WORKER"],
            "certifications": {}, 
            "verified_hours": 0.0,
            "safety_grade": 100.0,
            "created_at": time.time()
        }

        self.save()
        return True, {"mnemonic": mnemonic, "message": "Welcome to the Ark"}

    def restore(self, username, mnemonic, new_password):
        """Restores identity from mnemonic."""
        for u, data in self.users.items():
            if u == username and data.get('mnemonic') == mnemonic:
                data['password'] = new_password
                self.save()
                return True, "Identity restored. Password updated."
        return False, "Invalid mnemonic or username"


    def login(self, username, password):
        user = self.users.get(username)
        if user and user['password'] == password: return True, user
        return False, "Invalid credentials"

    def generate_token(self, username):
        header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().replace('=', '')
        payload = base64.urlsafe_b64encode(json.dumps({
            "sub": username, 
            "role": self.users.get(username, {}).get('role', 'WORKER'),
            "exp": time.time() + 86400
        }).encode()).decode().replace('=', '')
        signature = hmac.new(self.jwt_key.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(signature).decode().replace('=', '')
        return f"{header}.{payload}.{sig_b64}"

    def verify_token(self, token):
        try:
            parts = token.split('.')
            if len(parts) != 3: return None
            header, payload, sig = parts
            expected_sig = base64.urlsafe_b64encode(hmac.new(self.jwt_key.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()).decode().replace('=', '')
            if sig != expected_sig: return None
            data = json.loads(base64.urlsafe_b64decode(payload + '=='))
            if data['exp'] < time.time(): return None
            return data
        except: return None

    def get_role_multipliers(self, ledger=None):
        """Returns role multipliers from roles.py definitions + dynamic ledger overrides."""
        try:
            from core.roles import ROLE_DEFINITIONS
            base = {role: info['base_multiplier'] for role, info in ROLE_DEFINITIONS.items()}
        except ImportError:
            # Fallback to legacy hardcoded values
            base = {
                "WORKER": 1.0,
                "BUILDER": 1.5,
                "FARMER": 1.8,
                "ENERGY_TECH": 2.0,
                "DEVELOPER": 2.5,
                "ORACLE": 1.8,
                "HEARTH_KEEPER": 1.6,
                "CHRONICLER": 1.4,
                "EDUCATOR": 1.7,
                "HARDWARE_ENGINEER": 2.2,
                "AI_STEWARD": 2.3,
                "FEDERATION_COORDINATOR": 1.9,
                "ECONOMIST": 2.0,
                "WELDER": 1.5,
                "ARCHITECT": 1.3,
                "CODE_MINT": 1.0
            }
        
        # Allow ledger to override multipliers dynamically
        if ledger:
            for block in ledger.blocks:
                if block['type'] == 'ROLE_DEFINITION':
                    d = block['data']
                    base[d['role'].upper()] = d.get('multiplier', 1.0)
        return base
    
    def get_user_roles(self, username, ledger=None, hw_bridge=None):
        """Get all certified roles for a user from ledger + local host detection."""
        roles = set()
        
        # 1. Local Host Detection (Infrastructure Support)
        if hw_bridge and hw_bridge.is_active():
            # If the current local admin is the user, they are a host
            # For multi-user clusters, we check if the user is the primary operator
            if username == 'admin' or self.users.get(username, {}).get('is_primary_operator'):
                roles.add('NODE_HOST')
        
        # 2. Check in-memory user data
        user = self.users.get(username, {})
        if 'roles' in user:
            roles.update(user.get('roles', []))
        
        # 3. Check ledger for ROLE_CERTIFICATION blocks
        if ledger:
            for block in ledger.blocks:
                if block['type'] == 'ROLE_CERTIFICATION':
                    if block['data'].get('username') == username:
                        roles.add(block['data'].get('role'))
        
        # Default to WORKER if no roles found
        if not roles:
            roles.add('WORKER')
        
        return list(roles)

    def get_holistic_multiplier(self, username, role="WORKER", ledger=None):
        """Calculates HM = RoleMod * TierMod * HostMod * SafetyGrade * SurvivalNet"""
        if role is None: role = "WORKER"
        user = self.users.get(username, {})
        if not user: return 1.0
        
        # 1. Role Multiplier (Dynamic)
        multipliers = self.get_role_multipliers(ledger)
        role_mod = multipliers.get(role.upper(), 1.0)

        # 2. Tier Multiplier (Frictionless Success Path)
        hours = user.get('verified_hours', 0.0)
        tier_mod = 1.0
        if hours >= 500: tier_mod = 1.5   # Master
        elif hours >= 100: tier_mod = 1.2 # Journeyman
        
        # 3. Host Multiplier (Infrastructure Support - "Reward more if you contribute more")
        host_mod = 1.0
        if "NODE_HOST" in user.get('roles', []):
            host_mod = 2.0 # Infrastructure providers get double rewards
        
        # 4. Safety Multiplier (Justice Penalty)
        safety_grade = user.get('safety_grade', 100.0)
        safety_mod = max(0.1, safety_grade / 100.0)
        
        # 5. Survival Minimum (Safety Net / UBI Logic)
        # If balance is low, multiplier increases to ensure survival.
        survival_net = 1.0
        if ledger:
            balance = ledger.get_balance(username)
            if balance < 100: # Below "Comfort Threshold"
                survival_net = 1.0 + ((100 - balance) / 100) # Max 2.0x catch-up
        
        return round(role_mod * tier_mod * host_mod * safety_mod * survival_net, 2)

    def add_verified_hours(self, username, hours):
        """Updates user hours and triggers tier logic."""
        if username not in self.users: return
        self.users[username]['verified_hours'] = self.users[username].get('verified_hours', 0.0) + hours
        self.save()

    def update_pseudoname(self, username, pseudoname):
        """Sets or updates a user's pseudoname handle."""
        if username not in self.users: return False, "User not found"
        
        # Check if pseudoname is taken by another user
        for u, data in self.users.items():
            if u != username and data.get('pseudoname') == pseudoname:
                return False, "Pseudoname already taken"
        
        self.users[username]['pseudoname'] = pseudoname
        self.save()
        return True, "Pseudoname updated"

    def resolve_handle(self, handle):
        """Resolves a handle (e.g. @alice) to a username."""
        clean_handle = handle.lstrip('@')
        
        # 1. Direct username check
        if clean_handle in self.users:
            return clean_handle
        
        # 2. Pseudoname check
        for u, data in self.users.items():
            if data.get('pseudoname') == clean_handle:
                return u
        
        return None


