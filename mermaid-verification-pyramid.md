```mermaid
graph TD
    A[User Posts Content] --> B{AI Pre-Screen}
    B -->|Clean| C[Published]
    B -->|Flagged| D[Queue for Review]
    
    D --> E[Level 1: Oracles Review]
    E -->|8/10 Vote Ban| F[Temporary Suspension]
    E -->|<8/10| C
    
    F --> G[User Appeals]
    G --> H[Level 2: Meta-Oracles Audit]
    H -->|Overturn| I[Restore + Compensate]
    H -->|Uphold| J[Community Court]
    
    J --> K[9 Random Users Vote]
    K -->|7/9 Overturn| I
    K -->|<7/9| L[Permanent Ban]
    
    L --> M[Transparency Log]
    M --> N[Public Record]
    
    C --> O[Recursive Audit System]
    O --> P{Audit Trigger}
    P -->|Low Count: 10%| Q[Random Sample]
    P -->|Med Count: 50%| R[Half Audited]
    P -->|High Count: 100%| S[All Audited]
    
    Q --> T[Meta-Oracle Reviews Oracle]
    R --> T
    S --> T
    
    T -->|Fraud Detected| U[Slash Oracle Stake]
    T -->|Clean| V[Oracle Reputation +1]
    
    U --> W[Oracle Banned]
    W --> X[Community Vote on Replacement]
    
    V --> Y[Oracle Continues]
    
    style A fill:#90EE90
    style L fill:#FFB6C1
    style I fill:#87CEEB
    style U fill:#FF6B6B
    style V fill:#98FB98
```

# Recursive Verification Flow

**Key Innovation:** Verify-to-Earn with Inverted Incentive

- **More power → More scrutiny**
- **Higher verification count → Higher audit frequency**
- **Prevents concentration → Forces distribution**

**Layers:**

1. Users (verified by Oracles)
2. Oracles (verified by Meta-Oracles)
3. Meta-Oracles (verified by Community)
4. Community (verified by Transparency)
5. Transparency (verified by Code)

**Exit at Every Level:**

- Disagree with ban → Appeal
- Disagree with appeal → Fork
- Disagree with node → Leave
- Disagree with network → Start new one

*"Trust is earned recursively. Power is checked automatically. Exit is always available."*
