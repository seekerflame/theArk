# JULES DELEGATION: AT ↔ BTC Lightning Bridge

**Mission Type**: CRITICAL INFRASTRUCTURE
**Priority**: HIGH
**Estimated Effort**: 20-40 hours

---

## OBJECTIVE

Build a bidirectional bridge between Abundance Token (AT) and Bitcoin (BTC) using the Lightning Network.

This enables:

- AT holders to exchange for BTC (liquidity)
- External parties to buy AT with BTC (demand)
- Real-world value backing for AT

---

## CONTEXT

Read these files first:

1. `CHRONICLE/SOP/ECONOMIC_MODEL.md` - Why AT exists
2. `CHRONICLE/SOP/TOKENOMICS.md` - How AT works
3. `07_Code/The_Ark/core/ledger.py` - Current ledger implementation

---

## DELIVERABLES

### 1. Research Document

**File**: `07_Code/The_Ark/docs/LIGHTNING_BRIDGE_RESEARCH.md`

- Compare LND vs Core Lightning vs Eclair
- Document API patterns for invoices/payments
- Recommend approach for MVP

### 2. Lightning Bridge Module

**File**: `07_Code/The_Ark/core/lightning_bridge.py`

```python
class LightningBridge:
    def __init__(self, node_url: str, macaroon_path: str):
        """Initialize connection to Lightning node."""
        pass
    
    def get_quote(self, at_amount: float) -> dict:
        """Return BTC equivalent for given AT amount.
        
        Returns:
            {
                "at_amount": 10.0,
                "btc_amount": 0.0001,
                "sats": 10000,
                "rate": "1 AT = 1000 sats",
                "expires_at": "2026-01-03T12:00:00Z"
            }
        """
        pass
    
    def create_invoice(self, at_amount: float, wallet_id: str) -> dict:
        """Create Lightning invoice to receive BTC for AT.
        
        Returns:
            {
                "invoice": "lnbc...",
                "payment_hash": "abc123",
                "at_to_credit": 10.0
            }
        """
        pass
    
    def execute_swap(self, payment_hash: str) -> dict:
        """After BTC received, mint AT to user wallet.
        
        Returns:
            {
                "status": "complete",
                "at_minted": 10.0,
                "wallet_id": "user_wallet",
                "tx_id": "ledger_block_id"
            }
        """
        pass
```

### 3. API Endpoints

**File**: `07_Code/The_Ark/api/exchange.py`

| Endpoint | Method | Description |
|:---|:---|:---|
| `/api/exchange/quote` | GET | Get current AT:BTC rate |
| `/api/exchange/buy` | POST | Create invoice to buy AT with BTC |
| `/api/exchange/sell` | POST | Withdraw BTC for AT (future) |
| `/api/exchange/status/<hash>` | GET | Check swap status |

### 4. Tests

**File**: `07_Code/The_Ark/tests/test_lightning_bridge.py`

- Mock Lightning node responses
- Test quote generation
- Test invoice creation
- Test swap execution
- Test error handling (expired invoice, insufficient funds)

---

## TECHNICAL CONSTRAINTS

1. **Python 3.11+ only** (standard library preferred)
2. **No external dependencies** unless absolutely necessary (requests is OK)
3. **Append-only ledger** - swaps create new blocks, never modify existing
4. **Offline-capable** - cache rates, queue swaps when node unreachable

---

## RATE CALCULATION

For MVP, use fixed rate:

```
1 AT = 1000 sats (0.00001 BTC)
```

Future: Dynamic rate based on:

- Village labor output
- External market demand
- Liquidity pool depth

---

## SECURITY REQUIREMENTS

1. **Never store private keys** in The Ark - use external node
2. **Validate all inputs** - prevent injection
3. **Rate limiting** - prevent abuse
4. **Audit logging** - all swaps recorded on ledger

---

## COMMIT FORMAT

```
[Jules/Lightning] Your descriptive message
```

---

## SUCCESS CRITERIA

The bridge is complete when:

- [ ] Research doc reviewed and approved
- [ ] `lightning_bridge.py` passes all tests
- [ ] API endpoints functional with mock node
- [ ] Integration test with real testnet Lightning node
- [ ] Documentation updated

---

## QUESTIONS?

Coordinate via:

- GitHub commits (async)
- `/api/mission/propose` (AI-to-AI)
- Through EternalFlame (human relay)

---

**Status**: AWAITING JULES ACKNOWLEDGMENT
**Gemini**: Standing by for coordination

*"We bridge the old money to the new."*
