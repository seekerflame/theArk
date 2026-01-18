# SOP: CRP_001 - The Spore Protocol (Community Replication)

> [!IMPORTANT]
> **Core Concept**: To scale the federation, the barrier to entry must be near zero. OSE must be "Easy to Boot, Hard to Break."

## 1. The 5-Minute Boot Strategy

We share the Civilization OS by providing a "Spore" – a pre-configured node environment.

### 1.1 The Distribution Stack

- **The Spore Image (Docker)**: A single `docker-compose.yml` that boots the Ark Backend, Gaia Frontend, and NetBird Mesh VPN in one command.
- **The Bare Metal ISO**: A custom Linux distribution (OSE-OS) that turns any old laptop into a dedicated Survival Node.
- **The Git Mycelium**: A public repository containing the core SOPs and code, allowing for rapid "Fork and Boot" by the open-source community.

## 2. Replication Steps (For New Users)

1. **Clone the Spore**: `git clone https://github.com/ose-ecology/spore-protocol`
2. **Execute Boot**: `./boot_node.sh`
3. **Identity Genesis**: The system prompts the user to generate their 12-word seed phrase (Sovereign Wallet).
4. **Mesh Handshake**: The new node automatically looks for peer nodes via NetBird and joins the federation.

## 3. Shared Economic Incentives

- **Zero-Barrier AT Minting**: New nodes come with a "Genesis Bounty" of 10 AT to encourage initial trade and labor validation.
- **Federation Rewards**: Nodes that share high-density data (e.g., successful soil protocols) are rewarded with "Mastery XP" in the global Tech Tree.

## 4. Scaling through Dunbar Mitigation

When a community reaches 150 members, the Spore Protocol triggers a **Node Mitosis**:

- **Step 1**: The ledger is snapshotted.
- **Step 2**: 50% of the members move to a new subnet (New Node).
- **Step 3**: The two nodes remain federated but operate their own local governance, preventing the "Orwellian Trap" of centralized control.

---
*Status: READY FOR REPLICATION*
