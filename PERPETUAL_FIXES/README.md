# 🔧 PERPETUAL FIXES - Bug & Technical Debt Tracker

> **Philosophy**: "We do not ignore the cracks. We catalog them, prioritize them, and eliminate them systematically."

---

## 📁 DIRECTORY STRUCTURE

```
PERPETUAL_FIXES/
├── CRITICAL/     # System-breaking, blocks core functionality
├── HIGH/         # Major features broken, bad UX
├── MEDIUM/       # Minor issues, workarounds exist
├── LOW/          # Polish, nice-to-haves
└── README.md     # This file
```

---

## 🎯 PRIORITIZATION GUIDELINES

### 🔴 CRITICAL

**Criteria**: Breaks core user flow, prevents revenue, data loss risk
**Examples**:

- Server crashes
- Payment processing failures
- Data corruption
- Authentication broken
- API endpoints returning 500

**SLA**: Fix within 24 hours

### 🟡 HIGH

**Criteria**: Major feature degraded, poor UX, blocks secondary flows
**Examples**:

- UI tabs not rendering
- Missing feedback on actions
- Performance issues (>3s load)
- Mobile responsiveness broken

**SLA**: Fix within 1 week

### 🟠 MEDIUM

**Criteria**: Minor UX issues, cosmetic bugs, feature gaps
**Examples**:

- Inconsistent styling
- Missing tooltips
- Suboptimal workflows
- Missing secondary features

**SLA**: Fix within 1 month

### 🟢 LOW

**Criteria**: Polish, optimizations, future enhancements
**Examples**:

- Animation improvements
- Keyboard shortcuts
- Dark mode polish
- Accessibility enhancements

**SLA**: Backlog (no deadline)

---

## 📝 BUG REPORT FORMAT

Each bug gets its own `.md` file named: `YYYYMMDD_short_description.md`

**Template**:

```markdown
# [PRIORITY] Bug Title

**Date Reported**: YYYY-MM-DD
**Reporter**: Name/AI
**Affected Systems**: [Frontend/Backend/API/DB]
**User Impact**: [High/Medium/Low]

## Symptom
What the user experiences.

## Root Cause
Technical explanation (if known).

## Reproduction Steps
1. Step one
2. Step two
3. Observe bug

## Expected Behavior
What should happen.

## Proposed Fix
How to resolve it.

## Dependencies
Any blockers or related issues.

## Verification
How to test the fix.
```

---

## 🔄 WORKFLOW

### Adding a Bug

1. Create `.md` file in appropriate priority folder
2. Use date prefix: `20260117_mint_no_feedback.md`
3. Fill out template completely
4. Link related files/code with file:// links

### Fixing a Bug

1. Move file to `PERPETUAL_FIXES/RESOLVED/YYYYMM/`
2. Add resolution note at bottom
3. Commit fix with reference: `fix: MINT feedback (resolves 20260117_mint_no_feedback)`
4. Update VICTORY_LOG.md with lesson learned

### Escalating Priority

1. Rename file with new priority folder
2. Update bug report with escalation reason
3. Notify team/adjust sprint plan

---

## 📊 CURRENT BUG COUNT

**CRITICAL**: 3 bugs
**HIGH**: 2 bugs
**MEDIUM**: 0 bugs
**LOW**: 0 bugs

**Total Technical Debt**: 5 issues

---

## 🎯 NEXT SPRINT TARGETS

Focus: Clear all CRITICAL bugs before new feature work.

**Target**: 0 CRITICAL, <3 HIGH by end of week.

---

## 📖 LESSONS

### From Past Bugs

- UI initialization race conditions → Use explicit render() calls
- Missing user feedback → Always show loading/success/error states
- Data sanitization → Never trust Chassis inputs to Engine

### Prevention Strategies

- CoVe verification before deployment
- Test actual user flows, not just unit tests
- Visual verification with screenshots/videos

---

*"Bugs are not failures. They are lessons waiting to be learned."*

**Status**: ACTIVE ✅  
**Last Updated**: 2026-01-17
