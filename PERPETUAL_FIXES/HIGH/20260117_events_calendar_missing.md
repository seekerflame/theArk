# [HIGH] Events/Calendar System Missing

**Date Reported**: 2026-01-17
**Reporter**: ETERNAL FLAME / Antigravity
**Affected Systems**: [Frontend/Backend]
**User Impact**: High - Core discovery feature unavailable

## Symptom

No events or calendar system exists. This is critical for the "BORED" game loop where users discover local events.

## Root Cause

Feature never implemented. Both backend and frontend missing.

**Technical Details**:

- Backend missing: No `api/events.py`
- Frontend missing: No `web/events_ui.js`
- No database schema for events
- No calendar component

## Expected Behavior

Events system should provide:

- Calendar view (monthly/weekly/daily)
- Event creation (post new events)
- Event discovery (browse local events)
- Quest integration (events generate quests)
- Map integration (show events on map)

## Proposed Architecture

### Backend

**File**: `api/events.py`

```python
# CRUD operations
POST   /api/events/create
GET    /api/events/list
GET    /api/events/:id
PUT    /api/events/:id/update
DELETE /api/events/:id/delete
GET    /api/events/nearby?lat=X&lon=Y&radius=Z
```

### Frontend

**File**: `web/events_ui.js`

- Calendar component (full calendar library or custom)
- Event cards with time/location/description
- Filter by category/distance
- Integration with MAP tab

### Database Schema

```sql
CREATE TABLE events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    location_lat REAL,
    location_lon REAL,
    creator_id TEXT,
    category TEXT,
    quest_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Integration Points

1. **MAP Tab**: Show event pins on map
2. **QUEST System**: Auto-generate quests from events
3. **Social**: Users can RSVP/join events
4. **AT Economy**: Event creators earn AT for attendance

## Dependencies

- Map integration design
- Quest auto-generation logic
- Event moderation system

## Verification

### Phase 1: Backend

1. Create `api/events.py`
2. Test CRUD endpoints with Postman
3. Verify database operations

### Phase 2: Frontend

1. Create calendar UI
2. Test event creation flow
3. Test event browsing

### Phase 3: Integration

1. Show events on MAP
2. Generate quests from events
3. Test full user journey

---

**Priority**: HIGH - Core feature for BORED game loop
**References**:

- [MASTER_ARCHITECTURE.md](file:///Users/eternalflame/Documents/GitHub/theArk/IP_ARCHIVE/2026-01-RECOVERY/MASTER_ARCHITECTURE.md) - Golden Path requires events
- [The Rebrand](file:///Users/eternalflame/Documents/GitHub/theArk/IP_ARCHIVE/2026-01-RECOVERY/MASTER_ARCHITECTURE.md#the-rebrand-from-ark-os-to-bored) - Events are Layer 1: Game Loop
