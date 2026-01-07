# JULES MISSION: Governance UI Components

**Priority**: 🔴 CRITICAL  
**ETA**: 2-3 days  
**Context**: Anti-dystopia architecture implementation

---

## MISSION 1: Community Reporting System

### Goal

Build a reporting flow where users can flag content for review.

### Requirements

1. **Report Button**: One-tap flag on any content
2. **Cost**: 0.1 AT to report (refunded if upheld)
3. **Categories**: Violence, Fraud, Spam, Other
4. **Queue**: Reports go to oracle review queue
5. **Status**: Reporter sees outcome (Action Taken / No Action)

### Files to Create

```
web/
├── report.html         # Report submission modal
├── css/report.css      # Styling
api/
├── report.py           # Backend endpoints
```

### API Endpoints

- `POST /api/report/submit` - Submit a report
- `GET /api/report/status/<report_id>` - Check report status
- `GET /api/oracle/queue` - Oracle sees pending reports

### UI/UX Requirements

- Report in <3 clicks
- Show full context to oracle
- Confirm action with costs displayed

---

## MISSION 2: Appeals Dashboard

### Goal

Build system where banned users can appeal to community court.

### Flow

```
1. User banned → Sees "Appeal" button
2. User submits appeal with evidence
3. 9 random users selected as "Jury"
4. Each votes: Uphold / Overturn (anonymous)
5. 7/9 required to overturn
6. Result logged to transparency
```

### Requirements

1. **Jury Selection**: Random from users with rep >50
2. **Voting Period**: 48 hours
3. **Anonymity**: Jury sees case, not each other's votes
4. **Compensation**: False ban = 50 AT from treasury

### Files to Create

```
web/
├── appeals.html        # Appeals submission page
├── jury.html           # Jury voting interface
├── css/appeals.css     # Styling
api/
├── appeals.py          # Backend logic
core/
├── community_court.py  # Jury selection, voting
```

### API Endpoints

- `POST /api/appeal/submit` - Submit appeal
- `GET /api/appeal/jury/<appeal_id>` - Get jury panel
- `POST /api/appeal/vote` - Jury member votes
- `GET /api/appeal/result/<appeal_id>` - Check result

---

## MISSION 3: Oracle Queue View

### Goal

Dashboard for oracles to review pending reports/verifications.

### Requirements

1. List all pending reports assigned to this oracle
2. Show full content + context
3. Quick action buttons: Approve / Reject / Escalate
4. Track oracle's accuracy score
5. Show audit status (is meta-oracle reviewing me?)

### Files to Create

```
web/
├── oracle_queue.html   # Oracle dashboard
├── css/oracle.css      # Styling
```

---

## MISSION 4: Transparency Log Viewer

### Goal

Public page showing all moderation actions.

### Requirements

1. Table of all bans/warnings/appeals
2. Filterable by: action type, oracle, date
3. Link to appeal for each action
4. No user PII visible (pseudonymous IDs only)

### Files to Create

```
web/
├── transparency.html   # Public log viewer
```

---

## DESIGN REQUIREMENTS

### Visual Style

- Match existing Pip-Boy aesthetic (green/blue gradient, dark bg)
- Use existing `style.css` color scheme
- Mobile-first responsive design

### UX Principles

- Maximum 3 clicks for any action
- Clear feedback on success/failure
- Loading states for async operations
- Error messages human-readable

---

## SUCCESS CRITERIA

| Component | Must Have | Nice to Have |
|-----------|-----------|--------------|
| Reporting | <3 click submit | Attach evidence |
| Appeals | 48h vote window | Real-time vote count |
| Oracle Queue | Full context | Bulk actions |
| Transparency | Public feed | RSS/API access |

---

## NOTES FOR JULES

1. **Backend already exists in `core/`** - You're building UI on top
2. **Auth uses JWT** - `get_auth_user()` available in handlers
3. **Ledger is append-only** - All actions become permanent record
4. **Test locally** at `http://localhost:3000`

**Start with Mission 1 (Reporting). That unblocks the rest.**

---

*Advance the mission.* 🚀
