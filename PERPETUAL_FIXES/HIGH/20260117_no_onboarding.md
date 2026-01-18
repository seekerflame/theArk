# [HIGH] No Onboarding Flow

**Date Reported**: 2026-01-17
**Reporter**: ETERNAL FLAME / Antigravity
**Affected Systems**: [Frontend/UX]
**User Impact**: High - New users land on chaos

## Symptom

New users arrive at dashboard with no guidance. No welcoming flow, no explanation of features, no tutorial.

Result: Confusion, high bounce rate, poor first impression.

## Root Cause

No onboarding system implemented.

## Expected Behavior

New user experience should include:

1. **Welcome Screen**: "Welcome to The Ark / BORED"
2. **Choose Your Path**: 3 options (Join Event, Post Event, Browse Map)
3. **Quick Tutorial**: 30-60 second guided tour
4. **First Quest**: Guided mission to earn first AT
5. **Success**: Celebration + dashboard unlock

## Proposed Implementation

### Simple 5-Screen Flow

**Screen 1: Welcome**

- Logo
- "The only game where grinding actually matters"
- "Get Started" button

**Screen 2: What brings you here?**

- [ ] I want to find local events
- [ ] I want to host an event
- [ ] I want to explore the economy

**Screen 3: Quick Tour** (based on choice)

- 3-4 highlights specific to their path
- Skip button for experienced users

**Screen 4: Your First Quest**

- Simple task relevant to their path
- Immediate AT reward
- "Feels good!" moment

**Screen 5: You're Ready!**

- Unlock full dashboard
- Set user flag: `onboarding_complete = true`

### Technical Implementation

**File**: `web/onboarding_ui.js`

```javascript
class OnboardingFlow {
    constructor() {
        this.currentStep = 0;
        this.userChoice = null;
    }
    
    start() {
        if (this.isComplete()) return;
        this.showStep(0);
    }
    
    showStep(step) {
        // Render screen based on step
    }
    
    complete() {
        localStorage.setItem('onboarding_complete', 'true');
        // Redirect to dashboard
    }
}
```

## Dependencies

- User preferences storage
- Tutorial content writing
- First quest design

## Verification

1. Clear local storage (simulate new user)
2. Visit app
3. Complete onboarding flow
4. Verify smooth progression
5. Test skip functionality
6. Verify dashboard unlocks

---

**Priority**: HIGH - Critical for user retention
**Reference**: [MASTER_ARCHITECTURE.md - Golden Path](file:///Users/eternalflame/Documents/GitHub/theArk/IP_ARCHIVE/2026-01-RECOVERY/MASTER_ARCHITECTURE.md)
