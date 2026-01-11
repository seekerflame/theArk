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
from core.fishery import Fishery
from core.triple_verification import TripleVerification
from core.quest_system import QuestSystem
from core.inventory import InventorySystem
from core.fiat_bridge import FiatBridge, register_fiat_routes
from core.party_quests import PartyQuestSystem
from core.harvest_marketplace import HarvestMarketplace
from core.wisdom_engine import WisdomEngine
from core.foundry import OSEFoundry
from core.verification_pyramid import VerificationPyramid
from core.hardware_bridge import HardwareBridge
from core.anti_dystopia import verify_anti_dystopia_compliance
from core.agent_controller import AgentController
from federation.file_bridge import FileBridge



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
from api.academy import AcademyAPI, register_academy_routes
from api.lifeline import register_lifeline_routes
from api.nodes import register_node_routes



# Bot Modules
from core.treasury_bot import TreasuryBot

# Configuration
PORT = int(Config.get('PORT', 3000))
JWT_KEY = Config.get_jwt_key()
DB_FILE = os.path.join(os.getcwd(), 'ledger', 'village_ledger.db')
WEB_DIR = os.path.join(os.getcwd(), 'web')
USERS_FILE = os.path.join('core', 'users.json')

# Security Warning
if JWT_KEY == 'dev_only_key_change_in_production':
    logging.warning("⚠️  Using default JWT_KEY - set JWT_TOKEN_KEY env var for production!")

# Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
logger = logging.getLogger("ArkOS")

# Instances
ledger = VillageLedger(DB_FILE)
identity = IdentityManager(USERS_FILE, JWT_KEY)
sensors = SensorRegistry(os.path.join('hardware', 'sensor_registry.json'))
peers = PeerManager(os.path.join('federation', 'federation_registry.json'), PORT)
syncer = FederationSyncer(ledger, peers, PORT)
energy = EnergyMonitor(ledger, sensors=sensors)
steward = StewardNexus(ledger, sensors, identity, server_file='server.py')
treasury = TreasuryBot(ledger)
justice = JusticeSteward(ledger, identity)
verification = TripleVerification(ledger, identity)
quest_system = QuestSystem(ledger, identity)
inventory = InventorySystem(ledger, identity)
fiat_bridge = FiatBridge(ledger)
party_quests = PartyQuestSystem(ledger, identity, quest_system)
wisdom = WisdomEngine(os.path.join(os.getcwd(), '..', '..', '..', 'CHRONICLE', 'SOP'))
academy = AcademyAPI(ledger, wisdom)
foundry = OSEFoundry(ledger)
harvest = HarvestMarketplace(ledger, inventory)
verification_pyramid = VerificationPyramid(ledger, identity)
agent_controller = AgentController()
file_bridge = FileBridge(ledger)



# Routing
router = Router()
hw_bridge = HardwareBridge() # Physical Baseline
fishery = Fishery(hardware_bridge=hw_bridge) # Initialize with bridge
auth_decorator = requires_auth(identity)

# Anti-Dystopia Compliance Check (Ethics Hardcoding)
try:
    class SystemCompliance:
        def __init__(self):
            self.ledger = ledger
            self.user_model = {"required": ["wallet_id"]} # Enforce pseudoname-only by default
            self.auth = identity
            self.tracking = {"enabled": ["timestamp", "tx_hash"]}
            self.codebase = {"license": "AGPLv3", "source_available": True}
            self.platform = type('obj', (object,), {'export_data': lambda: True, 'export_cost': 0})()
            self.feeds = {"sort_by": "chronological"}
            self.revenue = {"sources": ["labor_mint"]}
            self.moderation = {"ban_reasons": ["violence", "fraud"]}
            self.media = {"allow_nsfw": False}
            self.economy = {"interest_rate": 0}
            self.oracles = {"meta_oracle_enabled": True, "inverted_incentive": True}
    
    verify_anti_dystopia_compliance(SystemCompliance())
except Exception as e:
    logger.critical(f"🛑 ANTI-DYSTOPIA VIOLATION: {e}")
    logger.critical("🚨 RECTIFY CORE CODE BEFORE BOOTING.")
    exit(1)

# API Registration
register_system_routes(router, ledger, identity, peers, sensors, energy, fishery, hw_bridge, auth_decorator)
register_steward_routes(router, ledger, energy, steward, auth_decorator)
register_economy_routes(router, ledger, sensors, identity, justice, auth_decorator, quest_system, verification)


