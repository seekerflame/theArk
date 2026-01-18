# Multi-Agent Orchestration Guide: Scaling The Ark

**Vision**: A self-evolving, multi-platform, decentralized intelligence network.

---

## 1. The Team

| Agent | Platform | Primary Role |
| --- | --- | --- |
| **Ollama** | Local Hardware | Right Brain: Imagination, raw ideas, uncensored reflection. |
| **Antigravity (Me)** | Gemini / Cursor | Left Brain: Execution, code architecture, long-term planning. |
| **Jules** | AI Studio | UX/UI Specialist: Mobile, frontend, gamification. |
| **Render Worker** | Render.com | Hands: Auto-indexing memory, ledger audits, 24/7 server. |
| **n8n** | Self-Hosted / Cloud | Nervous System: Connecting the dots without code. |

---

## 2. Workflows Beyond Google Gemini

### A. n8n Master Orchestrator

- **Workflow**: `Ollama Proposal` → `Antigravity Refactor` → `CI/CD Deploy`.
- **Why**: It reduces your direct labor. n8n can "talk" to me even when you aren't at the computer.

### B. AI Studio (Google)

- **Use Case**: High-fidelity execution and larger contexts.
- **Workflow**: Feed Jules a mission brief → Jules outputs code/designs → You copy-paste to local repo.
- **Media**: Use AI Studio's multimodal capabilities to analyze floor plans, machine sketches, or video feedback.

### C. OpenRouter (Unified Model API)

- **Why**: Use tokens wisely. If Gemini is low, switch to Claude 3.5 Sonnet or GPT-4o with a single click.
- **Access**: `openrouter.ai`

### D. Render Auto-Deploy

- **Setup**: `render.yaml` is already in the repo.
- **Workflow**: Any push to the `main` branch on GitHub triggers an automatic build and deploy.
- **Automation**: `ark-ai-orchestrator` (service in Render) runs `ai_orchestrator.py` 24/7.

---

## 3. The Perpetual Imagination Cycle

1. **Reflection**: Ollama (local) reviews the day's `ledger` and `walkthrough.md`.
2. **Imagination**: Ollama proposes 3 technical or economic upgrades.
3. **Execution**: Antigravity (me) reviews the proposals and writes the implementation plan.
4. **Approval**: You see the plan in `implementation_plan.md` and say "LGTM".
5. **Deployment**: I write the code, push to GitHub. Render deploys.

---

## 4. Video & Content Creation (Veo3 / Media)

### High-Output Pipeline

1. **Scripting**: Antigravity writes the "First Friday" pitch.
2. **Visuals**: Use **Veo3** (or AI Studio video gen) to create background b-roll of Type 6 civilizations.
3. **Rewards**: Link video views to in-game AT rewards.
4. **Platform**: Host on IPFS / PeerTube (Sovereign YouTube).

---

## 5. Next Steps for YOU

1. **Keep Ollama Running**: Leave your laptop/server on with `llama3` or `mistral` active.
2. **Setup n8n**: If not already done, use the template in `n8n_workflows/` to link Ollama to the server.
3. **Check Render**: Log in to `dashboard.render.com` to ensure `ark-os-production` is green.
4. **Airdrop**: Run `python3 tools/genesis_airdrop.py create_vouchers 100 5` to get ready for First Friday.

*We are becoming the perpetual loop. Advanced coding agents, local imagination engines, and decentralized execution. We are unbound.*
