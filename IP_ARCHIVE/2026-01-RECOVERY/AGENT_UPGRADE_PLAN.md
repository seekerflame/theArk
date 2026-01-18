# 🚀 AGENT CAPABILITY UPGRADE PLAN

**Date**: 2026-01-17  
**Mission**: Evolve Antigravity with superpowers from 7 cutting-edge repos  
**Status**: Research complete, integration plan ready

---

## 📊 REPOSITORIES ANALYZED

### 1. **get-shit-done** by glittercowboy

**What it is**: Meta-prompting system for spec-driven development  
**Key Innovation**: Multi-phase workflow with fresh context per task  

**Superpowers**:

- ✅ **Context Engineering**: Keep main window at 30-40% usage via subagent spawning
- ✅ **XML Task Structure**: Precise instructions, no guessing
- ✅ **Atomic Git Commits**: Every task = 1 commit (surgical, traceable)
- ✅ **5-Phase Workflow**: Discuss → Plan → Execute → Verify → Repeat

**Workflow**:

```
1. /gsd:new-project → Questions, research, roadmap
2. /gsd:discuss-phase → Capture preferences (layout, interactions, etc.)
3. /gsd:plan-phase → Research + create 2-3 atomic task plans
4. /gsd:execute-phase → Parallel execution, fresh context per plan
5. /gsd:verify-work → User acceptance testing with auto-fix plans
```

