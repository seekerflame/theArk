# SOP: SEC_001 - Mesh Immunity (Anti-Malware & Security)

> [!CAUTION]
> **Core Concept**: The Mesh is a biological-style network. We don't use "Firewalls"; we use an **Immune System**.

## 1. Malware Resistance

Because the OS runs on localized nodes, a single infected node must not be able to "decapitate" the federation.

### 1.1 Sandboxed Execution

- **Module Isolation**: UI modules (Gaia) run in a sandboxed browser environment with zero access to the node's filesystem unless explicitly granted via a **Sovereign Handshaking** protocol.
- **Python Hardening**: `The_Ark` (backend) uses a "White List Only" approach for system calls.

### 1.2 Binary Verification

- Every system upgrade (`SYSTEM_UPGRADE` block) must be cryptographically signed by an **Oracle Swarm** (Consensus of at least 7 trusted nodes).
- Automated check: If the hash of a core file changes without a corresponding verified block, the node enters **Safe Mode** (Life support only, network disabled).

## 2. Ransomware Defense

The "Abundance Token" ledger is append-only and immutable. It cannot be "encrypted" or "locked" by external actors because every node holds a partial or full redundant copy.

- **Redundancy**: If a node's local database is corrupted, it performs a **Rhizome Restore** from three peer nodes.
- **Sovereign Keys**: Your private key is stored in a **Hardware-Bound** way (or seed phrase). No "Admin" can reset your password; therefore, no hacker can take over your identity via central servers.

## 3. Malicious Logic (Sybil Attacks)

How we prevent one person from creating 1000 fake nodes to steal AT:

- **Proof of Presence**: Minting AT requires a **Peer-to-Peer Handshake** or a **Photo Proof** validated by a human Oracle.
- **Dunbar Limiting**: A node cannot scale past 150 people. Attempting to grow further triggers a **Mitosis Event**, creating a separate ledger that is independent but federated. Large-scale malicious takeover is mathematically disincentivized.

---
*Status: ACTIVE IMMUNE SYSTEM*