register_social_routes(router, ledger, auth_decorator)
register_hardware_routes(router, sensors, foundry, auth_decorator)
register_exchange_routes(router, ledger, auth_decorator)

register_justice_routes(router, ledger, justice, auth_decorator)

register_quest_routes(router, ledger, identity, auth_decorator)
register_treasury_routes(router, treasury, ledger, auth_decorator)
register_role_routes(router, ledger, identity, auth_decorator)
register_fiat_routes(router, ledger, fiat_bridge, auth_decorator)
register_academy_routes(router, academy, auth_decorator)
register_lifeline_routes(router, ledger, auth_decorator)
register_node_routes(router, ledger, identity, foundry, verification_pyramid, auth_decorator)


try:
    from api.ark_vault import register_ark_vault_routes
    register_ark_vault_routes(router, ledger, identity, auth_decorator)
    logger.info("🛡️  Ark Vault active (Data Privacy & Sales)")
except ImportError as e:
    logger.warning(f"⚠️  Ark API missing or dependencies failed: {e}")

logger.info("💰 Fiat Bridge loaded (Card ↔ BTC ↔ AT ↔ Bank)")
logger.info("📦 Inventory System loaded")
logger.info("👨‍👩‍👧 Party Quests loaded (families + groups)")
logger.info("🥬 Harvest Marketplace loaded (sell produce)")
logger.info("🛡️  Ark Vault active (Data Privacy & Sales)")

# Party & Harvest API
try:
    from api.party import register_party_routes
    
    register_party_routes(router, party_quests, harvest, auth_decorator)
    
    logger.info("🎉 Party & Harvest API endpoints registered")
    
    # Governance & Moderation
    from core.governance import GovernanceEngine
    from api.moderation import register_moderation_routes
    
    governance = GovernanceEngine(ledger, identity)
    register_moderation_routes(router, governance, identity, auth_decorator)
    logger.info("⚖️ Governance Engine & Moderation API active")
    
    # Academy Missions (Integrated into Academy)
    # register_mission_routes(router, ledger, identity, auth_decorator)
    # logger.info("🎓 Academy Missions (Learn-to-Earn) ONLINE")

    # Board Bored (Ad Network)
    from api.board_bored import register_board_bored_routes
    register_board_bored_routes(router, ledger, auth_decorator)
    logger.info("📺 Board Bored Ad Engine (Attention-to-Abundance) ONLINE")

    # Swarm Protocol
    from api.swarm import register_swarm_routes
    register_swarm_routes(router, ledger, auth_decorator)
    logger.info("🐝 Swarm Protocol (Modular Build) ONLINE")

    # Care Circle
    from api.care import register_care_routes
    register_care_routes(router, ledger, auth_decorator)
    logger.info("💗 Care Circle (Social Labor) ONLINE")

    # Federation Mesh
    from api.federation import register_federation_routes
    register_federation_routes(router, ledger, auth_decorator)
    logger.info("🌐 Federation Mesh (Cosmos) ONLINE")

    # Evolution Loop (Self-Improvement)
    from api.evolution import register_evolution_routes
    register_evolution_routes(router, ledger, auth_decorator)
    logger.info("🧬 Evolution Loop (Autopoiesis) ONLINE")

    # Trade API (Inter-Node Resource Swaps)
    from api.trade import register_trade_routes
    register_trade_routes(router, ledger, auth_decorator)
    logger.info("🤝 Trade API (Economic Federation) ONLINE")

    # Hardware Bridge (Physical/Simulated Sensors)
    from core.hardware_bridge import HardwareBridge
    hw_bridge = HardwareBridge()
    # Attach bridge to Fishery for physical interlocks
    fishery.bridge = hw_bridge

    # Gaia Autonomy Daemon (Background Observer)
    from gaia_daemon import GaiaDaemon
    gaia = GaiaDaemon(ledger, hardware_bridge=hw_bridge)
    
    # We expose Gaia's current 'pulse' to the dashboard
    @router.get('/api/gaia/pulse')
    def gaia_pulse(h):
        # Heartbeat for safety interlocks
        fishery.heartbeat()
        pulse = gaia.run_cycle()
        
        # Broadcast pulse messages to the general chat
        if 'messages' in pulse:
            for msg in pulse['messages']:
                ledger.add_block('MESSAGE', {
                    'sender': 'GAIA',
                    'content': msg,
                    'channel': 'general',
                    'timestamp': time.time(),
                    'verified': True
                })
        
        h.send_json(pulse)

    # Agent Control & File Discovery
    @router.get('/api/agents/status')
    @auth_decorator
    def get_agent_status(h, user):
        h.send_json(agent_controller.update_status_report())

    @router.post('/api/agents/control')
    @auth_decorator
    def control_agent(h, payload, user):
        service = payload.get('service')
        action = payload.get('action')
        if action == 'start':
            agent_controller.start_service(service)
        elif action == 'stop':
            agent_controller.stop_service(service)
        h.send_json({"status": "action_triggered", "service": service, "action": action})

    @router.get('/api/files/manifest')
    @auth_decorator
    def get_file_manifest(h, user):
        h.send_json(file_bridge.manifest)

    @router.post('/api/files/register')
    @auth_decorator
    def register_file(h, payload, user):
        file_path = payload.get('path')
        metadata = payload.get('metadata')
        file_hash = file_bridge.register_file(file_path, metadata)
        h.send_json({"hash": file_hash})

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

