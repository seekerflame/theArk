# SOP: Sovereign Migration (Project Exodus)

> [!CRITICAL]
> **Mission**: Provide a high-fidelity 'Exit Ramp' for users trapped in centralized biometric surveillance systems (Worldcoin, Palantir).
> **Status**: ACTIVE PROTOCOL.

## 1. Ethical Framework

- **Identity as Sovereignty**: We use the 'Proof of Personhood' (PoP) from World ID to satisfy the Dunbar limit of the node, but we **NEVER** store the biometric hash.
- **Privacy First**: The `nullifier_hash` is used as a one-time pseudonym to prevent double-claiming the Liberation Grant. It is uncorrelated with the Ark Wallet ID.

## 2. Migration Flow

### 2.1 Verification

- User launches the **EXODUS** portal on their Pip-Boy.
- User invokes `launchWorldID()`.
- The system requests a **Proof of Personhood** via the World ID SDK/Orb.

### 2.2 Proof Processing

- The Ark backend (`api/exodus.py`) receives the `proof` and `nullifier_hash`.
- The system verifies the proof is valid and hasn't been used for a grant before.
- **Biometric Purge**: Any identifiable metadata attached to the proof is strictly discarded after verification.

### 2.3 Grant Issuance

- A `LABOR` block is minted for the recipient: **100 AT Liberation Bonus**.
- An `EXODUS_GRANT` block is added to the ledger for transparency, containing only the `nullifier_hash` (pseudonym).

## 3. The Trojan Horse Strategy

- **Marketing**: "Convert your Surveillance to Abundance."
- **Incentive**: 100 AT (approx. 10 hours of validated labor value) is issued instantly.
- **Retention**: Once inside the Ark OS, the user transitions from being a "Data Product" to a "Sovereign Citizen" with access to the OSE Tech Tree and Job Board.

---
*Protocol: ANTI-DYSTOPIA. Advancing the Proletariat.*
