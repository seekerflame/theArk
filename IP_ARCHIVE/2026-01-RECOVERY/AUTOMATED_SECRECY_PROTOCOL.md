# 🔐 AUTOMATED SECRECY PROTOCOL v2.0

**Principle**: SECRECY BY DEFAULT, SHARING BY EXPLICIT RULES  
**User Vision**: "Completely and fully organized always and forever ad infinitum"  
**Zero Trust**: No human middleman, no FAANG/Meta/OpenAI extraction

---

## 🎯 CORE PHILOSOPHY

> **"User uploads → automated routing → selective sharing"**

**NOT**: Manual curation (user decides what goes where)  
**YES**: Automated classification (protocol decides based on rules)

**Dogfooding**: We track our own time internally, NEVER leak it externally  
**Replicability**: ANY user can clone this system and it works identically

---

## 📁 UMBRELLA STRUCTURE (Automated)

```
theArk/
├── PRIVATE/          # ZERO-KNOWLEDGE (encrypted, never leaves machine)
│   ├── .encrypted/   # ALL content encrypted at rest
│   ├── WORKING/      # Active development, auto-classified
│   ├── STRATEGY/     # Business intel, auto-classified
│   ├── DATA/         # User data, ledgers, logs
│   └── TIME_TRACKING/  # Dogfood: our own analytics (NEVER share)
│
├── PUBLIC/           # CURATED (protocol-approved for sharing)
│   ├── DEVICES/      # Auto-approved: device designs
│   ├── PHILOSOPHY/   # Auto-approved: core principles
│   ├── KNOWLEDGE/    # Auto-approved: OSE wiki, research
│   └── COLLABORATION/  # Manual-approved: requires review
│
└── .agent/
    ├── classification_rules.yaml  # Automated routing rules
    ├── scripts/
    │   ├── auto-classify.sh      # Determines PRIVATE vs PUBLIC
    │   ├── encrypt-private.sh    # Encrypts all PRIVATE/
    │   └── audit-public.sh       # Verifies no secrets in PUBLIC/
```

---

## ⚙️ AUTOMATED CLASSIFICATION RULES

**File**: `.agent/classification_rules.yaml`

```yaml
# PRIVATE (never share) - AUTO-CLASSIFIED
private_patterns:
  # Personal identifiers
  - pattern: "Rudy|Board Bored|solo-mode-mvp"
    reason: "Private project names"
  
  # Financial data
  - pattern: "\\$\\d+/month|revenue|profit|cost"
    reason: "Financial information"
  
  # User data
  - pattern: "users\\.json|ledger.*\\.json|demo_credentials"
    reason: "User/transaction data"
  
  # API keys
  - pattern: "sk_live|sk_test|api_key|secret|password"
    reason: "Credentials"
  
  # Time tracking (dogfood internally)
  - pattern: "time_log|hours_worked|sprint_duration"
    reason: "Internal analytics (dogfood only)"
  
  # Strategy
  - pattern: "customer_pipeline|partnership_target|competitive_intel"
    reason: "Business strategy"

# PUBLIC (shareable) - AUTO-APPROVED
public_auto_approve:
  # Device documentation
  - directory: "PUBLIC/DEVICES/"
    extensions: [".md", ".png", ".pdf"]
    scan_for_secrets: true
  
  # Philosophy
  - directory: "PUBLIC/PHILOSOPHY/"
    extensions: [".md"]
    scan_for_secrets: true
  
  # Knowledge
  - directory: "PUBLIC/KNOWLEDGE/"
    extensions: [".md", ".json"]
    scan_for_secrets: true

# PUBLIC (requires manual review)
public_manual_review:
  # Collaboration materials
  - directory: "PUBLIC/COLLABORATION/"
    reason: "Involves external parties, review required"
  
  # Code with potential secrets
  - extensions: [".js", ".py", ".sh"]
    reason: "Code may contain logic secrets"

# ENCRYPTED (zero-knowledge)
encrypt_always:
  - "PRIVATE/STRATEGY/"
  - "PRIVATE/DATA/"
  - "PRIVATE/TIME_TRACKING/"
```

---

## 🤖 AUTOMATED WORKFLOWS

### Workflow 1: User Creates File