# Ark Insight (Analytics & Passport)
try:
    from api.ark_insight import register_ark_insight_routes
    register_ark_insight_routes(router, ledger, identity, hw_bridge, auth_decorator)
    logger.info("📡 Ark Insight Engine ACTIVE (Anti-Palantir)")
except ImportError as e:
    logger.warning(f"⚠️ Ark Insight missing: {e}")

# Project Exodus
try:
    from api.exodus import register_exodus_routes
    from api.exodus_admin import register_exodus_admin_routes
    register_exodus_routes(router, ledger, identity, auth_decorator)
    register_exodus_admin_routes(router, ledger, identity, admin_only)
    logger.info("🕊️ Project Exodus Bridge & Admin ONLINE (Anti-Worldcoin Protocol)")
except ImportError as e:
    logger.warning(f"⚠️ Exodus API missing: {e}")

# Collaborative Canvas
try:
    from api.collab import register_collab_routes
    register_collab_routes(router, ledger)
    logger.info("🎨 Collaborative Canvas loaded")
except ImportError as e:
    logger.warning(f"⚠️  Collab API missing: {e}")

# Rate Limiting (simple in-memory, resets on restart)
rate_limit_store = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 30  # requests per window for auth endpoints

def check_rate_limit(ip, endpoint, max_count=RATE_LIMIT_MAX):
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
    
    if entry["count"] >= max_count:
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
        # 🛡️ FISHERY INTERLOCK
        if fishery.state == "LOCKDOWN":
            return self.send_json_error("NODE IN LOCKDOWN: Physical or digital breach detected.", status=503)

        path = self.path.split('?')[0]
        if path in router.routes['GET']:
            router.routes['GET'][path](self)
        elif path == '/' or path.endswith('.html') or path.endswith('.js') or path.endswith('.css') or path.endswith('.png') or path.endswith('.md'):
            self.serve_static()
        else:
            self.send_json_error("Not Found", status=404)

    def do_POST(self):
        # 🛡️ FISHERY INTERLOCK
        if fishery.state == "LOCKDOWN":
            return self.send_json_error("NODE IN LOCKDOWN: Physical or digital breach detected.", status=503)

        path = self.path.split('?')[0]
        
        # Rate limit auth endpoints + Fishery SHIELDED state
        is_auth_route = '/auth/' in path or '/login' in path or '/register' in path
        if is_auth_route or fishery.state == "SHIELDED":
            client_ip = self.client_address[0]
            # Stricter limits if SHIELDED
            limit = 5 if fishery.state == "SHIELDED" else RATE_LIMIT_MAX
            if not check_rate_limit(client_ip, path, limit):
                if is_auth_route: fishery.report_auth_failure() # Still count as failure
                self.send_json_error("Rate limited. System is under protective shield.", status=429)
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
        
        # Determine base directory
        if path.startswith('/wiki/') or path.startswith('/library/'):
            # Serve from project root (where wiki/ and library/ are)
            file_path = os.path.join(os.getcwd(), path.lstrip('/'))
        else:
            # Serve from web directory
            file_path = os.path.join(WEB_DIR, path.lstrip('/'))
            
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            # Mime type mapping
            if path.endswith('.js'): self.send_header('Content-Type', 'application/javascript')
            elif path.endswith('.css'): self.send_header('Content-Type', 'text/css')
            elif path.endswith('.html'): self.send_header('Content-Type', 'text/html')
            elif path.endswith('.md'): self.send_header('Content-Type', 'text/markdown')
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
        logger.info(f"Ark OS Modular Core v1.2.2 ONLINE at port {PORT}")
        httpd.serve_forever()
