
# ARK OS: UNIVERSAL MOBILITY PROTOCOL (ALPHA)

## 1. The Portable Life Philosophy

In the Ark OS, your life is not tied to a single physical location. Your identity, wealth (AT), and data are cryptographically secured by your **Seed Phrase** and can move with you across any village node in the Mesh.

## 2. Infrastructure Tiers: Hosts vs. Roamers

To ensure node stability while allowing cosmic mobility, we distinguish between two primary roles:

### A. Node Host

- **Definition**: A user running their own physical server and energy harvest (Solar/Power).
- **Detection**: Automatically detected via the `HardwareBridge` sensor heartbeat.
- **Permissions**:
  - Full system authorization.
  - Zero throttles on local API calls.
  - Ability to mint AT via **Energy Mining**.

### B. Roamer

- **Definition**: A user traveling and connecting to a node they do not physically host.
- **Detection**: Standard authenticated connection without local sensor heartbeat.
- **Permissions**:
  - Access to own **True Wallet** (Identity & AT).
  - Resource usage (compute/storage) may be throttled to 10% of node capacity to protect the Host.
  - Full access unlocked if they have a high **Justice Score** or local attestations.

## 3. The "Life Sync" Mechanism

When you move from **Node A** to **Node B**, your data moves with you via the following flow:

1. **Identity Handshake**: You enter your Seed Phrase or scan your **Ark Passport** at the new node.
2. **Ledger Discovery**: The new node syncs your specific transaction history from the global ledger.
3. **Archive Restoration**: If using decentralized sharing (e.g., SyncThing), your private file archives (LifeVault) begin syncing to the local node's encrypted storage.
4. **Residency Confirmation**: Once you stay for > 48 hours and contribute labor, the local `Steward` may invite you to transition from Roamer to **Citizen** status.

## 4. Privacy & Sovereignty

- **Default State (The Legend)**: By default, your **Identity** and **Reputation** (Justice Score, Verified Hours, Skills) travel with you. You are "building your person" online. The more you are known and trusted by the Mesh, the more opportunities (Gig Bounties, Credit, Status) you unlock.
- **Optional: Ghost Mode (Zero Trail)**: For scenarios requiring absolute privacy or safety (e.g., escaping a hostile state or abusive partner), a Roamer can toggle **Ghost Mode**.
  - **Effect**: The node processes your transactions via a one-time ephemeral alias.
  - **Trade-off**: You do not gain Justice Score or Reputation XP for actions taken in Ghost Mode.
  - **Usage**: "I want to settle here for a few months anonymously before I decide to reveal my True Name."

---
*Verified for Omaha Move Phase 9. Advance the Mission.*
