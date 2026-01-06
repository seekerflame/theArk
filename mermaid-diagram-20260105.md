# MVP Complete Flow: Card → AT → Merchant → Bank

**Generated**: 2026-01-05  
**Context**: First Friday Art Walk Launch - Full fiat on/off ramp visualization

---

## The Complete Money Flow

```mermaid
graph TD
    subgraph "ON-RAMP: User Buys AT"
        A[User's Card] -->|$10 USD| B[Stripe/Coinbase]
        B -->|$9.85 after 1.5% fee| C[BTC Purchase]
        C -->|0.000219 BTC| D[Lightning Network]
        D -->|Instant transfer| E[User's AT Wallet]
        E -->|21.9 AT credited| F[Ready to Spend]
    end

    subgraph "IN-APP: Economy Flows"
        F -->|Order coffee| G[Merchant App]
        G -->|2 AT + 0.5 AT tip| H[Barista accepts]
        H -->|Releases order| I[User picks up]
        I -->|Quest completed| J[User earns 0.5 AT]
    end

    subgraph "OFF-RAMP: Merchant Cashes Out"
        K[Merchant AT Wallet] -->|50 AT| L[Lightning Network]
        L -->|0.0005 BTC| M[Coinbase Sell]
        M -->|$22.50 less fees| N[ACH Transfer]
        N -->|$21.98 net| O[Merchant Bank Account]
    end

    style A fill:#60A5FA
    style E fill:#10B981
    style F fill:#10B981
    style K fill:#FBBF24
    style O fill:#60A5FA
```

---

## Fee Transparency (Not Hidden)

```mermaid
graph LR
    subgraph "Buy $10 of AT"
        A1[Input: $10.00] --> A2[Coinbase: -$0.15]
        A2 --> A3[Lightning: -$0.01]
        A3 --> A4[Output: 21.9 AT]
    end

    subgraph "Sell 50 AT"
        B1[Input: 50 AT] --> B2[Lightning: -$0.01]
        B2 --> B3[Coinbase: -$0.34]
        B3 --> B4[Bank ACH: -$0.25]
        B4 --> B5[Output: $21.98]
    end
```

**Total Fees**: ~1.5% each way (compared to 2.9% + $0.30 for Stripe alone)

---

## First Friday User Journey

```mermaid
sequenceDiagram
    participant U as User (Phone)
    participant A as Art Walk App
    participant M as Merchant (Booth)
    participant B as Bank

    Note over U,B: ON-RAMP
    U->>A: Open app, tap "Add Funds"
    A->>U: Enter card, $20
    A->>A: Coinbase → BTC → Lightning
    A->>U: ✅ 43.8 AT credited

    Note over U,B: ART WALK ECONOMY
    U->>A: Scan QR at coffee booth
    A->>M: Order: Latte (3 AT)
    M->>U: ☕ Order ready!
    U->>A: Complete quest "Visit 3 booths"
    A->>U: +1.5 AT earned

    Note over U,B: OFF-RAMP
    M->>A: End of night: Cashout 50 AT
    A->>B: ACH $21.98 (1-3 days)
    B->>M: ✅ Funds deposited
```

---

## Key Differentiators vs PayPal/Venmo

| Feature | AT System | PayPal/Venmo |
|---------|-----------|--------------|
| Merchant fees | ~1.5% | 2.9% + $0.30 |
| Instant transfer | ✅ Lightning | ❌ 1-3 days |
| User earns rewards | ✅ Quest system | ❌ No |
| Provenance tracking | ✅ Ledger | ❌ No |
| Central control | ❌ P2P | ✅ Can freeze |
| KYC required | ❌ Optional | ✅ Mandatory |

---

## What's Built

- ✅ `core/fiat_bridge.py` - Full on/off ramp logic
- ✅ `core/inventory.py` - Item tracking with provenance
- ✅ `core/quest_system.py` - Quest posting/claiming
- ✅ `core/triple_verification.py` - 3-Witness Protocol
- ✅ API endpoints for all flows

## What Jules Builds

- 📱 Mobile quest browser
- 🗺️ Merchant map with QR codes
- 📸 Photo proof upload (Phase 2)

## What You Execute

- 🤝 Kern Art Council partnership
- 👥 5-10 merchant recruitment
- 📄 Flyer design + printing
- 🎥 Demo video for socials

---

*The full loop is ready. Card in, AT flows, bank out. All transparent, all sovereign.*
