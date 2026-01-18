# [CRITICAL] Order Ahead Navigation Bug

**Date Reported**: 2026-01-17
**Reporter**: ETERNAL FLAME (from Rudy Raid testing)
**Affected Systems**: [Frontend/Order Ahead Chassis]
**User Impact**: Critical - Breaks user flow

## Symptom

Navigation between Order Ahead views fails. Clicking menu items or order button causes JavaScript error and prevents progression through order flow.

## Root Cause

Typo in method name: `this.showView` should be `this.switchView`

**Technical Details**:

- File: `web/app.js` or Order Ahead chassis file
- Error: `TypeError: this.showView is not a function`
- Correct method name: `this.switchView`

## Reproduction Steps

1. Navigate to Order Ahead interface (Rudy's Hotdogs)
2. Click on menu item
3. Console shows: `TypeError: this.showView is not a function`
4. User stuck, cannot proceed to checkout

## Expected Behavior

Smooth navigation through:

1. Discovery (merchant list)
2. Menu (item selection)
3. Order (customization)
4. Confirmation (QR code)
5. Pickup (verification)

## Proposed Fix

Search and replace in affected files:

```javascript
// WRONG
this.showView('menu');

// CORRECT
this.switchView('menu');
```

**Files to check**:

- `web/app.js`
- Any Order Ahead specific UI files
- Merchant interface files

## Dependencies

None. Simple find/replace.

## Verification

1. Apply fix
2. Test complete Order Ahead flow:
   - Select merchant
   - View menu
   - Add items
   - Customize
   - Place order
   - View confirmation
   - Complete pickup
3. Check console for errors
4. Verify smooth transitions

**Success Criteria**: Complete order flow without errors.

---

**Priority**: CRITICAL - Blocks Order Ahead MVP deployment
**Source**: [Rudy Raid walkthrough](file:///Users/eternalflame/.gemini/antigravity/brain/36088604-e288-4e07-95fb-f7f13f6b4ef6/walkthrough.md)
**Impact**: "Rudy Raid" cannot launch until fixed
