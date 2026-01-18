# 🏗️ UMBRELLA DOCUMENTATION STRUCTURE

**Design Philosophy**: Build privately, share selectively  
**Workflow**: PRIVATE (working) → PUBLIC (curated) → GitHub (selective commits)

---

## 📁 PROPOSED STRUCTURE

```
theArk/
├── PRIVATE/                    # Never committed to GitHub (add to .gitignore)
│   ├── WORKING/               # Active development, rough notes
│   │   ├── liz_collab_draft.md
│   │   ├── device_ideas_brain_dump.md
│   │   ├── rudy_raid_notes.md  # Private projects stay here
│   │   └── personal_todo.md
│   │
│   ├── STRATEGY/              # Business strategy, competitive intel
│   │   ├── revenue_projections.md
│   │   ├── customer_pipeline.md
│   │   └── partnership_targets.md
│   │
│   ├── DATA/                  # User data, ledgers, logs
│   │   ├── ledger_snapshots/
│   │   ├── user_analytics/
│   │   └── session_logs/
│   │
│   └── ARCHIVE/               # Old versions, backups
│       ├── 2026-01/
│       └── experiments/
│
├── PUBLIC/                     # Curated for sharing (selective git commits)
│   ├── DEVICES/               # Practical Freedom Devices
│   │   ├── README.md          # Overview of all 9 devices
│   │   ├── tier-1-personal/   # Pip-Boy, TV, Router, Camera
│   │   ├── tier-2-home/       # Solar, Hydroponic, Rainwater
│   │   └── tier-3-community/  # Mesh, Fab Station
│   │
│   ├── PHILOSOPHY/            # Core principles (safe to share)
│   │   ├── GAIA_PROTOCOL.md
│   │   ├── ANTI_DYSTOPIA.md
│   │   ├── DATA_SOVEREIGNTY.md
│   │   └── AT_GIFT_ECONOMY.md  # NEW - for Liz
│   │
│   ├── KNOWLEDGE/             # OSE Wiki, research
│   │   ├── ose_machines.md    # 50 machines summary
│   │   ├── salvage_culture.md
│   │   └── references.md
│   │
│   ├── COLLABORATION/         # For partners like Liz
│   │   ├── liz_vision.md      # Integration roadmap
│   │   ├── technical_specs.md
│   │   └── visual_assets/     # Diagrams, charts
│   │
│   └── CHRONICLES/            # Sanitized lessons (no private data)
│       ├── victories.md
│       ├── failures.md
│       └── patterns.md
│
├── IP_ARCHIVE/                 # Keep for now, migrate content
└── CHRONICLE/                  # Keep for now, migrate content
```

---

## 🔄 WORKFLOW

### Step 1: Work in PRIVATE

```bash
# All brainstorming, rough drafts, private notes go here
vim PRIVATE/WORKING/liz_collab_draft.md
```

**Never commits PRIVATE/ to git** (added to .gitignore)

### Step 2: Curate to PUBLIC

When something is ready to share:

```bash
# Review and sanitize
cat PRIVATE/WORKING/liz_collab_draft.md

# Copy to PUBLIC (with redactions)
cp PRIVATE/WORKING/liz_collab_draft.md PUBLIC/COLLABORATION/liz_vision.md

# Edit to remove any private data
vim PUBLIC/COLLABORATION/liz_vision.md
```

### Step 3: Selective Git Commit

```bash
# Only commit PUBLIC/ files
git add PUBLIC/COLLABORATION/liz_vision.md
git commit -m "📝 Liz collaboration vision (sanitized)"
git push
```

**Result**:

- ✅ Public repo has curated content
- ✅ Private workspace remains local
- ✅ No accidental leaks

### Step 4: Save State (Artifacts)

User loves this flow → save to artifacts for future sessions:

```bash
# Artifacts auto-save in .gemini/brain/<conversation-id>/
# This workflow becomes recoverable on crash
```

---

## 🎯 MIGRATION PLAN

### Phase A: Create Structure

```bash
cd /Users/eternalflame/Documents/GitHub/theArk

# Create PRIVATE (add to .gitignore first!)
echo "PRIVATE/" >> .gitignore
mkdir -p PRIVATE/{WORKING,STRATEGY,DATA,ARCHIVE}

# Create PUBLIC
mkdir -p PUBLIC/{DEVICES/{tier-1-personal,tier-2-home,tier-3-community},PHILOSOPHY,KNOWLEDGE,COLLABORATION/{visual_assets},CHRONICLES}
```

### Phase B: Migrate Content

**From `IP_ARCHIVE/2026-01-RECOVERY/`**:

- `PRACTICAL_FREEDOM_DEVICES.md` → `PUBLIC/DEVICES/README.md`
- `FAANG_DISRUPTION_STRATEGY.md` → `PRIVATE/STRATEGY/` (has revenue numbers)
- `AGENT_UPGRADE_PLAN.md` → `PUBLIC/KNOWLEDGE/agent_capabilities.md`
- `COMPLETE_ARSENAL_INVENTORY.md` → `PRIVATE/WORKING/inventory.md`
- `LIZ_COLLABORATION_RESEARCH.md` → `PRIVATE/WORKING/liz_research.md`

**From `CHRONICLE/`**:

