# SOP: NET_001 - Universal Access (Beyond NetBird)

> [!IMPORTANT]
> **Goal**: Access your node from any device (Phone, Tablet, Laptop) via a simple URL, without sacrificing sovereignty.

## 1. The Gateway Strategy

Instead of requiring every device to install NetBird, the Node acts as a **Secure Gateway**.

### 1.1 Cloudflare Tunnel (Easy Access)

- **Deployment**: Node runs `cloudflared` to expose `localhost:3000` to a secure subdomain (e.g., `ark.yourdomain.com`).
- **Security**: Access is gated by **Cloudflare Access** (OAuth) or our internal **Sovereign JWT** system.
- **Ease of Use**: No apps needed. Just go to the URL and log in.

### 1.2 PWA (Progressive Web App)

- Your Gaia UI is already PWA-compliant.
- **Step**: Open the URL in Safari (iOS) or Chrome (Android) and "Add to Home Screen."
- **Result**: A native-feeling app interface with offline support and mesh-sync capability.

## 2. Incentivizing Node Runners

"Maybe running nodes is rewarded."

### 2.1 The "Infrastructure Fee" (Node Yield)

- **The Protocol**: Every transaction (TX) processed by a node mints a small "Yield" in AT for the node owner.
- **Proof of Uptime**: Nodes that maintain 99% uptime for the federation receive a **Resilience Bounty** monthly.
- **CPU Sharing**: If a peer node is performing heavy compute (LLM training/Ledger audit), it can "offload" tasks to idle nodes, paying them in AT for the compute cycles used.

## 3. The "Wifi-to-Node" Handshake

- **Local Mesh**: When your phone is near a physical OSE node, it automatically detects the "spore" SSID and switches from Public Internet to **Direct Mesh**.
- **Silent Update**: Updates are pushed over this local connection, bypasssing any ISP-level blocking or filtering.

---
*Status: UNIVERSAL ACCESS PROTOCOL DESIGNED*
