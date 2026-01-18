# [CRITICAL] DATA Tabs Not Rendering

**Date Reported**: 2026-01-17
**Reporter**: ETERNAL FLAME / Antigravity
**Affected Systems**: [Frontend/UI]
**User Impact**: High - Core data features inaccessible

## Symptom

When user clicks on DATA section tabs (ACADEMY, LEDGER), the tab appears selected but content area remains blank.

## Root Cause

Same as SYST tabs issue - routing exists but no initialization. Modules load but `render()` never called.

**Technical Details**:

- Modules exist: `web/academy_ui.js`, `web/explorer_ui.js`
- Backend APIs functional: `api/academy.py`, `api/graph.py`
- **Missing**: Explicit `render()` calls

## Reproduction Steps

1. Navigate to `http://localhost:8080`
2. Click "DATA" in main navigation
3. Click "ACADEMY" or "LEDGER" sub-tabs
4. Observe: Blank content area

## Expected Behavior

- **ACADEMY**: OSE Academy learn-to-earn interface
- **LEDGER**: Transaction explorer and DAG visualization

## Proposed Fix

Update [`app.js`](file:///Users/eternalflame/Documents/GitHub/theArk/web/app.js):

```javascript
case 'ACADEMY':
    if (window.academyUI) {
        window.academyUI.render();
    }
    break;
case 'LEDGER':
    if (window.explorerUI) {
        window.explorerUI.render();
    }
    break;
```

## Dependencies

None. Apply same fix pattern as SYST tabs.

## Verification

Same verification process as SYST tabs fix.

---

**Batch Fix**: Can be fixed simultaneously with SYST tabs issue.
