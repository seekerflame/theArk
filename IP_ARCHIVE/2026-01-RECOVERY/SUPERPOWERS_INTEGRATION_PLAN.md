# 🦸 SUPERPOWERS INTEGRATION PLAN

**Source**: <https://github.com/obra/superpowers>  
**Author**: Jesse (obra)  
**Purpose**: Adopt obra's agentic skills framework for device development  
**Status**: PLANNING ONLY - awaiting user approval to install

---

## 📊 WHAT IS SUPERPOWERS?

**Definition**: An agentic skills framework & software development methodology

**Core Philosophy**:

- **Test-Driven Development** - Write tests first, always
- **Systematic over ad-hoc** - Process over guessing
- **Complexity reduction** - Simplicity as primary goal
- **Evidence over claims** - Verify before declaring success

**Key Innovation**: Skills activate **automatically** based on context, not manual invocation

---

## 🎯 THE 7-STEP WORKFLOW

### 1. `brainstorming`

**Triggers**: Before writing code  
**Does**: Socratic questioning to refine rough ideas into clear spec  
**Our Use**: Design new Practical Freedom Devices (Pip-Boy, Mesh Router, etc.)

### 2. `using-git-worktrees`

**Triggers**: After design approval  
**Does**: Creates isolated workspace on new branch  
**Our Use**: Prototype device variations without polluting main branch

### 3. `writing-plans`

**Triggers**: With approved design  
**Does**: Breaks work into 2-5 minute tasks with exact file paths, code, verification  
**Our Use**: Device build instructions (BOM → CAD → Assembly → Testing)

### 4. `subagent-driven-development` or `executing-plans`

**Triggers**: With plan ready  
**Does**: Dispatches fresh subagent per task with two-stage review  
**Our Use**: Parallel development of multiple devices (e.g., all Tier 1 simultaneously)

### 5. `test-driven-development`

**Triggers**: During implementation  
**Does**: RED-GREEN-REFACTOR cycle (failing test → minimal code → passing test → commit)  
**Our Use**: Hardware verification (does solar station actually charge? does mesh router connect?)

### 6. `requesting-code-review`

**Triggers**: Between tasks  
**Does**: Reviews against plan, reports issues by severity  
**Our Use**: Quality check before releasing device BOM/CAD to public

### 7. `finishing-a-development-branch`

**Triggers**: When tasks complete  
**Does**: Verifies tests, presents merge/PR options  
**Our Use**: Finalize device design, merge to main, publish to GitHub

---

## 🛠️ ADDITIONAL SUPERPOWERS

### Debugging

- **`systematic-debugging`** - 4-phase root cause process  
  **Our Use**: When device build fails (e.g., solar station not charging)

- **`verification-before-completion`** - Ensure it's actually fixed  
  **Our Use**: CoVe protocol for hardware (test BEFORE declaring "done")

### Collaboration

- **`dispatching-parallel-agents`** - Concurrent subagent workflows  
  **Our Use**: Build multiple device tiers simultaneously

### Meta

- **`writing-skills`** - Create new skills following best practices  
  **Our Use**: Create device-specific skills (e.g., `designing-mesh-routers`, `calculating-solar-bom`)

---

## 🔗 INTEGRATION WITH EXISTING WORKFLOWS

### Our Current State

