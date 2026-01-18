# 🛡️ Ark OS: Security Risk Log & Hardening Plan

> [!WARNING]
> This document tracks identified security vulnerabilities, leaks, and remediation status.
> **Immediate Action Required**: Rotate all credentials identified in the "Critical Leaks" section.

## 🔴 Critical Leaks (Immediate Action)

| Asset | Source | Risk | Remediation | Status |
| :--- | :--- | :--- | :--- | :--- |
| Wiki Password | `.wiki_credentials` (History) | Full wiki compromise | Rotate wiki pass; Use `git-filter-repo` to scrub history | 🔴 PENDING |
| JWT Secret | `server.py` (Old commits) | Token forgery | Change `JWT_SECRET` in `.env` | 🔴 PENDING |
| Hardware Secret | `ark_hardware_sim.py` | Internal bypass | Moved to `Config` layer | 🟢 SECURED |
| Mermaid API Key | Previous session | API abuse | Rotate key in Mermaid Chart settings | 🟢 SECURED (.env) |

## ✅ Audit Results (Jan 6)

- **scan_leaks.py** detected 3 flags.
- **Hardware Sim**: Fixed. No longer hardcoded.
- **MCP/Automation Docs**: Confirmed safe. Using `rnd_xxx` and `your_token` placeholders.

## 🟡 High Risks (To Bridge)

- **Git History Exposure**: Even with `.gitignore`, old secrets remain in the history.
- **Port 3000 Exposure**: If running on a public IP without a firewall, the local server is exposed.
- **OpenRouter Key**: If hardcoded in any evolution scripts.

## 🟢 Defenses Implemented

1. **Central Config Layer**: All secrets moved to `core/config.py` and `.env`.
2. **Standard Gitignore**: Excludes `.env`, `.wiki_credentials`, and `*.key`.
3. **Rate Limiting**: Simple in-memory rate limiting added to `server.py` for auth endpoints.
4. **Environment Template**: `ENV_TEMPLATE.md` provided to prevent hardcoding.

---
*Last Audit: 2026-01-06 16:45*
