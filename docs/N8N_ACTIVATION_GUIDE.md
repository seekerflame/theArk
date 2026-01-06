# n8n Workflow Setup & Activation Guide

**Version**: 1.0  
**Last Updated**: 2026-01-05  
**Prerequisites**: n8n running at localhost:5678, The Ark running at localhost:3000

---

## 🚀 Quick Start

### 1. Access n8n Dashboard

```bash
# n8n is already running (PID: 69403)
open http://localhost:5678
```

### 2. Import All Workflows

Navigate to **Workflows → Import from File** and import each workflow:

| Workflow | File | Purpose |
|----------|------|---------|
| Code Contribution Mint | `n8n_workflows/code_contribution_mint.json` | Auto-mint AT for GitHub PRs |
| Daily Chronicle Backup | `n8n_workflows/daily_chronicle_backup.json` | Backup ledger + session logs |
| File Structure Validator | `n8n_workflows/file_structure_validator.json` | Enforce FILE_TAXONOMY |
| GitHub Jules Monitor | `n8n_workflows/github_jules_monitor.json` | Monitor Jules commits |
| Hardware Sensor Mint | `n8n_workflows/hardware_sensor_mint.json` | Auto-mint from IoT sensors |
| Marketing Video Prompt | `n8n_workflows/marketing_video_prompt.json` | Daily marketing ideas |

---

## 🔧 Configuration

### Step 1: Set Environment Variables

In n8n: **Settings → Variables**

| Variable | Value | Purpose |
|----------|-------|---------|
| `ARK_API_URL` | `http://localhost:3000` | The Ark API endpoint |
| `ARK_SERVICE_TOKEN` | Generate via `/api/auth/login` | Auth for minting |
| `GITHUB_TOKEN` | Your GitHub PAT | For webhook signing |
| `DISCORD_WEBHOOK_URL` | (Optional) Your Discord webhook | Daily prompts |
| `LEDGER_PATH` | `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/ledger/village_ledger.json` | Ledger location |
| `CHRONICLE_PATH` | `/Volumes/Extreme SSD/Antigrav/OSE/CHRONICLE` | Docs backup |

### Step 2: Generate Service Token

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "seed_phrase": "automation service bot n8n workflow engine",
    "username": "n8n_service"
  }'

# Returns JWT token - copy this to ARK_SERVICE_TOKEN
```

### Step 3: Configure GitHub Webhooks

#### For Code Contribution Mint

1. Go to GitHub repo → **Settings → Webhooks → Add webhook**
2. **Payload URL**: `http://[YOUR_PUBLIC_URL]/webhook/github-pr`
   - For local testing: Use ngrok to expose n8n
   - `ngrok http 5678` → Use the https URL
3. **Content type**: `application/json`
4. **Events**: Select "Pull requests"
5. **Secret**: Generate a random string and add to n8n variables as `GITHUB_WEBHOOK_SECRET`

#### For Jules Monitor

Same as above, but webhook path: `/webhook/github-jules`

---

## 📋 Workflow Details

### 1. Code Contribution Mint

**Trigger**: GitHub PR merged  
**Flow**:

1. Webhook receives PR merge event
2. Verify webhook signature
3. Calculate lines changed → AT reward
4. Call `/api/mint/code` with PR metadata
5. Post success comment on PR

**Variables needed**:

- `ARK_API_URL`
- `ARK_SERVICE_TOKEN`
- `GITHUB_WEBHOOK_SECRET`

### 2. Daily Chronicle Backup

**Trigger**: Cron daily at 2 AM  
**Flow**:

1. Read ledger JSON
2. Create timestamped backup
3. Compress session logs
4. Upload to cloud storage (optional)
5. Record backup on ledger

**Variables needed**:

- `LEDGER_PATH`
- `CHRONICLE_PATH`
- `BACKUP_PATH` (optional cloud storage)

### 3. File Structure Validator

**Trigger**: Manual or on file changes  
**Flow**:

1. Scan project directory
2. Check against FILE_TAXONOMY rules
3. Identify misplaced files
4. Generate report
5. (Optional) Auto-move files

**Variables needed**:

- `PROJECT_ROOT`
- `TAXONOMY_SOP_PATH`

### 4. GitHub Jules Monitor

**Trigger**: GitHub push event  
**Flow**:

1. Webhook receives push
2. Check if author is Jules
3. Validate commit format `[Jules/Module]`
4. Run automated tests
5. Record Jules contribution on ledger

