# AT ↔ BTC Lightning Bridge Research

## Executive Summary
This document analyzes the integration of a Bitcoin Lightning Network bridge into The Ark's ecosystem. The goal is to enable bidirectional exchange between Abundance Tokens (AT) and Bitcoin (BTC), providing liquidity and real-world value backing.

## Node Implementation Comparison

### 1. LND (Lightning Network Daemon)
*   **Pros:** Widespread adoption, extensive documentation, mature REST API, robust plugin ecosystem (Loop, Pool).
*   **Cons:** Heavier resource usage.
*   **API:** gRPC and REST. REST is easy to use with `macaroons` for auth.
*   **Verdict:** **Recommended for MVP** due to broad support and easier-to-find resources/examples for Python integration.

### 2. Core Lightning (CLN)
*   **Pros:** Lightweight, highly modular (plugin system), specification-focused.
*   **Cons:** Native REST API requires a plugin (e.g., `c-lightning-REST` or `spark-wallet`).
*   **API:** JSON-RPC over Unix Socket is default. REST available via plugins.
*   **Verdict:** Strong contender for v2, but requires more setup for HTTP access compared to LND's out-of-the-box REST support.

### 3. Eclair
*   **Pros:** Scala-based, good for mobile/GUI context.
*   **Cons:** Less common for backend server infrastructure in Python environments.
*   **Verdict:** Not recommended for this specific server-side integration.

## Recommended Architecture (MVP)

**Lightning Backend:** LND (External Node)
**Integration:** Python `requests` communicating via REST API (`/v1/...`).
**Auth:** Macaroons (Hex-encoded) + TLS Certificate.

### API Patterns (LND)

1.  **Get Info**: `GET /v1/getinfo`
    *   Check node health and connectivity.
2.  **Add Invoice**: `POST /v1/invoices`
    *   Input: `{"value": <sats>, "memo": "Buy AT"}`
    *   Output: `{"payment_request": "lnbc...", "r_hash": "<base64_hash>"}`
3.  **Lookup Invoice**: `GET /v1/invoice/{r_hash}`
    *   Check status (`OPEN`, `SETTLED`, `CANCELED`).

## Exchange Rate Strategy (MVP)
*   **Fixed Rate:** 1 AT = 1000 Sats.
*   **Future:** Dynamic rate based on difficulty/energy or market oracle.

## Security Considerations
1.  **Macaroon Management:** The `admin.macaroon` (or strictly scoped `invoice.macaroon`) must be kept secure. The Ark should only store the path to it or inject it via env vars, never check it into git.
2.  **TLS Verification:** Self-signed certs from LND need to be handled (verify=False or provide cert path).
3.  **No Custody:** Ideally, The Ark generates invoices on behalf of a node controlled by the Village, but private keys remain on the node, not in The Ark's codebase.

## Proposed Module Structure (`core/lightning_bridge.py`)

The `LightningBridge` class will abstract the HTTP calls to the LND node.

```python
class LightningBridge:
    def __init__(self, node_url, macaroon_path, tls_cert_path=None):
        ...
    def create_invoice(self, sats, memo):
        ...
    def check_invoice(self, payment_hash):
        ...
```
