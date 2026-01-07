import http.server
import socketserver
import json
import os
import time
import logging
import threading

# Core Modules
from core.config import Config
from core.ledger import VillageLedger
from core.identity import IdentityManager
from core.sensors import SensorRegistry
from core.federation import PeerManager, FederationSyncer
from core.steward import StewardNexus
from core.energy import EnergyMonitor
from core.router import Router, requires_auth, admin_only
from core.justice import JusticeSteward
from core.triple_verification import TripleVerification
from core.quest_system import QuestSystem
from core.inventory import InventorySystem
from core.fiat_bridge import FiatBridge, register_fiat_routes
from core.party_quests import PartyQuestSystem
from core.harvest_marketplace import HarvestMarketplace
from core.governance import GovernanceEngine


# API Modules
from api.system import register_system_routes
from api.steward import register_steward_routes
from api.economy import register_economy_routes
from api.social import register_social_routes
from api.hardware import register_hardware_routes
from api.exchange import register_exchange_routes
from api.quests import register_quest_routes
from api.treasury import register_treasury_routes
from api.justice import register_justice_routes
from api.roles import register_role_routes
from api.moderation import register_moderation_routes


# Bot Modules
from core.treasury_bot import TreasuryBot

# Configuration
PORT = int(Config.get('PORT', 3000))
JWT_SECRET = Config.get_jwt_secret()
DB_FILE = os.path.join(os.getcwd(), 'ledger', 'village_ledger.db')
WEB_DIR = os.path.join(os.getcwd(), 'web')
USERS_FILE = os.path.join('core', 'users.json')

# Security Warning
if JWT_SECRET == 'dev_only_secret_change_in_production':
    logging.warning("⚠️  Using default JWT_SECRET - set JWT_SECRET env var for production!")

# Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
logger = logging.getLogger("ArkOS")

# Instances
ledger = VillageLedger(DB_FILE)
identity = IdentityManager(USERS_FILE, JWT_SECRET)
sensors = SensorRegistry(os.path.join('hardware', 'sensor_registry.json'))
peers = PeerManager(os.path.join('federation', 'federation_registry.json'), PORT)
syncer = FederationSyncer(ledger, peers, PORT)
energy = EnergyMonitor(ledger, sensors=sensors)
steward = StewardNexus(ledger, sensors, server_file='server.py')
treasury = TreasuryBot(ledger)
justice = JusticeSteward(ledger, identity)
verification = TripleVerification(ledger, identity)
quest_system = QuestSystem(ledger, identity)
inventory = InventorySystem(ledger, identity)
fiat_bridge = FiatBridge(ledger)
party_quests = PartyQuestSystem(ledger, identity, quest_system)
harvest = HarvestMarketplace(ledger, inventory)


# Routing
router = Router()
auth_decorator = requires_auth(identity)

register_system_routes(router, ledger, identity, peers, sensors, energy, auth_decorator)
register_steward_routes(router, ledger, energy, auth_decorator)
register_economy_routes(router, ledger, sensors, identity, justice, auth_decorator, quest_system, verification)


register_social_routes(router, ledger, auth_decorator)
register_hardware_routes(router, sensors, auth_decorator)
register_exchange_routes(router, ledger, auth_decorator)
register_justice_routes(router, ledger, justice, auth_decorator)

register_quest_routes(router, ledger, identity, auth_decorator)
register_treasury_routes(router, treasury, auth_decorator)
register_role_routes(router, ledger, identity, auth_decorator)
register_fiat_routes(router, ledger, fiat_bridge, auth_decorator)
logger.info("💰 Fiat Bridge loaded (Card ↔ BTC ↔ AT ↔ Bank)")
logger.info("📦 Inventory System loaded")
logger.info("👨‍👩‍👧 Party Quests loaded (families + groups)")
logger.info("🥬 Harvest Marketplace loaded (sell produce)")

# Party & Harvest API
try:
    from api.party import register_party_routes
    from api.evolution import EvolutionEngine, register_evolution_routes
    
    # Instance
    evolution = EvolutionEngine(ledger, identity)
    
    register_party_routes(router, party_quests, harvest, auth_decorator)
    register_evolution_routes(router, evolution, auth_decorator)
    
    logger.info("🎉 Party & Harvest API endpoints registered")
    logger.info("🧬 Evolution Engine loaded (Perpetual Loop active)")
    
    # Governance & Moderation
    from core.governance import GovernanceEngine
    from api.moderation import register_moderation_routes
    
    governance = GovernanceEngine(ledger, identity)
    register_moderation_routes(router, governance, identity, auth_decorator)
    logger.info("⚖️ Governance Engine & Moderation API active")
