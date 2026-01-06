# Jules Mission Brief: Mobile PWA & Merchant Features

**Agent**: Google Jules  
**Assigned By**: Antigravity + EternalFlame  
**Mission ID**: COMMUNITY_BRIDGE_MOBILE  
**Priority**: HIGH  
**Estimated Complexity**: 3-5 days of focused work

---

## Mission Context

The Ark OS has successfully implemented backend verification economics (3-Witness Protocol, quest system, tiered rewards). However, **80% of user interactions will happen on mobile phones**, and the current implementation is desktop-focused.

We need to build the mobile-first PWA experience to enable real-world usage at art walks, farmers markets, bars, and community events.

---

## Your Three Assignments

### Task 1: Mobile PWA Camera & Geolocation Integration

**Objective**: Enable users to submit photo proof and find nearby quests on their phones.

**Technical Requirements**:

1. **Camera Integration**:
   - Use `navigator.mediaDevices.getUserMedia()` for camera access
   - Allow photo capture for quest proof submission
   - Compress images before upload (max 1MB)
   - Store photos as base64 in proof payload (or upload to IPFS if available)

2. **Geolocation**:
   - Use `navigator.geolocation.getCurrentPosition()`
   - Get user's lat/lon with permission
   - Filter available quests by proximity (Haversine distance already implemented in backend)
   - Show "X quests within 5 miles" badge

3. **Offline-First Service Worker**:
   - Cache quest list for offline viewing
   - Queue verification submissions if offline, sync when online
   - Use `workbox` or vanilla service worker

**Files to Modify**:

- `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/web/app.js`
  - Add `capturePhoto()` function
  - Add `getUserLocation()` function
  - Add `filterQuestsByProximity()` function
- `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/web/index.html`
  - Add camera input element
  - Add location permission prompt

**API Endpoints to Use**:

- `GET /api/quests/available` - Returns all open quests
- `POST /api/verification/request` - Submit verification with photo proof
  - Payload includes `proof: {photos: [base64_string], geolocation: {lat, lon}, timestamp}`

**Testing**:

- Test on actual mobile device (iPhone/Android)
- Verify camera permission flow works
- Verify location permission flow works
- Test in airplane mode (offline-first)

---

### Task 2: Interactive Merchant Map for Art Walks

**Objective**: Build a visual map showing merchant locations with active quests, enabling art walk/farmers market navigation.

**Technical Requirements**:

1. **Map Rendering**:
   - Use **Leaflet.js** (lightweight, no API key required) or Mapbox (if API key available)
   - Display markers for each merchant with active quests
   - Cluster markers if many merchants in small area
   - Center map on user's current location

2. **Merchant Data Integration**:
   - Each quest can optionally have `location: {lat, lon, name}` field
   - Fetch from `GET /api/quests/available`
   - Filter to only show quests with location data

3. **Interactive Features**:
   - Click marker → show quest details popup
   - "Navigate to" button → open Google Maps/Apple Maps with directions
   - Filter by quest type (physical/skill/social) and reward amount
   - Toggle: "Show all merchants" vs. "Show only with active quests"

4. **QR Code Scanning**:
   - Add QR code scanner for instant quest claiming
   - Merchant posts QR code at booth → user scans → quest claimed
   - Use `jsQR` library or `html5-qrcode`

**Files to Create**:

- `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/web/merchant_map.html` (new view)
- `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/web/modules/merchant_map.js` (new module)

**Files to Modify**:

- `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/web/index.html`
  - Add "Merchant Map" nav item
- `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/web/app.js`
  - Add `renderMerchantMap()` function to switchView

**Testing**:

- Create test quests with mock merchant locations in Bakersfield, CA (art walk location)
- Verify map loads and centers correctly
- Test QR code generation and scanning flow

---

### Task 3: Order-Ahead System for Bars/Restaurants

**Objective**: Allow customers to pre-order drinks/food via app, skip the line, tip on performance.

**Technical Requirements**:

1. **Merchant Menu System**:
   - New API endpoint: `GET /api/merchant/menu/{merchant_id}`
   - Returns menu items: `{id, name, description, price_at, category}`
   - Merchant dashboard to add/edit menu items

2. **Order Flow**:
   - Customer browses menu
   - Adds items to cart
   - Submits order with AT payment (escrowed)
   - Kitchen/bar receives notification
   - When ready, customer gets notification
   - Customer picks up order, releases escrow + optional tip

3. **Backend API**:
   - `POST /api/orders/create` - Create order, escrow AT
   - `POST /api/orders/{order_id}/ready` - Merchant marks order ready (sends notification)
   - `POST /api/orders/{order_id}/complete` - Customer confirms pickup, release escrow + tip

4. **Notification System**:
   - Use **Web Push API** for notifications
   - Merchant gets push when new order arrives
   - Customer gets push when order ready
   - Fallback to in-app polling if push not supported

**Files to Create**:

- `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/api/orders.py` (new API module)
- `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/core/order_system.py` (business logic)
- `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/web/modules/order_ahead.js` (UI)

**Files to Modify**:

- `/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/server.py`
  - Import and register orders API routes

**Testing**:

- Create mock menu for "Joe's Coffee Shop"
- Simulate order flow: browse → order → notification → pickup → tip
- Test escrow release and tip distribution

---

## Technical Context

**Current Architecture**:

- Backend: Python 3 (standard library only, minimal dependencies)
- Frontend: Vanilla JS (no React/Vue framework)
- Database: SQLite ledger (`village_ledger.db`)
- Server: `http.server` with custom router
- Auth: JWT tokens

**Existing Systems to Integrate With**:

- **Quest System**: `core/quest_system.py` - handles quest posting, claiming, filtering
- **Verification System**: `core/triple_verification.py` - 3-witness verification protocol
- **Economy API**: `api/economy.py` - minting, transfers, store purchases
- **Art Walk Mode**: PWA mobile toggle already exists in `web/app.js` (lines 4697-4717)

**Important Files**:

- [server.py](file:///Volumes/Extreme%20SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/server.py) - Main server initialization
- [web/app.js](file:///Volumes/Extreme%20SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/web/app.js) - Frontend app logic
- [api/economy.py](file:///Volumes/Extreme%20SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark/api/economy.py) - Quest/verification endpoints (lines 220-365)

---

## Expected Deliverables

1. **Code**:
   - All files committed to git with clear commit messages
   - Follow existing code style (vanilla JS, minimal dependencies)
   - Add inline comments for complex logic

2. **Testing**:
   - Create test scripts demonstrating each feature
   - Document test results in `JULES_MOBILE_PWA_TESTING.md`

3. **Documentation**:
   - Update `docs/art_walk_manual.md` with new mobile features
   - Create `docs/order_ahead_guide.md` for merchants

4. **Demo Video** (optional but appreciated):
   - Record 2-min screencast showing mobile features in action
   - Save as `demos/mobile_pwa_demo.mp4`

---

## Success Criteria

**Task 1 Success**: User can take photo on phone, submit as quest proof, and filter quests by location.

**Task 2 Success**: User can view interactive map of merchant locations, click to see quests, and scan QR codes.

**Task 3 Success**: User can order coffee via app, bartender gets notification, user picks up and tips, all in AT.

---

## Timeline

- **Day 1-2**: Task 1 (Camera + Geolocation)
- **Day 3**: Task 2 (Merchant Map)
- **Day 4-5**: Task 3 (Order-Ahead System)

---

## Questions/Blockers

If you encounter any blockers or need clarification, document them in `JULES_QUESTIONS.md` and tag Antigravity for review.

---

**Advance the Mission. Build the infrastructure for the new economy.**
