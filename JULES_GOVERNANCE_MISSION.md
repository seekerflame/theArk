# JULES MISSION: Governance & Justice Hub (The Unified UI)

**Priority**: 🔴 CRITICAL  
**Context**: User flagged "Hydra Problem" (too many disparate apps).  
**Goal**: Consolidate `verifier.html`, Reporting, and Appeals into a single **Community Justice Hub**.

---

## MISSION: Unify and Modernize

We have a legacy `verifier.html` that user likes, but it points to old APIs (`/api/graph`, `/api/verify`). We need to upgrade it to use the new `api/moderation.py` and `api/economy.py` endpoints, and merge it with the new Reporting/Appeals features.

## 1. The Justice Hub (`web/justice.html`)

Create a main "Justice" dashboard that serves as the entry point.

**Tabs:**

1. **Verification Station** (Upgraded `verifier.html`) - For Oracles
2. **Report Center** (New) - For Users to report/view status
3. **Transparency Log** (New) - Public feed
4. **Appeals Court** (New) - For Jurors

## 2. Upgrade Verification Station

**Current State**: `verifier.html` exists but fetchs from `/api/graph`.  
**New Requirements**:

- fetch from `/api/verification/pending` (from `api/economy.py`)
- fetch from `/api/moderation/queue` (from `api/moderation.py`)
- combine these into one "Inbox" for the oracle.

**Action**: Refactor `verifier.html` code into a component `web/components/verification_inbox.js` and embed it in the Justice Hub.

## 3. Reporting UI (New)

- **Modal**: "Report This Content"
- **API**: `POST /api/moderation/report`
- **UX**: Simple, fast, shows cost (0.1 AT).

## 4. Transparency Log (New)

- **View**: Infinite scroll list of bans/actions
- **API**: `GET /api/moderation/log`

---

## FILES TO MODIFY/CREATE

| File | Status | Action |
|------|--------|--------|
| `web/justice.html` | NEW | Main container (Tabs + Nav) |
| `web/verifier.html` | **DEPRECATE** | Move logic to `web/justice.html` tab |
| `web/css/justice.css`| NEW | Unified styling |
| `web/components/oracle_inbox.js` | NEW | The "Pending Verifications" logic |
| `web/components/transparency.js` | NEW | The Log viewer |

---

## API MAP (The Source of Truth)

- **Pending Verifications**: `GET /api/verification/pending` (requires Auth)
- **Moderation Queue**: `GET /api/moderation/queue` (requires Auth + Oracle Role)
- **Submit Verification**: `POST /api/verification/submit`
- **Public Log**: `GET /api/moderation/log`

---

## EXECUTION ORDER

1. **Create `web/justice.html`** skeleton.
2. **Port `verifier.html` logic** into the "Oracle" tab of Justice Hub.
3. **Wire up** the new API endpoints.
4. **Delete/Redirect** old `verifier.html` to `justice.html` to kill the Hydra.

**"One System. One Interface. No Hydra."** 🛡️
