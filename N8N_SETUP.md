# n8n Workflow Setup Guide

> **Status**: n8n running on `http://localhost:5678`
> **Ark API**: `http://localhost:3001`

---

## Quick Setup

### 1. Open n8n

```
http://localhost:5678
```

### 2. Import Workflows

Go to **Workflows → Import from File** and import:

| Workflow | Path |
|----------|------|
| Code Contribution Mint | `n8n_workflows/code_contribution_mint.json` |
| Marketing Video Prompt | `n8n_workflows/marketing_video_prompt.json` |

### 3. Set Environment Variables

In n8n, go to **Settings → Environment Variables** and add:

| Variable | Value | Purpose |
|----------|-------|---------|
| `ARK_API_URL` | `http://localhost:3001` | Ark server URL |
| `ARK_SERVICE_TOKEN` | Generate via `/api/auth/login` | Auth for minting |
| `DISCORD_WEBHOOK_URL` | Your Discord webhook | For daily prompts |

### 4. Configure GitHub Webhook

In your GitHub repo → **Settings → Webhooks → Add webhook**:

| Field | Value |
|-------|-------|
| Payload URL | `http://[YOUR_N8N_URL]/webhook/github-pr` |
| Content type | `application/json` |
| Events | Pull requests |

---

## Verify

1. **Test marketing endpoint**:

```bash
curl http://localhost:3001/api/marketing/prompts
```

1. **Test n8n health**:

```bash
curl http://localhost:5678/healthz
```

---

## Auto-Start on Boot

Add to crontab or launchd:

```bash
@reboot cd /path/to/The_Ark && python3 server.py &
@reboot n8n start &
```
