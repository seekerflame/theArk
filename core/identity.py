import json
import os
import time
import base64
import hmac
import hashlib
import logging

logger = logging.getLogger("ArkOS.Identity")

class IdentityManager:
    def __init__(self, users_file, jwt_secret):
        self.users_file = users_file
        self.jwt_secret = jwt_secret
        self.users = {}
        self.load()

    def load(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f: self.users = json.load(f)
            except: pass
        else:
            self.users = {"admin": {"password": "admin", "role": "ADMIN", "created_at": time.time()}}
            self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        with open(self.users_file, 'w') as f: json.dump(self.users, f, indent=2)

    def register(self, username, password):
        if username in self.users: return False, "User exists"
        self.users[username] = {
            "password": password, 
            "role": "WORKER", 
            "roles": ["WORKER"],
            "certifications": {}, 
            "created_at": time.time()
        }
        self.save()
        return True, "Welcome to the Ark"


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
        signature = hmac.new(self.jwt_secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(signature).decode().replace('=', '')
        return f"{header}.{payload}.{sig_b64}"

    def verify_token(self, token):
        try:
            parts = token.split('.')
            if len(parts) != 3: return None
            header, payload, sig = parts
            expected_sig = base64.urlsafe_b64encode(hmac.new(self.jwt_secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()).decode().replace('=', '')
            if sig != expected_sig: return None
            data = json.loads(base64.urlsafe_b64decode(payload + '=='))
            if data['exp'] < time.time(): return None
            return data
        except: return None

    @staticmethod
    def get_role_multipliers():
        return {
            "WORKER": 1.0,
            "BUILDER": 1.0,
            "WELDER": 1.5,      # Safety pay / Skill bonus
            "ORACLE": 1.2,      # Trust bonus
            "FARMER": 1.1,      # Nutrient sovereignty
            "ARCHITECT": 1.3,   # Master design
            "CODE_MINT": 1.0    # Base for code (handled elsewhere)
        }

