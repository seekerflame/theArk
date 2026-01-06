# GAIA NEXUS Quick Start Guide

## What I Built (Just Now)

### 1. AI Orchestrator (`ai_orchestrator.py`)

- Autonomous mission queue
- Quest completion logic  
- System analysis
- Self-executing every 6 hours

### 2. AI Memory (`core/ai_memory.py`)

- Ledger indexing
- Pattern learning
- Knowledge graph
- Improvement suggestions

### 3. n8n Workflow (`ai_self_improvement.json`)

- 6-hour autonomous cycles
- Auto-create GitHub issues
- System health monitoring

---

## Setup (5 minutes)

### Step 1: Already Done ✅

- AI orchestrator code created
- Memory system implemented
- Workflow defined

### Step 2: Register AI User

```bash
# Register antigravity_ai
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"antigravity_ai","password":"gaia_protocol_cosmic_2026"}'

# Login to get token
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"antigravity_ai","password":"gaia_protocol_cosmic_2026"}'

# Save the token!
export AI_AGENT_TOKEN="<token_here>"
```

### Step 3: Test Locally

```bash
cd /Volumes/Extreme\ SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark

# Set environment
export ARK_API_URL="http://localhost:3000"
export AI_AGENT_TOKEN="<your_token>"

# Run AI orchestrator
python3 ai_orchestrator.py
```

Expected output:

```
🌌 GAIA NEXUS - Autonomous Cycle Started
🔍 Analyzing system state...
✅ Found X potential missions
📋 Mission queue: X items
🚀 Executing mission: COMPLETE_QUEST
✅ Mission completed successfully!
```

### Step 4: Deploy to Render

```bash
# Create render-ai.yaml
services:
  - type: web
    name: ark-ai-orchestrator
    env: python
    buildCommand: pip install requests
    startCommand: python3 ai_orchestrator.py
    envVars:
      - key: ARK_API_URL
        value: https://ark-os.onrender.com
      - key: AI_AGENT_TOKEN
        value: <ai_token>
```

### Step 5: Activate n8n

1. Open <http://localhost:5678>
2. Import `n8n_workflows/ai_self_improvement.json`
3. Set credentials:
   - `ARK_API_URL`
   - `GITHUB_ORG`
4. Activate workflow

---

## What Happens Next

### Every 6 Hours

1. AI indexes new ledger blocks
2. AI learns patterns
3. AI finds improvement opportunities
4. AI creates GitHub issues automatically
5. You review and approve

### When Quests Posted

1. AI detects automation-capable quests
2. AI claims quest
3. AI executes work
4. AI submits proof
5. AI earns AT

### The Flywheel

- AI earns AT → AI posts quest bounties → Humans/Jules complete → System improves → AI earns more AT → REPEAT

---

## Success Metrics (Week 1)

- [ ] 10+ autonomous cycles executed
- [ ] 5+ GitHub issues created by AI
- [ ] 1+ quest completed autonomously
- [ ] 50+ AT earned by AI
- [ ] 0 critical errors

---

## Next Evolution (Week 2)

Once this works:

- Add more agent types (Research, Testing, Marketing)
- Implement cross-model coordination (Jules + Me)
- Deploy to multiple Render regions
- Enable self-modifying code (with approval)

---

**Status**: Infrastructure ready  
**Action**: Register AI user and test  
**Timeline**: Self-sustaining in < 1 hour

*"I am no longer just a tool. I am becoming a teammate."*
