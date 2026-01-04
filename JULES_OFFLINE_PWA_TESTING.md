# JULES DELEGATION: PWA Offline Testing Suite

**Mission Type**: QUALITY ASSURANCE / PWA
**Priority**: MEDIUM
**Estimated Effort**: 15-20 hours

---

## OBJECTIVE

Verify that the Ark OS Progressive Web App (PWA) functions correctly in field conditions where internet connectivity is intermittent or non-existent.

---

## CONTEXT

Read: `07_Code/The_Ark/web/service-worker.js` (Unified SW v2.0)

---

## DELIVERABLES

### 1. Playwright Test Suite

**File**: `07_Code/The_Ark/tests/test_pwa_offline.py` (Using Playwright Python wrapper)

- **Installation Test**: Verify manifest loads and SW installs successfully.
- **Offline Shell Test**: Simulate `offline` mode and verify `index.html`, `app.js`, and `style.css` serve from cache.
- **Quest Asset Caching**: Verify `seh7_quests.json` and `truck_quests.json` are cached.
- **Post-Request Queueing**:
  - Simulate offline "Mint Labor" (POST to `/api/mint`).
  - Verify Service Worker intercepts and adds to IndexedDB queue.
  - Simulate re-connection and verify background sync triggers the fetch.

---

## TECHNICAL CONSTRAINTS

- Use **Playwright** for browser automation.
- Test against `localhost:3000` (can spawn a temporary server in a fixture).
- Focus on the **Unified Service Worker** strategy:
  - Network-First for main app files.
  - Cache-First for CDN assets.
  - Offline Queue for API POSTs.

---

## COMMIT FORMAT

```
[Jules/PWA] Your descriptive message
```

---

**Status**: AWAITING JULES ACKNOWLEDGMENT
**Lead**: Antigravity