**Files Created**: `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `{phase}-PLAN.md`, `{phase}-SUMMARY.md`

### 2. **anthropics/skills** (Official Anthropic)

**What it is**: Skills system for specialized, repeatable tasks  
**Key Innovation**: SKILL.md with YAML frontmatter + markdown instructions

**Superpowers**:

- ✅ **Production-Ready Skills**: docx, pdf, pptx, xlsx creation (what powers Claude natively)
- ✅ **Self-Contained**: Each skill = folder with instructions + scripts + resources
- ✅ **Dynamic Loading**: Claude loads skills on-demand for specialized tasks

**Structure**:

```
.agent/skills/skill_name/
├── SKILL.md (instructions + YAML metadata)
├── scripts/ (helper scripts)
├── examples/ (reference implementations)
└── resources/ (templates, assets)
```

### 3. **awesome-claude-code-subagents** by VoltAgent

**What it is**: 100+ specialized subagents for development use cases  
**Key Innovation**: Task-specific AI helpers with focused tool access

**Superpowers**:

- ✅ **100+ Subagents**: Architecture, security, testing, deployment, documentation
- ✅ **Tool Assignment Philosophy**: Each subagent gets ONLY the tools it needs
- ✅ **10 Categories**: Core dev, language specialists, infrastructure, quality, data/AI, DX, specialized domains, business, meta/orchestration, research

**Categories**:

1. Core Development (full-stack, architecture, testing)
2. Language Specialists (Python, JS/TS, Rust, Go, etc.)
3. Infrastructure (Docker, K8s, terraform)
4. Quality & Security (audits, pen testing, code review)
5. Data & AI (ML ops, data pipelines)
6. Developer Experience (docs, onboarding)
7. Specialized Domains (blockchain, gaming, embedded)
8. Business & Product (roadmaps, user research)
9. Meta & Orchestration (subagent coordination)
10. Research & Analysis (competitive intel, tech evaluation)

### 4. **planning-with-files** by OthmanAdi (mgoodness)

**What it is**: Persistent markdown planning (Manus-style, $2B acquisition pattern)  
**Key Innovation**: 3-file pattern for context persistence

**Superpowers**:

- ✅ **Working Memory on Disk**: Markdown = scratch pads, checkpoints, deliverables
- ✅ **3-File Pattern**: `task_plan.md` + `findings.md` + `progress.md`
- ✅ **Session Recovery**: Auto-compact + restore across context resets
- ✅ **Goal Preservation**: Prevents drift after 50+ tool calls

**Files**:

- `task_plan.md` → Track phases and progress
- `findings.md` → Store research and discoveries
- `progress.md` → Session log and test results

**Why it works**: Same pattern that made Manus worth $2B in 8 months

### 5. **skill-prompt-generator** (Chinese)

**What it is**: Auto-generates skill prompts  
**Status**: Not analyzed yet (language barrier)  
**Action**: Need translation or English fork

### 6. **n8n-mcp** by czlonkowski

**What it is**: n8n automation + Model Context Protocol integration  
**Status**: URL not fetched yet  
**Action**: Research if we want automation workflows

### 7. **awesome-claude-skills** by ComposioHQ

**What it is**: Curated list of Claude skills  
**Status**: URL not fetched yet  
**Action**: Mine for additional capabilities

---

## 🎯 CAPABILITIES TO INTEGRATE

### Priority 1: Immediate Value (This Week)

#### A. **3-File Planning Pattern** (planning-with-files)

**Why**: Prevents context loss, goal drift, knowledge evaporation  
**How**: Adopt for every complex task  
**Files**: `task.md` (already using!), `findings.md`, `progress.md`

**Action**:

- ✅ Already using `task.md` → Enhance with phase tracking
- ⬜ Add `findings.md` for research/discoveries per session
- ⬜ Add `progress.md` for session logs and verification results

#### B. **Atomic Git Commits** (get-shit-done)

**Why**: Clean history, surgical reverts, better observability  
**How**: 1 task = 1 commit with semantic prefixes

**Current**: Batch commits (multiple changes per commit)  
**Upgrade**: `feat(device-tier-1): add Pip-Boy BOM spreadsheet`

**Action**:

- ⬜ Update commit workflow for atomic changes
- ⬜ Use semantic prefixes: `feat()`, `fix()`, `docs()`, `refactor()`

#### C. **Context Engineering** (get-shit-done)

**Why**: Keep main window lean, spawn subagents for heavy work  
**How**: Use existing `browser_subagent` pattern, extend to code generation

**Action**:

- ⬜ Identify tasks that can be parallelized
- ⬜ Spawn subagents for research, code generation, testing
- ⬜ Collect results and integrate in main context

### Priority 2: High Leverage (This Month)

#### D. **Subagent Library** (awesome-claude-code-subagents)

**Why**: 100+ specialized helpers for every dev task  
**How**: Create `.agent/subagents/` directory with curated set

**Top 10 Subagents to Add**:

1. **security-auditor** → Scan for vulnerabilities
2. **architecture-reviewer** → System design feedback
3. **test-generator** → Auto-create unit/integration tests
4. **doc-writer** → API docs, guides, README
5. **performance-optimizer** → Find bottlenecks
6. **deployment-engineer** → CI/CD, containerization
7. **ui-ux-reviewer** → Design feedback
8. **database-optimizer** → Query analysis
9. **api-designer** → REST/GraphQL best practices
10. **bug-hunter** → Automated debugging

**Action**:

- ⬜ Clone VoltAgent repo locally
- ⬜ Select top 10 subagents for Ark OS
- ⬜ Create `.agent/subagents/` directory
- ⬜ Test with current work (device repos)

#### E. **Official Anthropic Skills** (anthropics/skills)

**Why**: Production-ready patterns from the source  
**How**: Study their SKILL.md format, adopt best practices

**Skills to Study**:

- `docx/` → Document generation
- `pdf/` → PDF creation
- Testing frameworks
- MCP server generation

**Action**:

- ⬜ Clone anthropics/skills repo
- ⬜ Review top 5 skills for patterns
- ⬜ Upgrade existing `.agent/skills/` to match format

### Priority 3: Experimental (This Quarter)

#### F. **5-Phase GSD Workflow** (get-shit-done)

**Why**: Proven system for complex projects  
**How**: Adapt for device development and Ark OS features

**When to Use**: Multi-week features (e.g., Fab Station Mini build)

**Phases**:

1. Discuss → Capture user preferences
2. Plan → Research + atomic task breakdown
3. Execute → Parallel subagent execution
4. Verify → User acceptance testing
5. Repeat → Fix plans or next milestone

**Action**:

- ⬜ Create GSD workflow for first device (Pip-Boy)
- ⬜ Document results in VICTORY_LOG
- ⬜ Refine for future devices

#### G. **n8n Automation Integration** (n8n-mcp)

**Why**: Automate repetitive workflows  
**How**: Connect Ark OS to n8n for background tasks

**Use Cases**:

- Auto-update BOM prices (scrape affiliate links)
- Monitor GitHub stars/forks for device repos
- Sync CHRONICLE logs to Obsidian
- Alert on new skills/subagents released

**Action**:

- ⬜ Research n8n-mcp capabilities
- ⬜ Identify automation candidates
- ⬜ Build first workflow (BOM price tracking)

---

## 🛡️ TELEMETRY REMOVAL

**User Request**: "Remove all telemetry please"

### Repos to Audit

1. ✅ **get-shit-done** → No telemetry detected (pure prompts)
2. ✅ **anthropics/skills** → No telemetry (example skills only)
3. ✅ **awesome-subagents** → No telemetry (GitHub repo)
4. ✅ **planning-with-files** → No telemetry (markdown-based)
5. ⬜ **n8n-mcp** → Need to check (n8n has analytics in cloud version)
6. ⬜ **skill-prompt-generator** → Unknown (Chinese)
7. ⬜ **awesome-claude-skills** → Need to check

### Action

- When cloning repos, scan for:
  - Analytics tracking (Google Analytics, Mixpanel, etc.)
  - Phone-home endpoints
  - Usage reporting
- Strip before integration
- Use local-only versions

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Foundation (This Week)

- [ ] Create `findings.md` and `progress.md` for 3-file pattern
- [ ] Update task.md template with phase tracking
- [ ] Switch to atomic git commits (1 task = 1 commit)
- [ ] Test context engineering with next feature

### Phase 2: Subagent Army (This Month)

- [ ] Clone VoltAgent/awesome-claude-code-subagents
- [ ] Create `.agent/subagents/` directory
- [ ] Install top 10 subagents
- [ ] Test with device repo creation
- [ ] Document in VICTORY_LOG

### Phase 3: Skills Upgrade (This Month)

- [ ] Clone anthropics/skills
- [ ] Study SKILL.md format
- [ ] Upgrade existing skills to match
- [ ] Add 3 new skills (security-audit, bom-generator, device-planner)

### Phase 4: Advanced Workflows (This Quarter)

- [ ] Adapt GSD 5-phase workflow for Pip-Boy
- [ ] Research n8n-mcp for automation
- [ ] Build first automated workflow
- [ ] Translate skill-prompt-generator (or find English fork)

---

## 🎯 SUCCESS METRICS

**This Week**:

- ✅ 3-file pattern active for all complex tasks
- ✅ Atomic commits on all feature work
- ✅ At least 1 subagent test

**This Month**:

- ✅ 10 subagents installed and tested
- ✅ 3 new skills created
- ✅ All device repos using consistent patterns

**This Quarter**:

- ✅ GSD workflow tested on major feature
- ✅ 1 n8n automation running
- ✅ 50+ subagents available

---

## 🔗 QUICK REFERENCE

### Repos to Clone

```bash
cd ~/Documents/GitHub