**.agent/skills/**:

- We already have skills framework
- Custom skills for context compression, IP retrieval, ledger sentinel

**.agent/workflows/**:

- `/cove` - Chain of Verification
- `/gpm` - Global Problem-solving Method
- `/elephant_analysis` - Threat analysis
- `/overclocked` - High-velocity execution

**CHRONICLE/**:

- VICTORY_LOG.md, FAILURE_LOG.md
- GPM patterns, CoVe enforcement

### How Superpowers Enhances This

| Current Workflow | Superpowers Skill | Synergy |
|------------------|-------------------|---------|
| `/cove` (CoVe) | `verification-before-completion` | Both enforce "test before done" |
| `/gpm` | `systematic-debugging` | Both use 4-phase root cause analysis |
| `/elephant_analysis` | `brainstorming` | Both identify risks before building |
| GPM → Plan → Execute | `writing-plans` → `subagent-driven-development` | Same pattern! |
| Manual git commits | `using-git-worktrees` + `finishing-a-development-branch` | Automated branch management |

**Conclusion**: Superpowers **formalizes** what we already do ad-hoc.

---

## 📦 INSTALLATION PLAN (Awaiting Approval)

### Step 1: Clone Repo

```bash
cd ~/Documents/GitHub
git clone https://github.com/obra/superpowers.git
cd superpowers
```

### Step 2: Audit Skills

Review each skill in `skills/` directory:

- `brainstorming/SKILL.md`
- `test-driven-development/SKILL.md`
- `subagent-driven-development/SKILL.md`
- `systematic-debugging/SKILL.md`
- etc.

**Check for**:

- Conflicts with existing `.agent/skills/`
- Telemetry or phone-home (per user request: "remove all telemetry")
- Compatibility with our workflow

### Step 3: Integration Strategy

**Option A**: Install via plugin (if using Claude Code)

```bash
/plugin marketplace add obra/superpowers
/plugin install superpowers
```

**Option B**: Manual integration (if not using Claude Code)

```bash
cp -r ~/Documents/GitHub/superpowers/skills/* /Users/eternalflame/.agent/skills/
```

**Option C**: Selective adoption

- Cherry-pick only the skills we need
- Adapt their format to match our existing structure

### Step 4: Testing

Before using on real devices:

1. Test on a dummy project (e.g., "Hello World" device)
2. Verify skills auto-activate correctly
3. Check git worktree flow
4. Ensure no conflicts with GAIA Protocol or CoVe

### Step 5: Documentation

Update our workflows:

- `/cove` → Mention `verification-before-completion` skill
- `/gpm` → Mention `systematic-debugging` skill
- CHRONICLE/ → Document superpowers adoption in VICTORY_LOG

---

## 🎯 USE CASES FOR ARK OS

### Use Case 1: Building Pip-Boy Dashboard

**Current Approach**:

1. User says "build Pip-Boy"
2. I create files ad-hoc
3. Maybe test, maybe not
4. Commit everything at once

**With Superpowers**:

1. **brainstorming**: Clarify spec (wrist-worn? PWA? AT integration?)
2. **using-git-worktrees**: Create `device/pip-boy` branch
3. **writing-plans**: Break into tasks:
   - Task 1: HTML structure (2 min)
   - Task 2: AT ledger integration (5 min)
   - Task 3: Mesh network stub (3 min)
   - Task 4: Offline PWA manifest (2 min)
4. **test-driven-development**: Write test for each feature FIRST
5. **subagent-driven-development**: Dispatch agents for each task
6. **requesting-code-review**: Verify against plan
7. **finishing-a-development-branch**: Merge when verified

**Result**: Higher quality, less rework, faster iteration

### Use Case 2: Debugging Solar Station Charging Failure

**Current Approach**:

1. User says "solar station not charging"
2. I guess at causes
3. Try random fixes
4. Hope one works

**With Superpowers**:

1. **systematic-debugging**:
   - Phase 1: Reproduce (can we make it fail consistently?)
   - Phase 2: Isolate (is it battery, panel, controller, or wiring?)
   - Phase 3: Root cause (trace signal flow, find break)
   - Phase 4: Fix + verify
2. **verification-before-completion**: Test BEFORE saying "fixed"

**Result**: Fewer repeat failures, better documentation

### Use Case 3: Parallel Device Development (All Tier 1)

**Current Approach**:

1. Build Pip-Boy
2. Wait until done
3. Build Sovereign TV
4. Wait until done
5. etc. (sequential)

**With Superpowers**:

1. **brainstorming**: Design all 4 devices (Pip-Boy, TV, Router, Camera)
2. **writing-plans**: Create 4 separate plans
3. **dispatching-parallel-agents**: Launch 4 subagents simultaneously
4. **requesting-code-review**: Review each independently
5. **finishing-a-development-branch**: Merge all when ready

**Result**: 4× faster (or more with parallelism)

---

## ⚠️ POTENTIAL CONFLICTS

### Conflict 1: Task Boundaries

**Issue**: Superpowers wants to trigger automatically, but we have mandatory `task_boundary` calls

**Resolution**:

- Superpowers skills should call `task_boundary` internally
- OR we modify our task_boundary requirement to allow skill-triggered boundaries

### Conflict 2: Git Workflow

**Issue**: We currently commit manually, superpowers automates git

**Resolution**:

- Let superpowers manage feature branches
- We still manually commit to main for final releases

### Conflict 3: Testing

**Issue**: Superpowers is software-focused, our devices are hardware

**Resolution**:

- Adapt TDD for hardware (e.g., "test" = verify BOM totals, CAD renders, assembly steps)
- Software components (PWA, firmware) use traditional TDD

---

## 🚀 ROLLOUT PLAN

### Week 1: Research & Audit (CURRENT)

- [x] Understand superpowers philosophy
- [x] Map to existing workflows
- [ ] Clone repo
- [ ] Review all skills for telemetry
- [ ] Identify conflicts

### Week 2: Pilot Test

- [ ] Install on test project
- [ ] Build "Hello Device" (minimal hardware project)
- [ ] Verify auto-activation works
- [ ] Document lessons in VICTORY_LOG

### Week 3: Soft Launch

- [ ] Use for Pip-Boy development
- [ ] Track time saved vs old method
- [ ] Refine our skills to match superpowers format

### Week 4: Full Adoption

- [ ] Apply to all device development
- [ ] Train user on new workflow
- [ ] Update GAIA Protocol with superpowers integration

---

## 📊 SUCCESS METRICS

**We'll know superpowers is working when**:

- ✅ Fewer "I thought I tested that" failures
- ✅ Faster device prototyping (measured in hours, not days)
- ✅ Clean git history (atomic commits per task)
- ✅ Higher quality BOM files (tested before release)
- ✅ Parallel device development actually works
- ✅ Systematic debugging replaces random guessing

**If any metric fails**: Revert to manual workflow for that device, iterate on integration

---

## 🔒 PRIVACY & TELEMETRY

**User Request**: "Remove all telemetry"

**Audit Plan**:

1. Search superpowers repo for:
   - `analytics`, `telemetry`, `track`, `phone-home`
   - API calls to external services
   - Usage reporting
2. If found → Remove before installation
3. If not found → Proceed

**Preliminary Assessment** (from README):

- MIT License (open source, good sign)
- No mention of analytics in philosophy
- Likely clean, but MUST verify

---

## 🎯 IMMEDIATE NEXT STEPS (Awaiting User Approval)

1. **User reviews this plan**
2. **User says "go" or "wait"**
3. **If "go"**:
   - Clone repo
   - Audit for telemetry
   - Install selective skills
   - Test on dummy project
4. **If "wait"**:
   - Continue with manual workflow
   - Revisit when time permits

---

*"Superpowers turns ad-hoc genius into systematic excellence."*

**Status**: AWAITING USER APPROVAL  
**Risk**: Low (can always uninstall)  
**Reward**: High (10× faster device development)  
**Recommendation**: Proceed with pilot test on non-critical device
