---
description: Chain of Verification for Ark Workshop - Solo Mode XP Integration
---

# CoVe Workflow for Ark Workshop

**Purpose**: Enforce verification-before-completion with XP rewards for validated work

**Integration**: Ark Workshop tracks all tool usage → CoVe verifies → XP awarded

---

## Core Principle

**TEST BEFORE DONE** - No story marked complete until verified working

From Vibecraft standards:

- Character states trigger on verified actions
- Station pulses only on successful tool completion
- Notifications show proof of work

---

## CoVe Steps for Each Story

### 1. READ (Context Gathering)

- Tool: Read file, view code
- Verification: Can you explain purpose?
- XP: +5 XP per critical file understood
- Workshop: Agent moves to "Bookshelf" station

### 2. WRITE (Code Creation)

- Tool: Write new file
- Verification: Does it compile/run?
- XP: +25 XP per working file
- Workshop: Agent at "Desk" station, working animation

### 3. EDIT (Code Modification)

- Tool: Replace/multi-replace
- Verification: Did it fix the issue? Tests pass?
- XP: +15 XP per successful fix
- Workshop: Agent at "Workbench", tool animations

### 4. TEST (Verification)

- Tool: Run command, check output
- Verification: Does it actually work?
- XP: +50 XP for passing tests
- Workshop: Agent moves to "Scanner" station

### 5. COMMIT (Proof of Work)

- Tool: Git commit
- Verification: Clean git history, descriptive message
- XP: +10 XP per commit
- Workshop: Celebration animation (zone pulse)

---

## XP Tiers (Ark Workshop Integration)

### Tier 1: Basic Actions (Auto-Award)

- Read file: +5 XP
- Write file (no test): +10 XP
- Edit file: +10 XP
- Git status check: +2 XP

### Tier 2: Verified Actions (CoVe Required)

- Write + Test passing: +25 XP
- Edit + Bug fixed: +20 XP
- Commit with proof: +15 XP
- Full story complete: +50 XP

### Tier 3: Breakthroughs (Manual Award)

- Feature complete + tested: +100 XP
- Major bug fix: +75 XP
- System integration working: +150 XP
- Level up achievement: +500 XP

---

## Ark Workshop CoVe Flow

```typescript
// User triggers action
claudeCode.readFile('workspace.js')

// Ark Workshop receives event
arkWorkshop.onToolUse({
  agent: 'antigravity',
  tool: 'Read',
  target: 'workspace.js'
})

// CoVe check (automatic for basic, manual for verified)
if (tool === 'Read') {
  // Auto-award basic XP
  arkWorkshop.addXP(5, 'Read workspace.js')
  workspace.moveAgent('antigravity', 'bookshelf')
}

if (tool === 'Write' && hasTest) {
  // Wait for test verification
  onTestPass(() => {
    arkWorkshop.addXP(25, 'Write + test passing')
    workspace.stationPulse('desk')
    workspace.celebrateSuccess('antigravity')
  })
}
```

---

## Story Completion Checklist (RALPH + CoVe)

**Story is NOT complete until ALL verified**:

- [ ] Acceptance criteria met
- [ ] Code compiles/runs
- [ ] Tests written (if applicable)
- [ ] Tests passing
- [ ] Git committed with clear message
- [ ] Documented in progress.txt
- [ ] XP awarded
- [ ] Ark Workshop shows completion animation

**Only then**: Mark `passes: true` in prd.json

---

## Current Quest: Ark Workshop MVP

### Story 001: ✅ VERIFIED

- [x] Folder structure created
- [x] package.json configured
- [x] npm install successful
- [x] Git initialized
- **XP Awarded**: +50 XP

### Story 002: ✅ VERIFIED  

- [x] Hexagonal grid renders
- [x] 3 agent zones visible
- [x] 5 workstations placed
- [x] OrbitControls smooth (60fps)
- [x] Cyberpunk aesthetic confirmed
- **XP Awarded**: +75 XP (visual excellence)

### Story 003: ✅ VERIFIED

- [x] WebSocket server on port 4004
- [x] Client connects successfully
- [x] Bidirectional sync working
- [x] XP reads/writes QUEST_PROGRESS.md
- [x] Session recording functional
- **XP Awarded**: +100 XP (system integration)

**Total XP This Session**: 225 XP
**Current Level**: 2 (650 + 225 = 875/800) → **Level 3!**

---

## Next Stories (CoVe Required)

### Story 004: Activity Feed UI

**Verification Needed**:

- [ ] Feed updates in real-time
- [ ] Filters work (All, Antigravity, Business-OS, User)
- [ ] File paths shortened correctly
- [ ] Timestamps accurate
- [ ] Scrolling smooth

**XP on Complete**: +50 XP

### Story 005: Claude Code Hooks

**Verification Needed**:

- [ ] Hook script executable
- [ ] Parses tool events correctly
- [ ] Sends to WebSocket
- [ ] Triggers workspace animations
- [ ] No crashes/errors

**XP on Complete**: +75 XP

### Story 006: Agent Animations

**Verification Needed**:

- [ ] Character moves smoothly
- [ ] States trigger correctly (idle/walking/working/thinking)
- [ ] Thought bubbles animate
- [ ] Status ring changes color
- [ ] Performance: 60fps maintained

**XP on Complete**: +100 XP (high complexity)

---

## CoVe + RALPH Integration

**RALPH provides structure** (10 stories, acceptance criteria)  
**CoVe provides verification** (test before done)  
**Ark Workshop provides feedback** (XP, animations, celebrations)

**Combined**: Tight iteration loop with proof of work

---

## Level-Up Celebrations (Ark Workshop)

When XP crosses threshold → Level up:

1. **All zones flash** (3× pulse)
2. **Notification**: "🎉 LEVEL 3 ACHIEVED!"
3. **Activity feed**: System message with XP breakdown
4. **Sound**: Celebratory chime
5. **VICTORY_LOG.md**: Auto-append entry
6. **Quest overlay**: Updates to new level

---

**Status**: CoVe workflow active, integrated with Ark Workshop
**Current Level**: 3 (75/1200 XP to Level 4)
**Next Milestone**: Story 004 complete (+50 XP)