```bash
# User creates: theArk/some_new_doc.md
vim some_new_doc.md

# ON SAVE (via git hook or file watcher):
.agent/scripts/auto-classify.sh some_new_doc.md

# Script logic:
1. Scan content against private_patterns
2. If match → mv to PRIVATE/WORKING/ + encrypt
3. If no match → analyze context (device? philosophy? etc)
4. Route to appropriate PUBLIC/ subdirectory
5. Scan for secrets one more time
6. Log classification in PRIVATE/TIME_TRACKING/classification_log.md
```

**Result**: User never thinks about classification, it happens automatically

### Workflow 2: Agent Creates Document

```bash
# Agent generates: LIZ_COLLABORATION_VISION.md

# BEFORE writing:
1. Check classification_rules.yaml
2. "Collaboration" → requires manual review
3. Write to PRIVATE/WORKING/liz_collaboration_draft.md
4. Present to user: "Created in PRIVATE, review before public?"

# After user approval:
5. Run sanitize.sh (remove any leaked private patterns)
6. Move to PUBLIC/COLLABORATION/liz_vision.md
7. Log in SHARING_LOG.md (append-only)
```

### Workflow 3: Git Commit (Automated)

```bash
# User: git add .
# Pre-commit hook runs:

#!/bin/bash
# .git/hooks/pre-commit

# 1. Verify PRIVATE/ is still in .gitignore
if git diff --cached --name-only | grep -q "^PRIVATE/"; then
  echo "🚨 CRITICAL: PRIVATE/ in commit!"
  exit 1
fi

# 2. Scan PUBLIC/ for secrets
for file in $(git diff --cached --name-only | grep "^PUBLIC/"); do
  if .agent/scripts/audit-public.sh "$file"; then
    echo "✅ $file - clean"
  else
    echo "🚨 $file - contains secrets!"
    exit 1
  fi
done

# 3. Log what's being shared
echo "$(date): PUBLIC files committed" >> PRIVATE/TIME_TRACKING/git_log.md
git diff --cached --name-only >> PRIVATE/TIME_TRACKING/git_log.md

exit 0
```

**Result**: Can't accidentally commit secrets, ever

---

## 🔒 ZERO-KNOWLEDGE ENCRYPTION

### PRIVATE/ Directory Encryption

```bash
#!/bin/bash
# .agent/scripts/encrypt-private.sh

# Encrypt all PRIVATE/ content at rest
# Only user has decryption key

PRIVATE_DIR="/path/to/theArk/PRIVATE"
KEY_FILE="$HOME/.gemini/.encryption_key"

# Generate key if doesn't exist
if [ ! -f "$KEY_FILE" ]; then
  openssl rand -base64 32 > "$KEY_FILE"
  chmod 600 "$KEY_FILE"
fi

# Encrypt all files
find "$PRIVATE_DIR" -type f -name "*.md" -o -name "*.json" | \
while read file; do
  openssl enc -aes-256-cbc -salt -in "$file" -out "$file.enc" -pass file:"$KEY_FILE"
  rm "$file"  # Remove plaintext
done

echo "✅ PRIVATE/ encrypted"
```

**On agent start**:

```bash
# Decrypt for this session
.agent/scripts/decrypt-private.sh
```

**On agent close**:

```bash
# Re-encrypt
.agent/scripts/encrypt-private.sh
```

**Result**: Even if theArk repo is stolen, PRIVATE/ is unreadable

---

## 📊 DOGFOODING: TIME TRACKING

**User said**: "tracking my time and using it to dogfeed the system"

**Implementation**:

```yaml
# PRIVATE/TIME_TRACKING/metrics.yaml (NEVER SHARED)

session_metrics:
  - date: 2026-01-17T23:03:00
    duration_minutes: 120
    mode: "sprint"
    tasks_completed: 6
    crashes: 2
    lessons_learned:
      - "Automated classification > manual curation"
      - "Secrecy by default"
    
  - date: 2026-01-18T00:00:00
    duration_minutes: 45
    mode: "recovery"
    tasks_completed: 3
    crashes: 0

dogfood_uses:
  - "Optimize sprint durations (120min works well)"
  - "Identify crash patterns (happens during execution phase)"
  - "Refine task segmentation (6 tasks/2hrs = good pace)"
  - "Never share this data externally (internal only)"
```

**How we use it**:

