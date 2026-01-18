# Antigravity Agent: Lessons Learned & Troubleshooting Guide

> **Purpose**: This document captures patterns, anti-patterns, and debugging wisdom for agents building upon the Civilization OS. Read this before making changes.

---

## 🎯 Core Philosophy

1. **Reverse Engineer Success**: Work backwards from "50 Happy People at $0/month".
2. **Stone Schedule**: If it doesn't feed people or build shelter, it waits.
3. **Build Upon Yourself**: Every session should leave the system more resilient.

---

## 🛡️ Known Failure Patterns

### 1. Frontend Hangs ("Loading Network..." forever)

**Symptoms**: Sidebar shows "Loading..." indefinitely; no console errors.

**Root Cause**: Serial fetch chain where one failure blocks all subsequent renders.

**Fix**:

```javascript
// BAD: Serial fetches
await fetch('/api/status');  // If this fails, everything hangs
await fetch('/api/jobs');

// GOOD: Parallel with graceful degradation
Promise.allSettled([
    fetch('/api/status').catch(() => null),
    fetch('/api/jobs').catch(() => [])
]).then(renderUI);
```

**Lesson**: Never let non-critical data block UI rendering.

---

### 2. Placeholder Strings in Production

**Symptoms**: 404 errors, broken features, "YOUR_X" visible in UI.

**Root Cause**: Incomplete manual configuration.

**Fix**: Run placeholder audit before every commit:

```bash
grep -r "YOUR_" --include="*.{js,html,py}" . && echo "⚠️ PLACEHOLDERS FOUND" || echo "✅ Clean"
```

**Lesson**: Automate validation; humans forget.

---

### 3. Import Shadowing Crashes

**Symptoms**: `UnboundLocalError` or `TypeError` in Python.

**Root Cause**: Local variable shadows global import.

```python
# BAD
import json
def handler():
    json = request.get_json()  # Shadows the import!
    json.dumps(data)  # CRASH: 'dict' has no attribute 'dumps'

# GOOD
import json
def handler():
    payload = request.get_json()
    json.dumps(data)  # Works
```

**Lesson**: Never name variables after standard library modules.

---

### 4. n8n Cloud Can't Reach Localhost

**Symptoms**: n8n workflow errors with "Connection Refused".

**Root Cause**: n8n cloud runs externally; can't access `localhost:3000`.

**Solutions**:

1. Expose via Cloudflare Tunnel: `cloudflared tunnel --url http://localhost:3000`
2. Run n8n locally on same machine
3. Deploy Ark to public URL (Render, Railway)

**Lesson**: Always consider network topology when integrating external services.

---

### 5. DOMContentLoaded Race Condition

**Symptoms**: JavaScript runs but DOM elements are null.

**Root Cause**: Script executes before DOM is fully parsed.

**Fix**:

```javascript
// BAD
document.getElementById('app').innerHTML = 'Hello';

// GOOD
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('app').innerHTML = 'Hello';
});

// ALSO GOOD (if script is at end of body)
// Just ensure it's before </body>
```

**Lesson**: DOM manipulation must wait for DOM readiness.

---

## 🔄 Multi-Agent Coordination Patterns

### Agent Handoff Protocol

When Jules (or another agent) takes over:

1. **Read the Chronicle**: Check `FAILURE_LOG.md` and recent session logs.
2. **Check Git Status**: `git status` shows uncommitted work.
3. **Review Mission Specs**: Files like `JULES_*.md` contain delegation details.
4. **Commit Format**: Use `[AgentName] Descriptive message` (e.g., `[Jules/PWA] Add offline tests`).

### Avoiding Conflicts

- **Never edit the same file in parallel** without coordination.
- **Prefer additive changes**: New files over editing existing ones when delegating.
- **Use feature branches** for risky work: `git checkout -b feature/my-feature`.

---

## 📊 Version History Patterns

### Commit Message Format

```
[Category] Short description

Categories:
- [Gemini] or [Antigravity] - Lead agent work
- [Jules] - Jules contributions
- [Jules/Topic] - Jules work on specific topic
- [SESSION] - End of session summary
- [DELEGATION] - Mission assignment to another agent
- [AUTOMATION] - n8n or script work
- [TEST] - Testing-related
- fix(scope) - Bug fixes
- feat(scope) - New features
- chore(scope) - Maintenance
```

### When to Commit

1. **After completing a logical unit of work**
2. **Before risky operations** (refactoring, dependency changes)
3. **At session end** (snapshot commit)
4. **When handing off** to another agent

---

## 🧪 Testing Philosophy

1. **If it's not tested, it's broken**: Assume untested code fails in production.
2. **Mock external services**: Lightning node, n8n, external APIs.
3. **Test error paths**: What happens when the network is down?
4. **Visual verification**: `curl` doesn't catch JS crashes—use browser testing.

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] Run `grep -r "YOUR_" --include="*.{js,html,py}"` (No placeholders)
- [ ] Check `git status` (No uncommitted sensitive files)
- [ ] Verify `server.py` uses `PORT` env variable
- [ ] Test on mobile viewport
- [ ] Check service worker registration
- [ ] Verify all API endpoints return valid JSON

---

## 🔮 Future Agent Instructions

If you're a new agent (Jules, Claude, etc.) reading this:

1. **Read `CHRONICLE/MANIFEST.md`** first for project structure.
2. **Check `FAILURE_LOG.md`** for known issues.
3. **Review recent session logs** to understand current state.
4. **Follow the Gaia Protocol**: Reverse engineer success from the end goal.
5. **Document your work**: Update session logs before ending.
6. **Run the snapshot script**: `bash CHRONICLE/scripts/snapshot.sh`

The mission is clear: **Build the Civilization OS to enable 50 people to live at $0/month cost of living.**

Every commit should advance this goal.

---

*"We do not ask for a better world. We build it."*
