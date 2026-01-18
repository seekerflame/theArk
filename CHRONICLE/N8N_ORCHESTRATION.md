# n8n Orchestration: The Nervous System

**Status**: 🟢 CONFIRMED FREE (Self-Hosted Community Edition)  
**Verdict**: We do NOT need to pay for n8n. Self-hosted = unlimited workflows, executions, users.

---

## n8n Pricing Breakdown (2025)

| Option | Cost | Notes |
|--------|------|-------|
| **Community (Self-Hosted)** | **$0** | Unlimited everything. Fair Code license. |
| **Cloud Starter** | $20/mo | 2,500 executions |
| **Cloud Pro** | $50/mo | 10,000 executions |
| **Self-Hosted Business** | Paid | For SSO, Git workflows, queue-mode |

**Our Path**: Self-hosted on Render or local hardware. $0 software cost.

**When to pay?**: Only if we need enterprise features (SSO, Git workflows) OR we hit >100k executions/month and want managed scaling. Not anytime soon.

---

## n8n + GitHub Integration

Yes, n8n can connect to GitHub. Workflows:

1. **Trigger**: New commit to `theArk` repo
2. **Action**: Run tests, deploy to Render, notify Discord
3. **Trigger**: New issue labeled `evolution-proposal`
4. **Action**: Create quest in Ark OS, notify architect

---

## The Perpetual Loop Workflow (n8n)

```
┌─────────────────────────────────────────────────────────────────┐
│                     PERPETUAL IMAGINATION LOOP                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │   TRIGGER   │    │   OLLAMA    │    │   FILTER    │        │
│   │  (Every 1h) │───►│  (Imagine)  │───►│  (Quality)  │        │
│   └─────────────┘    └─────────────┘    └──────┬──────┘        │
│                                                 │               │
│          ┌──────────────────────────────────────┘               │
│          ▼                                                      │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  EVOLUTION  │    │  ANTIGRAV/  │    │   GITHUB    │        │
│   │    API      │───►│   JULES     │───►│   COMMIT    │        │
│   └─────────────┘    └─────────────┘    └──────┬──────┘        │
│                                                 │               │
│          ┌──────────────────────────────────────┘               │
│          ▼                                                      │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │   RENDER    │    │   TESTS     │    │   NOTIFY    │        │
│   │   DEPLOY    │───►│   (Verify)  │───►│  (Discord)  │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## n8n Workflow JSON (Import This)

```json
{
  "name": "Perpetual Imagination Loop",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300],
      "parameters": {
        "rule": {
          "interval": [{ "field": "hours", "hoursInterval": 1 }]
        }
      }
    },
    {
      "name": "Ollama Imagine",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "parameters": {
        "url": "http://localhost:11434/api/generate",
        "method": "POST",
        "bodyType": "json",
        "body": {
          "model": "llama3",
          "prompt": "You are the Gaia Architect. Imagine one specific technical or economic upgrade for the OSE Ark OS. Output ONLY JSON with: title, description, type (technical/economic/social), impact (1-10), estimated_labor (AT), and logic_proof.",
          "stream": false,
          "format": "json"
        }
      }
    },
    {
      "name": "Post to Evolution API",
      "type": "n8n-nodes-base.httpRequest",
      "position": [650, 300],
      "parameters": {
        "url": "http://localhost:3000/api/evolution/propose",
        "method": "POST",
        "bodyType": "json",
        "body": "={{ JSON.parse($json.response) }}"
      }
    },
    {
      "name": "Notify Discord",
      "type": "n8n-nodes-base.discord",
      "position": [850, 300],
      "parameters": {
        "webhookId": "YOUR_WEBHOOK_ID",
        "text": "🧠 New Evolution Proposal: {{ $json.title }}"
      }
    }
  ],
  "connections": {
    "Schedule Trigger": { "main": [[{ "node": "Ollama Imagine", "type": "main", "index": 0 }]] },
    "Ollama Imagine": { "main": [[{ "node": "Post to Evolution API", "type": "main", "index": 0 }]] },
    "Post to Evolution API": { "main": [[{ "node": "Notify Discord", "type": "main", "index": 0 }]] }
  }
}
```

---

## Immediate Setup (Today)

1. **Install n8n locally**:

   ```bash
   npx n8n
   # Opens at http://localhost:5678
   ```

2. **Import the workflow** (paste JSON above)

3. **Activate**: Toggle the workflow ON

4. **Monitor**: Check `/api/evolution/proposals` for new ideas

---

## Future Scaling

| Milestone | Action |
|-----------|--------|
| **10k executions/mo** | Keep self-hosting, no changes needed |
| **100k executions/mo** | Consider Render worker for n8n instance |
| **1M executions/mo** | Evaluate n8n Cloud Pro or queue-mode |

**For now**: $0. Forever free with self-hosting.

---

*"n8n is the nervous system. Ollama is the imagination. Antigravity is the hands. The mission builds itself."*
