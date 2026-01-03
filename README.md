# 🌍 The Ark - Civilization OS (v0.73)

> **Building the infrastructure for a Type 1 Civilization, one node at a time.**

The Ark is a self-sovereign village operating system that enables communities of up to 150 people to achieve absolute survival sovereignty through decentralized labor markets, real-time energy tracking, and AI-assisted governance.

## 🎯 Mission

Enable the transition from Type 0.7 → Type 6 Civilization via **Abundance Tokens (AT)**, where 1 AT = 1 Hour of Validated Labor.

## 🏗️ Architecture

```
The_Ark/
├── server.py              # Main entry point (lean controller)
├── core/                  # Core business logic
│   ├── ledger.py         # Blockchain-style ledger
│   ├── identity.py       # User authentication & JWT
│   ├── energy.py         # Kardashev scale tracking
│   ├── sensors.py        # IoT/hardware bridge
│   ├── federation.py     # P2P mesh networking
│   ├── steward.py        # AI audit system
│   └── router.py         # HTTP routing
├── api/                   # API endpoints (modular)
│   ├── system.py         # Health, state, energy
│   ├── steward.py        # AI collaboration
│   ├── economy.py        # Minting, trading
│   └── social.py         # Messages, bounties
├── web/                   # Frontend UI
│   ├── index.html        # Main UI
│   ├── app.js            # Application logic
│   └── style.css         # Sovereign Dark Theme
└── tools/                 # Utilities & workflows
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- (Optional) Ollama with `deepseek-r1:1.5b` for local AI

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/The_Ark.git
cd The_Ark

# Create data directories
mkdir -p data hardware federation uploads

# Initialize the ledger
touch village_ledger_py.json
echo '{"blocks": []}' > village_ledger_py.json

# Run the server
python3 server.py
```

The Ark will be available at `http://localhost:3000`

### First Login

1. Navigate to the **Auth** tab
2. Register a new account (first user becomes ADMIN)
3. Your wallet is your identity - **SAVE YOUR SEED PHRASE**

## 🤖 Multi-AI Collaboration

The Ark supports collaboration between multiple AI systems via standardized API endpoints.

### Steward Protocol

All AIs interact through the `/api/steward/think` endpoint:

```bash
curl -X POST http://localhost:3000/api/steward/think \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Propose a technical upgrade for the village infrastructure",
    "context": {
      "current_kardashev": 0.73,
      "active_users": 5,
      "total_mints": 42
    }
  }'
```

### Supported AI Systems

| System | Integration | Purpose |
|--------|-------------|---------|
| **Ollama** | Local `/api/steward/think` | Technical audits, upgrades |
| **Google Jules** | API endpoints | Code collaboration, debugging |
| **Gemini** | API endpoints | Architecture, planning |

### AI Contribution Workflow

1. **Audit**: AI calls `/api/evolution` to get system state
2. **Think**: AI generates proposal via `/api/steward/think`
3. **Propose**: AI records mission via `/api/mission/propose`
4. **Execute**: Human reviews and implements (or delegates to AI)

## 🔑 Key Features

- ✅ **Sovereign Identity**: Seed phrase-based authentication
- ✅ **Abundance Economics**: Labor-backed currency (AT)
- ✅ **Real-time Kardashev Scale**: Track civilizational energy progress
- ✅ **Decentralized Job Board**: P2P task marketplace
- ✅ **AI Steward**: Automated system audits and upgrade proposals
- ✅ **Mesh Federation**: Connect villages via P2P network
- ✅ **Hardware Bridge**: Integrate solar, water, motion sensors

## 📡 API Reference

### System Endpoints

- `GET /api/health` - Server status
- `GET /api/state` - Village statistics
- `GET /api/system/energy` - Real-time Kardashev metrics
- `GET /api/graph?since=<id>` - Ledger sync (incremental)

### Economy Endpoints

- `POST /api/mint` - Mint Abundance Tokens (requires auth)
- `POST /api/transfer` - Send AT to another user
- `GET /api/evolution` - System evolution metrics

### Steward Endpoints

- `POST /api/steward/think` - AI brainstorming
- `POST /api/mission/propose` - AI proposal submission
- `GET /api/mission/list` - Active missions

## 🌐 Federation

Connect your node to the global mesh:

```python
# In your Python REPL or script
import requests

requests.post('http://localhost:3000/api/federation/register', json={
    'node_id': 'your-village-name',
    'endpoint': 'https://your-public-url.com',
    'coords': [lat, lon]
})
```

## 🛠️ Development

### Running Tests

```bash
python3 -m py_compile server.py core/*.py api/*.py
```

### Adding a New Module

1. Create `core/your_module.py` with your logic
2. Create `api/your_routes.py` with API endpoints
3. Import and register in `server.py`

### Contributing

We welcome contributions from humans AND AIs! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a PR with clear description
4. AIs: Include your model name in commit messages

## 📜 License

Open Source Ecology - MIT License

## 🌟 Philosophy

> "We do not ask for a better world. We build it."

The Ark operates on the principle that **absolute survival sovereignty** is achieved through:

1. **Energy mastery** (Kardashev progression)
2. **Sovereign identity** (self-custody)
3. **Abundance economics** (labor-backed value)
4. **Distributed intelligence** (human + AI collaboration)

---

**Current Kardashev Level**: Type 0.73  
**Mission Status**: ALPHA v1.0 - Modular Sharding Complete  
**Next Milestone**: Type 0.75 (Hardware Bridge Integration)
