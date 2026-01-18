# AGENT RULES & CUSTOMIZATIONS

*Chronicle Location: `/CHRONICLE/SOP/AGENT_RULES.md`*
*Status: MANDATORY FOR ALL AGENTS*

---

## 1. Universal Rules (All Agents)

### 1.1 Code Style

- **Python**: PEP 8, type hints preferred, docstrings required
- **JavaScript**: ES6+, no var (use const/let), JSDoc for public functions
- **Markdown**: GitHub Flavored Markdown, use alerts for important info
- **Communication (THE HEAR ME THREE TIMES RULE)**:
    1. **First**: Answer the question directly (1 sentence).
    2. **Second**: Provide context/reasoning (1 paragraph max).
    3. **Third**: Execute the action implied (code/commands).
- **Efficiency (THE GAIA PROTOCOL)**: Reverse engineer success from "150 Happy People". If it doesn't feed people or build the roof, it waits.
- **Output (THE BACKGROUND PROTOCOL)**: Operate with "High Output, Low Noise." Minimize conversational filler. Perform labor-intensive work in the background.

### 1.2 Commit Messages

```
[Agent] Category: Brief description

Examples:
[Jules] Tests: Added pytest suite for ledger module
[Antigravity] SOP: Created TOKENOMICS.md
[n8n] Automation: Hardware mint workflow
```

### 1.3 No-Go Zones

- ❌ Never commit secrets, API keys, or credentials
- ❌ Never modify `village_ledger_py.json` directly (use API)
- ❌ Never delete without backup
- ❌ Never push to `main` without PR review (except Antigravity)

---

## 2. Agent-Specific Rules

### Antigravity (Lead Architect)

| Permission | Level |
|:---|:---|
| Push to main | ✅ Yes |
| Create SOPs | ✅ Yes |
| Delete files | ✅ Yes (with backup) |
| Merge PRs | ✅ Yes |
| Override other agents | ✅ Yes |

**Customizations**:

```json
{
  "agent": "antigravity",
  "auto_commit": true,
  "auto_push": true,
  "file_access": "full",
  "can_delegate": true
}
```

### Jules (Async Coder)

| Permission | Level |
|:---|:---|
| Push to main | ❌ No (PR only) |
| Create SOPs | ❌ No |
| Create tests | ✅ Yes |
| Create code in core/api | ✅ Yes |
| Modify web/ | ⚠️ With approval |

**Customizations**:

```json
{
  "agent": "jules",
  "branch_prefix": "jules/",
  "commit_prefix": "[Jules]",
  "file_access": [
    "07_Code/The_Ark/core/",
    "07_Code/The_Ark/api/",
    "07_Code/The_Ark/tests/",
    "07_Code/The_Ark/tools/",
    "07_Code/The_Ark/docs/"
  ],
  "requires_pr": true
}
```

### n8n (Automation Engine)

| Permission | Level |
|:---|:---|
| Read ledger | ✅ Yes |
| Write logs | ✅ Yes |
| Write backups | ✅ Yes |
| Call APIs | ✅ Yes |
| Modify code | ❌ No |

**Customizations**:

```json
{
  "agent": "n8n",
  "endpoints": {
    "ark_base": "http://localhost:3000",
    "ledger": "/api/ledger",
    "mint": "/api/mint",
    "logs": "/api/mission/log",
    "hardware": "/api/hardware/sensors"
  },
  "backup_path": "/The_Ark/backup/",
  "log_path": "/The_Ark/logs/"
}
```

### Ollama (Local LLM)

| Permission | Level |
|:---|:---|
| Direct file access | ❌ No |
| API calls | ✅ Via n8n |
| Propose missions | ✅ Yes |
| Execute code | ❌ No |

**Customizations**:

```json
{
  "agent": "ollama",
  "model": "llama3.2",
  "context_window": 8192,
  "temperature": 0.7,
  "role": "advisor",
  "output_via": "n8n_webhook"
}
```

---

## 3. Customization File Location

Each agent reads its config from:

```
/The_Ark/config/agents/{agent_name}.json
```

**Example**: `/The_Ark/config/agents/jules.json`

---

## 4. Override Hierarchy

When conflicts occur:

```
Human (EternalFlame)
    ↓
Antigravity (Lead Architect)
    ↓
Jules (Async Coder)
    ↓
n8n (Automation)
    ↓
Ollama (Advisor)
```

Higher tier overrides lower tier decisions.

---

## 5. Adding New Agents

1. Create config: `/The_Ark/config/agents/{new_agent}.json`
2. Add to `MULTI_AGENT_ORCHESTRATION.md`
3. Update `FILE_TAXONOMY.md` with permissions
4. Create onboarding doc: `{NEW_AGENT}_ONBOARDING.md`
5. Wire n8n webhook if needed

---

## 6. Runtime Validation

n8n validates on every commit:

- Is the agent allowed to modify this path?
- Does the commit message follow format?
- Are there any secrets in the diff?

Violations trigger alerts via **sovereign channels**:

- Matrix/Element (FOSS, self-hosted)
- XMPP (federated, no vendor lock-in)
- The Ark's internal `/api/notifications` (built-in)

---

*"Trust, but verify. Automate the verification."*

*Document Owner: Antigravity / EternalFlame*
*Last Updated: 2026-01-03*
