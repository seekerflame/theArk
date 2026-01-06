# Jules Mission Brief: First Friday Art Walk Launch

**Agent**: Google Jules  
**Assigned By**: Antigravity + EternalFlame  
**Mission ID**: FIRST_FRIDAY_MOBILE  
**Priority**: 🔴 CRITICAL - LAUNCH BLOCKER  
**Timeline**: 3 days  
**Launch Event**: Next First Friday (Bakersfield, CA monthly art walk)

---

## The Reality
https://render.com/docs/mcp-server
✅ **Backend is DONE**: Quest system, verification, bounty board all working  
❌ **Frontend is desktop-only**: Can't use at mobile art walk event  
🎯 **Your Mission**: Make it work on phones in 3 days

---

## Context: What We're Launching

**The Partnership**: Kern Art Council + 5-10 local merchants  
**The Event**: First Friday downtown art walk (hundreds of people wandering with phones)  
**The Hook**: Flyers say "Download the map for First Friday" → opens PWA  
**The Experience**: Interactive map, QR code quest claiming, earn AT for exploring

---

## Task 1: Mobile-Optimize Quest Browser (1 day)

**What Exists**: Desktop bounty board at `web/bounty_board.js` (190 lines, fully functional)  
**What's Needed**: Make it thumb-friendly for phones

**Steps**:

1. Add CSS media queries for mobile (`@media (max-width: 768px)`)
2. Make buttons min 44px height (Apple guidelines)
3. Increase font sizes for readability
4. Add pull-to-refresh
5. Test on actual iPhone/Android

**Files**:

- `web/bounty_board.js` - Adjust card styles (lines 46-113)
- `web/style.css` - Add mobile breakpoints

**Success**: User can comfortably browse/claim quests on phone

---

## Task 2: QR Code Quest Claiming (1 day)

**The Flow**:

```
Merchant creates quest → System generates QR code → Merchant prints/hangs at booth
↓
Customer scans QR → Quest auto-claimed → Opens in app
```

**Steps**:

1. Add QR generation to quest creation (use `qrcode.js`)
2. Create `/api/quests/{id}/qr` endpoint (returns PNG image)
3. Add QR scanner to mobile app (use `html5-qrcode` library)
4. When scanned, extract quest_id and POST to `/api/quests/claim`

**Files to Create**:

- `web/modules/qr_scanner.js`

**Files to Modify**:

- `api/economy.py` - Add QR endpoint after line 365
- `web/index.html` - Add "Scan QR" button in header

**Success**: Scan QR code → quest claimed instantly, no typing

---

## Task 3: Interactive Merchant Map (1 day)

**The Flow**:

```
User opens "Map" → Sees downtown with merchant pins → Clicks pin → Quest details + Navigate button
```

**Steps**:

1. Use **Leaflet.js** (no API key, lightweight: `<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>`)
2. Fetch quests from `/api/quests/available`
3. Filter quests with `location: {lat,lon}` data
4. Plot markers on map (cluster if many merchants nearby)
5. Click marker → popup with quest details
6. "Navigate" button → open Apple Maps/Google Maps

**Files to Create**:

- `web/modules/merchant_map.js`
- `web/merchant_map.html`

**Files to Modify**:

- `web/index.html` - Add "Map" nav item
- `web/app.js` - Add `renderMerchantMap()` to `switchView()`

**Map Center**: Bakersfield downtown (lat: 35.3733, lon: -119.0187)

**Success**: User sees visual map of merchants, can navigate to booths

---

## What You DON'T Need to Build

❌ Order-ahead system (not needed for v1)  
❌ Camera/photo upload (manual verification for first event)  
❌ Push notifications (users can manually check app)  
❌ Offline service worker (nice to have, not critical)

Focus on the **3 core features above**. Everything else can wait until after first event feedback.

---

## Technical Context

**Existing Backend APIs**:

- `GET /api/quests/available`
- `POST /api/quests/claim`
- `POST /api/quests/post`
- `GET /api/quests/detail?quest_id=X`

**Existing Frontend** (`web/bounty_board.js`):

- Quest rendering function (line 25-119)
- Claim function (line 143-156)
- Just needs mobile CSS

**File Structure**:

```
/web
  ├── index.html (main app shell)
  ├── app.js (routing, switchView)
  ├── style.css (global styles)
  ├── bounty_board.js (quest UI - exists!)
  └── modules/
      ├── qr_scanner.js (you create)
      └── merchant_map.js (you create)
```

---

## Success Criteria

**Task 1**: Open bounty board on iPhone → cards fit screen, buttons are tappable, pull-to-refresh works

**Task 2**: Create quest → get QR code image → print → scan with phone → quest claimed

**Task 3**: Open map view → see Bakersfield downtown → see merchant pins → click → see quest → navigate to booth

---

## Timeline

- **Day 1**: Mobile CSS optimization + testing
- **Day 2**: QR code system end-to-end
- **Day 3**: Merchant map with Leaflet.js

---

## Deliverables

1. **Code**: Committed to git with clear messages
2. **Testing**: Document results in `JULES_FIRST_FRIDAY_TEST.md`
3. **Demo**: 2-min video showing mobile flow (optional but helpful)

---

## Questions/Blockers

If stuck, document in `JULES_QUESTIONS.md` and tag Antigravity.

---

*Launch is 3 days away. Build the minimum, test on real devices, ship it. We'll iterate after real user feedback.*
