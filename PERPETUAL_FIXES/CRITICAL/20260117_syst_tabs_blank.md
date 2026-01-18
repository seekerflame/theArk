# [CRITICAL] SYST Tabs Not Rendering

**Date Reported**: 2026-01-17
**Reporter**: ETERNAL FLAME / Antigravity
**Affected Systems**: [Frontend/UI]
**User Impact**: High - Core features inaccessible

## Symptom

When user clicks on SYST section tabs (LIFE, FOCUS, ADMIN), the tab appears selected but the content area remains blank. No error messages in console.

## Root Cause

Modules load successfully but `render()` function never called during initialization. The tab routing exists but the initialization sequence is incomplete.

**Technical Details**:

- Modules exist: `web/lifeline.js`, `web/components/focus.js`, `web/admin_deck.js`
- Backend APIs functional: `api/lifeline.py`, `api/system.py`
- UI entry points defined in `app.js`
- **Missing**: Explicit `render()` calls in module initialization chain

## Reproduction Steps

1. Navigate to `http://localhost:8080`
2. Click "SYST" in main navigation
3. Click "LIFE", "FOCUS", or "ADMIN" sub-tabs
4. Observe: Tab highlights but content area stays blank

## Expected Behavior

Content should immediately render when tab is selected:

- **LIFE**: Lifeline dashboard with memories/favors/tasks
- **FOCUS**: Focus timer and productivity tools
- **ADMIN**: System administration panel

## Proposed Fix

Update [`app.js`](file:///Users/eternalflame/Documents/GitHub/theArk/web/app.js):

```javascript
// In switchView() function, add explicit render calls
case 'LIFE':
    if (window.lifelineUI) {
        window.lifelineUI.render(); // ← ADD THIS
    }
    break;
case 'FOCUS':
    if (window.focusUI) {
        window.focusUI.render(); // ← ADD THIS
    }
    break;
case 'ADMIN':
    if (window.adminDeck) {
        window.adminDeck.render(); // ← ADD THIS
    }
    break;
```

## Dependencies

None. This is a self-contained frontend fix.

Related issue: DATA tabs have same problem (see [20260117_data_tabs_blank.md](file:///Users/eternalflame/Documents/GitHub/theArk/PERPETUAL_FIXES/CRITICAL/20260117_data_tabs_blank.md))

## Verification

1. Apply fix to `app.js`
2. Restart server: `./ark_start.sh`
3. Navigate to each SYST tab
4. Verify content renders immediately
5. Check browser console for errors
6. Test tab switching (no memory leaks)

**Success Criteria**: All 3 SYST tabs render content on first click.

---

**From**: [`MASTER_ARCHITECTURE.md`](file:///Users/eternalflame/Documents/GitHub/theArk/IP_ARCHIVE/2026-01-RECOVERY/MASTER_ARCHITECTURE.md) - Day 1 fix priority