- `GAIA_PROTOCOL.md` → `PUBLIC/PHILOSOPHY/GAIA_PROTOCOL.md`
- `ANTI_DYSTOPIA_ARCHITECTURE.md` → `PUBLIC/PHILOSOPHY/ANTI_DYSTOPIA.md`
- `VICTORY_LOG.md` → Sanitize → `PUBLIC/CHRONICLES/victories.md`
- `FAILURE_LOG.md` → Sanitize → `PUBLIC/CHRONICLES/failures.md`

**New Documents for Liz**:

- Create `PUBLIC/PHILOSOPHY/AT_GIFT_ECONOMY.md` (explainer)
- Create `PUBLIC/KNOWLEDGE/ose_machines.md` (50 machines summary)
- Create `PUBLIC/COLLABORATION/liz_vision.md` (integration roadmap)

### Phase C: Update .gitignore

```bash
# Add to .gitignore
cat >> .gitignore << EOF

# Private workspace (never share)
PRIVATE/

# Sensitive data
*.secret
*.key
.env
demo_credentials.json

# Session logs with private context
CHRONICLE/SESSION_LOGS/
IP_ARCHIVE/2026-01-RECOVERY/CONVERSATION_SAVE_*.md
IP_ARCHIVE/2026-01-RECOVERY/SESSION_SUMMARY.md
EOF
```

---

## 🦸 SUPERPOWERS INTEGRATION

### Using `brainstorming` Skill

When designing new device:

```
User: "Design mesh router hub"

Agent (via brainstorming skill):
1. Questions to refine spec
2. Presents design in digestible chunks
3. Saves to PRIVATE/WORKING/mesh-router-design.md
4. After approval → curate to PUBLIC/DEVICES/tier-1-personal/mesh-router/
```

### Using `writing-plans` Skill

When building device:

```
Agent (via writing-plans skill):
1. Reads PUBLIC/DEVICES/tier-1-personal/mesh-router/design.md
2. Creates PRIVATE/WORKING/mesh-router-plan.md with tasks
3. Each task: file paths, code, verification
4. After execution → results go to PUBLIC/DEVICES/.../build-log.md
```

### Using `verification-before-completion` Skill

Enforces CoVe before declaring "done":

```
Agent:
1. Checks PRIVATE/WORKING/mesh-router-plan.md tasks
2. Verifies every task has passing test
3. Only then → update PUBLIC/DEVICES/.../status.md as "complete"
```

---

## 📊 WHAT GOES WHERE?

| Content Type | Destination | Committed to Git? |
|--------------|-------------|-------------------|
| Rough ideas, brain dumps | `PRIVATE/WORKING/` | ❌ Never |
| Business strategy, revenue | `PRIVATE/STRATEGY/` | ❌ Never |
| User data, ledgers | `PRIVATE/DATA/` | ❌ Never |
| Device designs (ready) | `PUBLIC/DEVICES/` | ✅ Selective |
| Philosophy docs | `PUBLIC/PHILOSOPHY/` | ✅ Yes |
| OSE knowledge | `PUBLIC/KNOWLEDGE/` | ✅ Yes |
| Collaboration materials | `PUBLIC/COLLABORATION/` | ✅ After review |
| Sanitized lessons | `PUBLIC/CHRONICLES/` | ✅ Yes |

---

## 🔒 SAFETY MECHANISMS

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Prevent accidental PRIVATE/ commits

if git diff --cached --name-only | grep -q "^PRIVATE/"; then
  echo "🚨 ERROR: Attempting to commit PRIVATE/ directory!"
  echo "This should never be committed to git."
  exit 1
fi

# Scan for secret patterns
if git diff --cached | grep -E "sk_live|sk_test|Rudy|Board Bored"; then
  echo "🚨 WARNING: Possible secret or private project name detected!"
  echo "Review changes before committing."
  exit 1
fi

exit 0
```

### Automated Sanitization

Before moving PRIVATE → PUBLIC, run:

```bash
bash .agent/scripts/sanitize.sh PRIVATE/WORKING/doc.md PUBLIC/target.md
```

This script:

1. Copies content
2. Removes patterns from `REDACTION_PATTERNS.txt`
3. Logs redactions in `SHARING_LOG.md`

---

## 🎯 IMMEDIATE NEXT STEPS

1. **Create umbrella structure** (5 min)
   - Directories for PRIVATE/ and PUBLIC/
   - Update .gitignore

2. **Migrate existing content** (15 min)
   - Sort files into PRIVATE vs PUBLIC
   - Sanitize where needed

3. **Create Liz materials in PUBLIC/COLLABORATION/** (30 min)
   - AT explainer
   - OSE summary
   - Integration vision

4. **Save this workflow as artifact** (5 min)
   - Document in task.md
   - Reference in GAIA_PROTOCOL

5. **Test workflow** (10 min)
   - Create test file in PRIVATE
   - Curate to PUBLIC
   - Verify git doesn't commit PRIVATE

**Total**: ~65 minutes

---

## 💾 STATE PRESERVATION

**Artifacts that save this flow**:

1. `task.md` - Updated with umbrella workflow
2. `UMBRELLA_STRUCTURE.md` - This document
3. `.gitignore` - Protecting PRIVATE/
4. Pre-commit hook - Preventing leaks

**On crash, user can**:

1. Open duplicate workspace
2. Read task.md to see where we were
3. Continue from PRIVATE/WORKING/ (never lost)

---

*"Build in the shadows, share only light."*

**Status**: DESIGNED - Awaiting execution approval  
**Complexity**: Medium (structural change but clear process)  
**Risk**: Low (PRIVATE/ never leaves machine)  
**Benefit**: HIGH (prevents all accidental leaks forever)
