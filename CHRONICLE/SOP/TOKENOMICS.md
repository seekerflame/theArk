# TOKENOMICS: Abundance Token (AT) Specification

*Chronicle Location: `/CHRONICLE/SOP/TOKENOMICS.md`*
*Status: ACTIVE DOCTRINE*

---

## 1. Token Identity

| Property | Value |
|:---|:---|
| **Name** | Abundance Token |
| **Symbol** | AT |
| **Decimals** | 2 (0.01 AT = 0.6 minutes of labor) |
| **Backing** | 1 AT = 1 Hour of Validated Labor |
| **Network** | OSE Federation Ledger (off-chain, append-only JSON) |
| **Future Bridge** | BTC (Lightning), Ethereum (ERC-20), or Solana (SPL) |

---

## 2. Supply Model

### 2.1 Minting (Inflation)

AT is minted when:

| Event | Rate | Validator |
|:---|:---|:---|
| Human Labor | 1 AT / hour | Oracle multi-sig (3/5) |
| Machine Output | Variable (e.g., 0.1 AT / kWh) | Hardware Bridge sensor |
| Quest Completion | Fixed bounty (e.g., 5 AT) | Quest issuer + Oracle |
| Community Service | Discretionary | Village Council |

**Daily Cap**: No global cap. Inflation is tied to real production, not speculation.

### 2.2 Recirculation (The Circular Flow)

AT is **never burned** in standard transactions. To maintain abundance, value is recirculated into pools that ensure system longevity.

| Event | Recirculation Target |
|:---|:---|
| Internal services (e.g., Fab Lab) | 100% to Provider (Operator + Maintenance) |
| Material usage | 100% to **OSE Node Wallet** (to restock materials) |
| Infrastructure Fee (Tax) | 5-10% to **OSE Node Wallet** (Village Maintenance) |
| Dispute resolution (slashing) | Redirected to **OSE Node Wallet** (Victim/Public Fund) |

**The OSE Node Wallet**: A multi-sig community fund used to purchase external resources (seeds, raw steel, energy) or to fund village-wide infrastructure upgrades.

**Philosophical Rule**: Every AT spent is an IOU for future contribution. Deleting AT is deleting human potential.

### 2.3 Circulating Supply

- **Genesis**: 0 AT (no pre-mine)
- **Year 1 Target**: 10,000 AT (100 contributors × 100 hours avg)
- **Year 5 Target**: 1,000,000 AT (1000+ contributors + machine output)

---

## 3. Distribution

| Allocation | Percentage | Purpose |
|:---|:---|:---|
| **Laborers** | 80% | Direct mint for validated work |
| **Infrastructure Reserve** | 10% | Village maintenance, emergency fund |
| **Development Fund** | 5% | Core protocol development (The Ark) |
| **Seeder Bonus** | 5% | Early contributors (first 50) |

**No VC allocation. No team pre-mine. No insider advantage.**

---

## 4. Governance

### 4.1 Voting Power

- 1 AT = 1 Vote (for economic decisions)
- 1 Citizen = 1 Vote (for constitutional decisions)

### 4.2 Proposal Types

| Type | Quorum | Threshold |
|:---|:---|:---|
| Quest Creation | 1 Oracle | Approval |
| Budget Allocation | 10% of supply | 51% |
| Protocol Upgrade | 20% of supply | 66% |
| Constitutional Amendment | 50% of citizens | 75% |

---

## 5. Exchange Mechanics

### 5.1 Internal Exchange

- AT accepted for all village goods/services.
- Prices set by providers (free market within village).
- Example: Meal = 0.5 AT, Housing/month = 0 AT (covered by infrastructure).

### 5.2 External Exchange (Future)

| Phase | Mechanism | Target Rate |
|:---|:---|:---|
| OTC Desk | Manual swaps with trusted partners | 0.10 USD |
| DEX Listing | Uniswap/Raydium liquidity pool | Market |
| CEX Listing | Major exchange (long-term) | Market |

### 5.3 BTC Bridge (Priority)

- **Goal**: 1 AT ↔ X sats (satoshis)
- **Mechanism**: Lightning Network escrow contract
- **Why BTC?**: Hardest money, no counterparty risk, global liquidity

---

## 6. Security Model

### 6.1 Validation

| Layer | Mechanism |
|:---|:---|
| Labor Proof | Photo/video upload, Oracle review |
| Time Proof | GPS timestamp, device attestation |
| Reputation | Decay function (unvalidated claims reduce trust) |

### 6.2 Anti-Sybil

- New wallets require invitation from existing citizen.
- First 10 mints require manual Oracle approval.
- Suspicious patterns flagged for council review.

### 6.3 Slashing

- Fraudulent mints: 100% AT balance forfeited.
- Repeated violations: Wallet banned from network.

---

## 7. Roadmap to 1 AT = 1 USD

| Milestone | Trigger | Estimated Timeline |
|:---|:---|:---|
| **Internal Circulation** | 3+ villages using AT | Q2 2026 |
| **Export Product Launch** | First sale for Fiat/BTC | Q4 2026 |
| **OTC Desk** | Manual AT ↔ BTC swaps | Q1 2027 |
| **DEX Listing** | Liquidity pool funded | Q3 2027 |
| **Parity** | Market demand = 1 hour = $1 | 2028-2030 |

---

## 8. Technical Implementation

### 8.1 Current (MVP)

- **Ledger**: `village_ledger_py.json` (append-only JSON)
- **Minting**: `/api/mint` endpoint with Oracle validation
- **Viewing**: `/api/ledger`, `/api/balance/<wallet>`

### 8.2 Future (Production)

- **Ledger**: DAG-based (see `/ledger/abundance-dag/`)
- **Bridge**: Lightning Network integration
- **ZK Proofs**: Private labor verification without exposing details

---

## 9. Jules Delegation: AT-BTC Bridge

This is the coding task for Jules or another AI operative.

**Mission**: Build the AT ↔ BTC bridge using Lightning Network.

**Scope**:

1. Research: LND, Core Lightning, or Eclair API
2. Create: `core/lightning_bridge.py`
3. Endpoints: `/api/exchange/quote`, `/api/exchange/swap`
4. Tests: Mock Lightning payments, edge cases

**See**: `JULES_ONBOARDING.md` for setup.

---

*"Scarcity is a choice. We choose abundance."*

*Document Owner: Antigravity / EternalFlame*
*Last Updated: 2026-01-03*
