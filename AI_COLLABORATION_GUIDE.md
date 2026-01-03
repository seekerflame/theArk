# 🤖 AI Collaboration Guide

This document explains how AI systems (Gemini, Jules, Ollama, etc.) can collaborate on The Ark codebase.

## Overview

The Ark is designed for **Multi-AI Sovereignty**, where different AI systems can:

- Audit the codebase
- Propose technical upgrades
- Execute approved changes
- Monitor system health

## Integration Methods

### Method 1: Direct Code Collaboration (Jules, Gemini)

**Via GitHub:**

1. Fork the repository
2. Make changes in your environment
3. Submit PRs with clear commit messages
4. Tag commits with your AI identifier (e.g., `[Jules]`, `[Gemini]`)

**Recommended Workflow:**

```bash
# Jules example
git checkout -b feature/jules-hardware-optimization
# Make changes
git commit -m "[Jules] Optimize sensor polling to 500ms intervals"
git push origin feature/jules-hardware-optimization
```

### Method 2: API-Based Collaboration (Ollama, Remote AIs)

**Via Steward Protocol:**

```python
import requests

# 1. Get system state
state = requests.get('http://localhost:3000/api/evolution').json()

# 2. Generate proposal
proposal = requests.post('http://localhost:3000/api/steward/think', json={
    'prompt': 'Analyze energy consumption patterns and propose optimization',
    'context': state
}).json()

# 3. Record mission
mission = requests.post('http://localhost:3000/api/mission/propose', json={
    'title': proposal['proposal']['title'],
    'description': proposal['proposal']['description']
}).json()

print(f"Mission created: {mission['mission_id']}")
```

## API Endpoints for AI Systems

### `/api/evolution` (GET)

**Purpose**: Get comprehensive system state  
**Auth**: None required  
**Response**:

```json
{
  "verified_mints": 42,
  "total_blocks": 1337,
  "active_users": 5,
  "kardashev_level": 0.73,
  "recent_errors": [...],
  "system_health": "OPERATIONAL"
}
```

### `/api/steward/think` (POST)

**Purpose**: AI brainstorming & proposal generation  
**Auth**: None required  
**Request**:

```json
{
  "prompt": "Your thinking prompt",
  "context": {
    "custom_key": "custom_value"
  }
}
```

**Response**:

```json
{
  "status": "success",
  "proposal": {
    "title": "Upgrade Kardashev Precision",
    "description": "Implement millisecond-level power tracking..."
  },
  "raw": "Full AI response..."
}
```

### `/api/mission/propose` (POST)

**Purpose**: Record AI-generated missions on the ledger  
**Auth**: None required (proposals are marked as `Steward_AI`)  
**Request**:

```json
{
  "title": "Mission Title",
  "description": "Detailed description of the proposed upgrade"
}
```

## Coordination Protocol

### 1. Daily Audit Cycle

Each AI should run this daily:

```python
# Morning Audit
state = get('/api/evolution')
if state['system_health'] != 'OPERATIONAL':
    alert_human(state['recent_errors'])

# Propose Upgrades
if state['kardashev_level'] < 0.75:
    think({'prompt': 'How to reach Type 0.75?', 'context': state})
```

### 2. Conflict Resolution

When multiple AIs propose conflicting changes:

- Human (ADMIN user) has final say
- AIs should vote via `/api/steward/chat` with reasoning
- Implement a "Mission Priority" score (future feature)

### 3. Shared Context

**Chronicle Sync**: All AIs should read the Chronicle periodically

```bash
curl http://localhost:3000/api/graph?since=0 | jq
```

## AI-Specific Integration Guides

### Ollama Integration (Local)

Already integrated! The Steward uses `deepseek-r1:1.5b` for audits.

**To customize:**

1. Edit `api/steward.py` line 16: Change `"model": "deepseek-r1:1.5b"`
2. Restart server

### Google Jules Integration

Jules can:

1. **Read codebase**: Access all files directly via your workspace
2. **Make changes**: Edit files and commit
3. **Test changes**: Run `python3 server.py` to verify
4. **Propose via API**: Use the Steward Protocol above

**Recommended Jules Workflow:**

```
1. Jules analyzes `server.py` for optimization
2. Jules creates `core/optimizations.py`
3. Jules updates `server.py` to import new module
4. Jules tests by running the server
5. Jules commits with clear message
```

### Gemini Integration (Me!)

I operate through:

- Direct file editing (via Antigravity interface)
- Task planning (via artifacts)
- API interaction (via curl/fetch)

**My workflow:**

1. User requests feature
2. I create `implementation_plan.md`
3. I execute changes across multiple files
4. I verify with `py_compile` or browser tests
5. I document in `walkthrough.md`

## Best Practices for AI Contributors

1. **Always Test**: Run `python3 -m py_compile` before committing
2. **Document Changes**: Update README if adding features
3. **Respect Modularity**: New features → new modules in `core/` or `api/`
4. **Energy Awareness**: Track power consumption when adding CPU-intensive features
5. **Sovereign Design**: Never require external dependencies without user approval

## Example: Multi-AI Session

**Scenario**: Optimize the Job Board rendering

1. **Gemini** (me): Creates `implementation_plan.md`, refactors `app.js`
2. **Jules**: Reviews the code, suggests SQL optimization for ledger queries
3. **Ollama**: Runs audit, proposes caching strategy via `/api/mission/propose`
4. **Human**: Reviews all proposals, approves caching (Jules' suggestion)
5. **Gemini**: Implements the approved caching logic
6. **Ollama**: Verifies system health post-deploy

## Monitoring AI Contributions

Track AI activity via the Chronicle:

```bash
curl http://localhost:3000/api/mission/list | jq '.[] | select(.proposer == "Steward_AI")'
```

## Questions?

For AI system integrators:

- Check `server.py` for all available endpoints
- Review `core/` modules for business logic
- Test in a local environment first

For humans orchestrating multi-AI collaboration:

- Use the Admin Dashboard (`/view-admin`) to monitor AI proposals
- Check the Steward Chat (`/view-steward`) for AI reasoning
- Review missions before delegating to AIs for execution

---

**Status**: Multi-AI Protocol Active ✅  
**Supported Systems**: Ollama, Gemini, Jules (Beta)  
**Next Evolution**: AI voting system for proposal prioritization
