# FILE TAXONOMY: The Skeleton Structure

*Chronicle Location: `/CHRONICLE/SOP/FILE_TAXONOMY.md`*
*Status: MANDATORY FOR ALL AGENTS*

---

## Purpose

This document defines **where every file goes** in the OSE ecosystem. All agents (Antigravity, Jules, n8n, Ollama) MUST follow this structure. Violations will be flagged by n8n validation.

---

## 1. The Skeleton

```
/OSE/                                    # ROOT
├── CHRONICLE/                           # 📜 DOCTRINE (Read-mostly, append-only)
│   ├── SOP/                             # Standard Operating Procedures
│   ├── SESSION_LOGS/                    # AI session transcripts
│   ├── ARCHIVE/                         # Old/deprecated docs
│   ├── MANIFEST.md                      # System overview
│   └── scripts/                         # Shell scripts for Chronicle ops
│
├── abundancetoken/                      # 💾 IMPLEMENTATION
│   └── 07_Code/The_Ark/                 # Main codebase
│       ├── api/                         # API endpoint modules
│       ├── core/                        # Core business logic
│       ├── web/                         # Frontend (HTML/CSS/JS)
│       │   └── modules/                 # Modular UI components/games
│       ├── hardware/                    # Hardware bridge code
│       ├── tests/                       # Pytest suites
│       ├── tools/                       # CLI utilities
│       ├── n8n_workflows/               # Automation workflow JSON
│       ├── ledger/                      # Ledger data (JSON/SQLite)
│       ├── logs/                        # Runtime logs
│       ├── backup/                      # Backup files
│       ├── JULES_*.md                   # Agent mission specs
│       └── server.py                    # Main server entry point
│
├── ARCHIVE/                             # 🗄️ Historical/reference material
├── INTERANTICOMS/                       # 📡 Inter-node communication logs
└── furnace/                             # 🔥 Experimental/scratch space
```

---

## 2. File Routing Rules

| File Type | Location | Example |
|:---|:---|:---|
| **SOP/Doctrine** | `/CHRONICLE/SOP/` | `TOKENOMICS.md` |
| **Python module** | `/The_Ark/core/` or `/api/` | `ledger.py` |
| **Frontend file** | `/The_Ark/web/` | `app.js`, `style.css` |
| **Game/Module** | `/The_Ark/web/modules/{name}/` | `space_invaders/` |
| **Test file** | `/The_Ark/tests/` | `test_ledger.py` |
| **n8n workflow** | `/The_Ark/n8n_workflows/` | `github_jules_monitor.json` |
| **Shell script** | `/CHRONICLE/scripts/` or `/The_Ark/` | `snapshot.sh` |
| **Jules mission** | `/The_Ark/JULES_*.md` | `JULES_LIGHTNING_BRIDGE.md` |
| **Backup/export** | `/The_Ark/backup/` | `ledger_2026-01-03.json` |
| **Logs** | `/The_Ark/logs/` | `server.log` |
| **Experimental** | `/furnace/` | `crazy_idea.py` |

---

## 3. Naming Conventions

| Category | Convention | Example |
|:---|:---|:---|
| **SOP files** | `SCREAMING_SNAKE.md` | `ECONOMIC_MODEL.md` |
| **Python files** | `snake_case.py` | `lightning_bridge.py` |
| **JS files** | `camelCase.js` or `snake_case.js` | `hardwareBridge.js` |
| **Test files** | `test_{module}.py` | `test_ledger.py` |
| **Workflow JSON** | `snake_case.json` | `hardware_sensor_mint.json` |
| **Jules missions** | `JULES_{MISSION}.md` | `JULES_SECURITY_AUDIT.md` |

---

## 4. Agent Responsibilities

### Antigravity (Cursor)

- Creates SOPs in `/CHRONICLE/SOP/`
- Creates Jules missions in `/The_Ark/JULES_*.md`
- Edits any file across the structure
- Commits to Git

### Jules (GitHub)

- Works only within `/The_Ark/`
- Creates branches: `jules/{mission-name}`
- Commits with format: `[Jules] Message`
- Never touches `/CHRONICLE/` without approval

### n8n (Automation)

- Reads/writes `/The_Ark/logs/`
- Reads `/The_Ark/ledger/`
- Writes backups to `/The_Ark/backup/`
- Validates file locations (see workflow below)

### Ollama (Local LLM)

- Advisory only (no direct file access)
- Outputs via n8n HTTP requests

---

## 5. n8n Validation Workflow

Import `file_structure_validator.json` to enforce this taxonomy.

**Triggers**: GitHub webhook (on push)
**Checks**:

- Python files in correct directories
- SOPs have correct naming
- No files in root (except config)
- Tests in `tests/` directory

---

## 6. Quick Reference for Agents

```
WHERE DO I PUT THIS?

Is it doctrine/philosophy?     → /CHRONICLE/SOP/
Is it Python code?             → /The_Ark/core/ or /api/
Is it frontend?                → /The_Ark/web/
Is it a test?                  → /The_Ark/tests/
Is it an automation?           → /The_Ark/n8n_workflows/
Is it a Jules mission?         → /The_Ark/JULES_*.md
Is it experimental?            → /furnace/
```

---

*"A place for everything, everything in its place."*

*Document Owner: Antigravity / EternalFlame*
*Last Updated: 2026-01-03*