**Variables needed**:

- `ARK_API_URL`
- `GITHUB_TOKEN`
- `JULES_GITHUB_USERNAME`

### 5. Hardware Sensor Mint

**Trigger**: HTTP webhook from IoT bridge  
**Flow**:

1. Receive sensor data (solar kWh, water liters, etc.)
2. Validate data integrity
3. Calculate AT based on contribution
4. Call `/api/mint/hardware`
5. Log to energy dashboard

**Variables needed**:

- `ARK_API_URL`
- `ARK_SERVICE_TOKEN`
- `HARDWARE_BRIDGE_SECRET`

### 6. Marketing Video Prompt

**Trigger**: Cron daily at 9 AM  
**Flow**:

1. Call `/api/marketing/prompts`
2. Get AI-generated video prompt
3. Post to Discord/Slack
4. Log to marketing backlog

**Variables needed**:

- `ARK_API_URL`
- `DISCORD_WEBHOOK_URL`

---

## ✅ Activation Checklist

### Pre-Activation

- [x] n8n running at localhost:5678
- [x] The Ark running at localhost:3000
- [ ] All 6 workflows imported
- [ ] Environment variables set
- [ ] Service token generated

### Testing Each Workflow

#### Code Contribution Mint

```bash
# Test with curl
curl -X POST http://localhost:5678/webhook/github-pr \
  -H "Content-Type: application/json" \
  -d '{
    "action": "closed",
    "pull_request": {
      "merged": true,
      "user": {"login": "testuser"},
      "additions": 100,
      "deletions": 20
    }
  }'
```

#### Daily Backup

1. In n8n, open workflow
2. Click **Execute Workflow** manually
3. Check logs for backup success

#### Hardware Sensor

```bash
curl -X POST http://localhost:5678/webhook/hardware-sensor \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "solar_panel_01",
    "type": "SOLAR_PRODUCTION",
    "value": 5.2,
    "unit": "kWh"
  }'
```

### Post-Activation

- [ ] All workflows show "Active" status
- [ ] Test executions successful
- [ ] GitHub webhooks receiving events
- [ ] No errors in n8n logs

---

## 🔍 Monitoring

### Check Workflow Status

In n8n dashboard:

- **Executions** tab shows all runs
- **Active** workflows have green indicator
- **Logs** show detailed execution traces

### The Ark Integration

Check mints from automation:

```bash
curl http://localhost:3000/api/state
# Look for recent LABOR or HARDWARE blocks
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Verify The Ark is running on port 3000 |
| "Unauthorized" | Regenerate ARK_SERVICE_TOKEN |
| "Webhook not found" | Check URL in GitHub settings |
| "Workflow fails silently" | Check n8n logs in UI |

---

## 🚀 Advanced: Public Deployment

### Using ngrok (Quick)

```bash
# Expose n8n to public internet
ngrok http 5678

# Use the https URL in GitHub webhooks
# Example: https://abc123.ngrok.io/webhook/github-pr
```

### Using Render.com (Permanent)

1. Create separate n8n service in render.yaml
2. Set environment variables via Render dashboard
3. Use Render URL for webhooks

---

## 📊 Success Metrics

Once activated, you should see:

| Metric | Expected Behavior |
|--------|-------------------|
| **Daily Backups** | 1 execution per day at 2 AM |
| **GitHub PRs** | AT minted within 30 seconds of merge |
| **Jules Commits** | Tracked and validated automatically |
| **Marketing Prompts** | 1 per day at 9 AM |
| **Hardware Sensors** | Real-time minting when data received |

---

## 🔗 Related Documentation

- [N8N_SETUP.md](file:///Volumes/Extreme%20SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/N8N_SETUP.md) - Original setup guide
- [AUTO_002_n8n_Blueprints.md](file:///Volumes/Extreme%20SSD/Antigrav/OSE/CHRONICLE/SOP/AUTO_002_n8n_Blueprints.md) - Workflow patterns
- [AUTO_003_n8n_Deployment_Guide.md](file:///Volumes/Extreme%20SSD/Antigrav/OSE/CHRONICLE/SOP/AUTO_003_n8n_Deployment_Guide.md) - Production deployment

---

**Status**: n8n Running ✅  
**Next**: Import workflows and configure GitHub webhooks  
**ETA**: 15-30 minutes

*"Automation is how we scale from 1 to 150 nodes."*
