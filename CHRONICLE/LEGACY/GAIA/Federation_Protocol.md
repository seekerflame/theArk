# Federation Protocol v1.0

## Multi-Village Synchronization & Trade

### Vision

Enable multiple OSE villages to operate as independent nodes while synchronizing ledgers and trading resources/tokens between each other.

### Architecture

```
Village A (Missouri)  ←→  Federation Hub  ←→  Village B (California)
     ↓                                              ↓
  Local Ledger                                  Local Ledger
     ↓                                              ↓
  Local Economy                                  Local Economy
```

### Core Principles

1. **Sovereignty First** - Each village maintains its own ledger
2. **Opt-In Federation** - Villages choose which others to federate with
3. **Conflict Resolution** - Consensus via timestamp + village reputation
4. **Privacy Preserved** - Only public transactions sync (no PII)

---

## Phase 1: Federation Discovery

### Village Registry

```json
{
  "village_id": "ose-missouri-001",
  "name": "Factor e Farm",
  "location": {"lat": 38.45, "lon": -93.85},
  "public_key": "...",
  "federation_enabled": true,
  "trusted_villages": ["ose-california-001", "ose-texas-001"],
  "last_sync": 1703462400
}
```

### Discovery Methods

1. **Manual Registration** - Admin adds village via IP/domain
2. **NetBird Mesh** - Auto-discover via existing VPN
3. **DHT (Future)** - Distributed hash table for global discovery

---

## Phase 2: Ledger Synchronization

### Sync Protocol

1. **Heartbeat** - Villages ping each other every 60s
2. **Block Diff** - Exchange blocks since last sync
3. **Merkle Verification** - Validate block integrity
4. **Conflict Resolution** - Last-write-wins with reputation weight

### API Endpoints

```
POST /federation/register
POST /federation/sync
GET  /federation/villages
POST /federation/trade
```

---

## Phase 3: Inter-Village Trade

### Trade Flow

1. Village A user wants resource from Village B
2. Create cross-village transaction proposal
3. Village B user accepts
4. Atomic swap:

   - A's ledger: -X AT, +Resource
   - B's ledger: +X AT, -Resource

5. Both ledgers updated simultaneously

### Trade Example

```json
{
  "trade_id": "trade_001",
  "from_village": "ose-missouri-001",
  "to_village": "ose-california-001",
  "from_user": "Alice",
  "to_user": "Bob",
  "offer": {"AT": 100},
  "request": {"Resource": "Solar Panel"},
  "status": "PENDING"
}
```

---

## Phase 4: Reputation System

### Village Reputation

- **Trust Score** (0-100) based on:
  - Successful trades
  - Ledger uptime
  - Sync reliability
  - Community votes

### Benefits of High Reputation

- Preferred in conflict resolution
- Lower trade fees
- Access to federation-wide quests
- Voting weight in meta-governance

---

## Implementation Files

### Backend

- `federation_hub.py` - Central relay (optional)
- `federation_client.py` - Village-side sync client
- `trade_escrow.py` - Atomic swap handler

### Frontend

- `federation_map.js` - Interactive village map
- `trade_market.js` - Inter-village marketplace UI

### Database

- `federation_registry.json` - Known villages
- `federation_trades.json` - Cross-village trade history

---

## Security Considerations

1. **DDoS Protection** - Rate limit sync requests
2. **Sybil Resistance** - Require physical location proof
3. **Byzantine Tolerance** - 2/3 majority for consensus
4. **Encrypted Comms** - All federation traffic over TLS

---

**Status:** DESIGN COMPLETE - Ready for implementation