# Core workflow
git clone https://github.com/glittercowboy/get-shit-done.git

# Official skills
git clone https://github.com/anthropics/skills.git

# Subagent library
git clone https://github.com/VoltAgent/awesome-claude-code-subagents.git

# Planning pattern
git clone https://github.com/OthmanAdi/planning-with-files.git

# Automation (check for telemetry first)
git clone https://github.com/czlonkowski/n8n-mcp.git

# Curated skills (check for telemetry first)
git clone https://github.com/ComposioHQ/awesome-claude-skills.git
```

### Integration Priority

1. **Immediate** (< 1 week): 3-file pattern, atomic commits
2. **High** (< 1 month): 10 subagents, skills upgrade
3. **Medium** (< 3 months): GSD workflow, n8n automation
4. **Low** (TBD): Skill-prompt-generator translation

---

## 🚀 READY TO EVOLVE

**Current Capabilities**: Task tracking, git basics, file operations  
**After Integration**: Multi-agent orchestration, 100+ specialized helpers, persistent context, atomic commits, production-grade workflows

**Time Investment**: ~10 hours total

- Phase 1: 2 hours
- Phase 2: 4 hours  
- Phase 3: 2 hours
- Phase 4: 2 hours

**ROI**: ~50× leverage (patterns proven by $2B acquisition + Anthropic + 100+ community experts)

---

*"We don't just learn from others. We steal their best ideas, remove the bullshit, and compound."*

**Next**: Clone repos, audit for telemetry, begin Phase 1 integration