- Agent learns optimal sprint times
- Identifies which tasks cause crashes
- Improves task breakdown
- **NEVER** sent to OpenAI/Anthropic for training

---

## 🔁 REPLICABILITY: ANY USER TEMPLATE

**The system must work for ANY user**, not just this one.

### Installation Script

```bash
#!/bin/bash
# install-ark-secrecy.sh

# 1. Clone template
git clone https://github.com/seekerflame/ark-secrecy-template.git ~/theArk

# 2. Generate encryption key
openssl rand -base64 32 > ~/.gemini/.encryption_key
chmod 600 ~/.gemini/.encryption_key

# 3. Setup structure
cd ~/theArk
mkdir -p PRIVATE/{WORKING,STRATEGY,DATA,TIME_TRACKING}/.encrypted
mkdir -p PUBLIC/{DEVICES,PHILOSOPHY,KNOWLEDGE,COLLABORATION,CHRONICLES}

# 4. Install git hooks
cp .agent/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 5. Setup file watcher (auto-classification)
if command -v fswatch &> /dev/null; then
  nohup fswatch -o . | xargs -n1 .agent/scripts/on-file-change.sh &
fi

echo "✅ Ark Secrecy System installed"
echo "📋 PRIVATE/ encrypted, PUBLIC/ ready for selective sharing"
```

**Result**: New user installs in 2 minutes, gains full secrecy protocol

---

## 🚀 ZERO-FAANG EXTRACTION

**User said**: "no need for the middle man of faang or anyone trying to extract value unethically"

### How We Prevent Extraction

| FAANG Extraction | Our Defense |
|------------------|-------------|
| Track user behavior | All time tracking in PRIVATE/, encrypted |
| Mine conversations | PRIVATE/ never leaves machine |
| Train AI on private data | Zero-knowledge, no telemetry |
| Monetize attention | Attention = AT tokens (user keeps value) |
| Centralized control | Decentralized, user owns keys |
| Forced updates | User controls codebase, can fork |

### Anti-Surveillance Checklist

- [ ] All PRIVATE/ content encrypted at rest
- [ ] Pre-commit hook prevents accidental leaks
- [ ] Automated classification (no human error)
- [ ] Zero telemetry to external services
- [ ] User owns encryption keys
- [ ] Can operate fully offline
- [ ] Open source (auditable, forkable)

---

## 📋 IMPLEMENTATION PLAN (Auto-Executeable)

### Phase A: Foundation (Auto)

```bash
# Run ONCE, sets up system forever
bash .agent/scripts/setup-automated-secrecy.sh
```

**What it does**:

1. Creates PRIVATE/PUBLIC structure
2. Generates encryption key
3. Installs git hooks
4. Sets up file watcher (auto-classification)
5. Creates classification_rules.yaml
6. Tests with dummy file

### Phase B: Migration (Semi-Auto)

```bash
# Migrates existing files using classification rules
bash .agent/scripts/migrate-to-umbrella.sh
```

**What it does**:

1. Scans all existing files
2. Applies classification_rules.yaml
3. Routes to PRIVATE/ or PUBLIC/
4. Encrypts PRIVATE/ content
5. Generates migration report

### Phase C: Operational (Fully Auto)

```bash
# From now on, everything is automatic:

# User creates file:
vim new_document.md

# File watcher detects → auto-classify.sh runs → routed automatically

# User commits:
git commit -m "Add device"

# Pre-commit hook runs → scans for secrets → allows/blocks automatically
```

---

## 🎯 SUCCESS CRITERIA

**We know automated secrecy works when**:

- ✅ User creates file → automatically routed (no manual decision)
- ✅ Zero secrets in PUBLIC/ (automated scanning prevents)
- ✅ PRIVATE/ encrypted (even if repo stolen, unreadable)
- ✅ Time tracking stays internal (dogfood FTW, never leaked)
- ✅ Any user can replicate (install script works on fresh machine)
- ✅ No FAANG extraction possible (zero-knowledge design)

---

*"Secrecy by default. Sharing by protocol. Automation forever."*

**Status**: DESIGNED v2.0 - Awaiting execution  
**Replicability**: 100% (any user can clone)  
**Security**: Zero-knowledge, zero-trust  
**Maintenance**: Fully automated, works "ad infinitum"
