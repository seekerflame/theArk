# Jules Mission Brief: Flow-State Onboarding Experience

**Agent**: Google Jules  
**Priority**: HIGH  
**Timeline**: 5 days  
**Inspiration**: Duolingo + Brilliant + Skool + Natural Learning

---

## Mission Context

Users won't read docs. They won't watch long videos. They need to **learn by doing** in a way that feels like play, not work. This onboarding must:

1. Induce **flow state** (challenge matches skill, immediate feedback)
2. Feel **natural** (like the app learns WITH the user)
3. Be **personalized** (different paths for different types)
4. Respect **time** (user knows how long things take)
5. Enable **retention** (spaced repetition, not info dump)

---

## Onboarding Questions (First 60 Seconds)

When user opens app first time, ask:

**Question 1: "What brings you here?"**

- [ ] Earn money for doing things I already do
- [ ] Support local businesses in my community
- [ ] Learn about alternative economies
- [ ] A friend told me about it
- [ ] Just exploring

**Question 2: "How do you prefer to learn?"**

- [ ] Show me, don't tell me (interactive tutorials)
- [ ] Quick video walkthrough (60 seconds or less)
- [ ] Let me figure it out myself (just show tooltips)
- [ ] Read the docs (text-based guide)

**Question 3: "What's your experience with crypto/wallets?"**

- [ ] Total beginner (what's a wallet?)
- [ ] I've used Venmo/PayPal
- [ ] I know about Bitcoin/crypto
- [ ] I'm an expert (skip basics)

Based on answers, customize the path:

- Beginner + Interactive = Full Duolingo journey
- Expert + Self-guided = Just tooltips + first quest
- Earner + Video = Quick video + "Find Quests" CTA

---

## Tutorial Quest Flow (Duolingo-Style)

### Level 1: "Your First AT" (2 minutes)

**Step 1**: Claim your wallet

- Animation: Wallet appears with friendly sparkle
- "This is your wallet. It holds your AT."
- Action: Tap wallet to see balance (0 AT)

**Step 2**: Complete micro-quest

- "Let's earn your first AT! Take a photo of something beautiful near you."
- User takes photo with camera
- "Great! Submitting for verification..."
- (Fake verification for tutorial - auto-approve in 2 seconds)
- Celebration animation: "+0.5 AT!"
- "That's 30 minutes of someone's labor. You earned it with yours."

**Step 3**: See balance update

- Wallet pulses, shows new balance
- "You now have 0.5 AT. Ready to earn more?"

### Level 2: "Find a Quest" (2 minutes)

**Step 1**: Browse quest board

- "These are quests posted by your community."
- Highlight one quest card
- "This one gives 2 AT for helping a local shop."

**Step 2**: Claim a quest

- User taps "Claim"
- "You've committed to this quest. Complete it within 2 hours."
- Timer appears (friendly, not stressful)

**Step 3**: Complete quest (simulated in tutorial)

- "For this tutorial, pretend you completed the quest."
- User taps "I've completed this"
- "Now you need 3 witnesses to verify."

### Level 3: "Get Verified" (1 minute)

**Step 1**: Select witnesses

- "Choose 3 people to verify your work."
- (Tutorial shows fake witnesses or uses Oracles)
- User selects 3

**Step 2**: Wait for verification

- Progress bar shows witnesses approving
- "Witness 1 approved! ✓"
- "Witness 2 approved! ✓"
- "Witness 3 approved! ✓"
- Celebration: "+2 AT! You're now a verified contributor."

### Level 4: "Spend or Save" (1 minute)

**Step 1**: Show balance

- "You now have 2.5 AT."
- "That's 2.5 hours of human labor stored in your wallet."

**Step 2**: Options

- "You can:"
- "🛒 Spend at local businesses"
- "💰 Save for later"
- "🔄 Convert to BTC/USD"
- User taps one to explore (no action needed)

**End of Tutorial**:

- "You're ready! Find quests, earn AT, build community."
- Badge unlocked: "First Steps 🌱"
- CTA: "Find Quests Near Me" or "Post a Quest"

---

## Flow-State Design Principles

### 1. Challenge = Skill

- Tutorial difficulty adjusts to user responses
- If user clicks fast, speed up explanations
- If user hesitates, offer more guidance

### 2. Immediate Feedback

- Every action has visual/audio response
- - animations for positive actions
- Gentle guidance for errors (no red "WRONG")

### 3. Clear Goals

- Always show "Step X of Y"
- Progress bar visible
- Time estimate: "~2 minutes remaining"

### 4. No Dead Ends

- "Skip this" always available
- "Go back" always available
- "Ask a human" always available

### 5. Intrinsic Motivation

- No forced ads or upsells
- Earning AT IS the reward
- Badges for milestones (collect them all)

---

## Time Awareness Features

**Show Duration Upfront**:

- "This tutorial takes ~5 minutes"
- "This quest takes ~30 minutes"
- "This video is 60 seconds"

**Respect User's Time**:

- Auto-save progress (can resume later)
- "Continue where you left off?"
- No punishment for pausing

**Track Learning Time**:

- "You've learned for 15 minutes today"
- "Streak: 3 days in a row!"
- But make it optional (no shame for breaks)

---

## Retention Strategies

### Spaced Repetition

- After Day 1: "Remember how to claim a quest?"
- After Day 3: "Ready for your next challenge?"
- After Day 7: "You've got 5 new quests near you!"

### Progressive Disclosure

- Don't show everything at once
- Unlock features as user progresses:
  - Level 1: Earn AT
  - Level 5: Post Quests
  - Level 10: Become a Witness
  - Level 20: Start a Mutual Aid Pool

### Social Proof

- "12 people in your area completed quests today"
- "Your friend Sarah earned 5 AT this week"
- Leaderboard (opt-in)

---

## Technical Implementation

### Files to Create

- `web/modules/onboarding.js` - Tutorial logic
- `web/modules/onboarding.css` - Styles
- `web/templates/tutorial_quests.json` - Tutorial content

### Files to Modify

- `web/app.js` - Add onboarding check on first load
- `web/index.html` - Add onboarding container
- `core/identity.py` - Store onboarding progress

### Key Functions

```javascript
// Check if user is new
function checkOnboardingStatus(userId) {
  return localStorage.getItem(`onboarding_complete_${userId}`) !== 'true';
}

// Start onboarding flow
function startOnboarding(userPreferences) {
  // userPreferences from initial questions
  const path = calculateLearningPath(userPreferences);
  renderTutorialStep(path.steps[0]);
}

// Track progress
function completeStep(stepId) {
  saveProgress(stepId);
  if (stepId === path.steps.length - 1) {
    markOnboardingComplete();
    awardBadge('first_steps');
  } else {
    renderTutorialStep(path.steps[stepId + 1]);
  }
}
```

---

## Success Metrics

**Completion Rate**: 80%+ of users finish tutorial  
**Time to First AT**: Under 5 minutes  
**Day 7 Retention**: 50%+ return within a week  
**Quest Completion Rate**: 70%+ of claimed quests completed

---

## Deliverables

1. **Onboarding Flow** (5 levels, ~7 minutes total)
2. **Question System** (3 questions, adaptive paths)
3. **Progress Tracking** (localStorage + server sync)
4. **Badge System** (5 initial badges)
5. **Time Awareness UI** (duration labels, streaks)

---

*Make it feel like Duolingo meets Brilliant meets a warm welcome from a friend. Natural. Fun. Flow-inducing.*

*Advance the mission.*