except ImportError as e:
    logger.warning(f"⚠️  API modules missing: {e}")

# Merchant Discovery API
try:
    from api.merchants import register_merchant_routes
    register_merchant_routes(router, ledger, auth_decorator)
    logger.info("🏪 Merchant Discovery API loaded")
except ImportError as e:
    logger.warning(f"⚠️  Merchant API missing: {e}")

# AI Memory System Integration
try:
    from core.ai_memory import create_ai_memory_api
    create_ai_memory_api(router, ledger, auth_decorator)
    logger.info("🧠 AI Memory System loaded")
except ImportError:
    logger.warning("⚠️  AI Memory System not available")

# Collaborative Canvas
try:
    from api.collab import register_collab_routes
    register_collab_routes(router)
    logger.info("🎨 Collaborative Canvas loaded")
except ImportError as e:
    logger.warning(f"⚠️  Collab API missing: {e}")

# Rate Limiting (simple in-memory, resets on restart)
rate_limit_store = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 30  # requests per window for auth endpoints

def check_rate_limit(ip, endpoint):
    """Returns True if request should be allowed, False if rate limited"""
    key = f"{ip}:{endpoint}"
    now = time.time()
    
    if key not in rate_limit_store:
        rate_limit_store[key] = {"count": 1, "window_start": now}
        return True
    
    entry = rate_limit_store[key]
    if now - entry["window_start"] > RATE_LIMIT_WINDOW:
        # Reset window
        rate_limit_store[key] = {"count": 1, "window_start": now}
        return True
    
    if entry["count"] >= RATE_LIMIT_MAX:
        return False
    
    entry["count"] += 1
    return True


class ArkHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # High Output, Low Noise
        pass

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        response = {"status": "success", "request_id": os.urandom(4).hex(), "data": data, "timestamp": time.time()}
        self.wfile.write(json.dumps(response).encode())

    def send_json_error(self, message, status=400):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "error", "message": message, "timestamp": time.time()}).encode())

    def get_auth_user(self):
        auth = self.headers.get('Authorization')
        if not auth or not auth.startswith('Bearer '): return None
        return identity.verify_token(auth.split(' ')[1])

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in router.routes['GET']:
            router.routes['GET'][path](self)
        elif path == '/' or path.endswith('.html') or path.endswith('.js') or path.endswith('.css') or path.endswith('.png'):
            self.serve_static()
        else:
            self.send_json_error("Not Found", status=404)

    def do_POST(self):
        path = self.path.split('?')[0]
        
        # Rate limit auth endpoints
        if '/auth/' in path:
            client_ip = self.client_address[0]
            if not check_rate_limit(client_ip, path):
                self.send_json_error("Rate limited. Try again in 60 seconds.", status=429)
                return
        
        if path in router.routes['POST']:
            content_length = int(self.headers.get('Content-Length', 0))
            try:
                payload = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}
                router.routes['POST'][path](self, payload)
            except Exception as e:
                self.send_json_error(f"Invalid Request: {str(e)}")
        else:
            self.send_json_error("Not Found", status=404)

    def serve_static(self):
        path = self.path.split('?')[0]
        if path == '/': path = '/index.html'
        file_path = os.path.join(WEB_DIR, path.lstrip('/'))
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            # Simple mime type mapping
            if path.endswith('.js'): self.send_header('Content-Type', 'application/javascript')
            elif path.endswith('.css'): self.send_header('Content-Type', 'text/css')
            elif path.endswith('.html'): self.send_header('Content-Type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open(file_path, 'rb') as f: self.wfile.write(f.read())
        else:
            self.send_json_error("File Not Found", status=404)

if __name__ == '__main__':
    syncer.start()
    steward.start()
    treasury.start()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), ArkHandler) as httpd:
        logger.info(f"Ark OS Modular Core v1.2 ONLINE at port {PORT}")
        httpd.serve_forever()
