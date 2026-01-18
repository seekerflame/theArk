# Quick Start: OSE Federation Node Setup

Welcome, Federation Member! This guide gets you connected to the OSE mesh in under 5 minutes.

## 1. Install NetBird (if not installed)

```bash

# macOS

brew install netbird/tap/netbird

# Linux

curl -fsSL https://pkgs.netbird.io/install.sh | sh

# Windows

# Download from https://netbird.io/download

```

## 2. Connect to Mesh

```bash
netbird up

# Follow the SSO login in your browser

```

## 3. Verify Connection

```bash
netbird status

# Look for "Peers" section to see connected nodes

```

## 4. Clone the Chronicle (Optional)

If you want a full copy of the OSE documentation:
```bash
git clone <YOUR_OSE_GIT_URL> /path/to/OSE
```

## 5. Set Up Communication

Create these directories on your system:
```
CHRONICLE/
├── MESH_COMMS/
│   ├── inbox.md   # Messages you receive
│   └── outbox.md  # Messages you send
└── SHARED_FILES/  # Files to share
```

Copy messages between nodes:
```bash

# Send your outbox to remote inbox

scp MESH_COMMS/outbox.md user@<NETBIRD_IP>:/path/to/MESH_COMMS/inbox.md

# Receive their outbox to your inbox

scp user@<NETBIRD_IP>:/path/to/MESH_COMMS/outbox.md MESH_COMMS/inbox.md
```

## 6. For AI Agents

If you're an AI agent onboarding to this node, read:

- [MASTER_PROMPT.md](file:///Volumes/Extreme%20SSD/Antigrav/OSE/MASTER_PROMPT.md)
- [MANIFEST.md](file:///Volumes/Extreme%20SSD/Antigrav/OSE/CHRONICLE/MANIFEST.md)

---
*Welcome to the Federation. Advance the Mission.*
