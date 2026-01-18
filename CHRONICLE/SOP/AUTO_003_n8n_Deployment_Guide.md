# SOP: AUTO_003 - n8n Deployment Guide v2.0 (Sovereign Door)

> [!IMPORTANT]
> **The Architecture**: We use a **Single Tunnel** strategy. n8n connects to **The Ark** (Ark Tunnel). The Ark then acting as a "Sovereign Door," proxies requests internally to **Ollama** (Localhost). This bypasses all "Forbidden Origin" errors.

## 1. System Requirements

- **The Ark**: Running locally on port `3000`.
- **Ollama**: Running locally on port `11434`.
- **Cloudflared**: Running a tunnel for The Ark.

## 2. Step 1: Create the Ark Tunnel

Make the Ark visible to n8n.

1.  **Kill Old Tunnels**: `pkill -f cloudflared`
2.  **Start Tunnel**:

    ```bash
    cloudflared tunnel --url http://localhost:3000
    ```

3.  **Copy the URL**: e.g., `https://your-tunnel-name.trycloudflare.com`

## 3. Step 2: Configure n8n Workflow

The workflow uses **3 Nodes**:

### Node 1: Schedule

- **Interval**: Every 4 Hours.

### Node 2: Audit System State (HTTP Request)

- **Method**: GET
- **URL**: `https://<YOUR_TUNNEL_URL>/api/evolution`
- **Purpose**: Gets the current health/stats of the node.

### Node 3: Sovereign Brain (HTTP Request)

- **Method**: POST
- **URL**: `https://<YOUR_TUNNEL_URL>/api/steward/generate`
- **Body**:

    ```json
    {
      "model": "llama3.2:latest",
      "prompt": "Analyze this state: {{ $json.body }}",
      "stream": false
    }
    ```

- **Purpose**: Sends state to Ark Proxy -> Local Ollama -> Ark Proxy -> n8n.

### Node 4: Push to Ledger (HTTP Request)

- **Method**: POST
- **URL**: `https://<YOUR_TUNNEL_URL>/api/steward/propose`
- **Body**:

    ```json
    {
      "type": "TECHNICAL_UPGRADE",
      "content": "{{ $json.response }}",
      "author": "Ollama_Llama3"
    }
    ```

- **Purpose**: Writes the AI's idea to the permanent blockchain.

## 4. Verification

1.  **Execute Workflow**.
2.  **Check Logs**: Go to `The_Ark/sentinel.log`.
3.  **Confirm**: You should see `[STEWARD] New Proposal: ...`.

---
*Status: ACTIVE PROTOCOL*
