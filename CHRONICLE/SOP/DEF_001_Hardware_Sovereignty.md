# SOP: DEF_001 - Hardware & State Sovereignty

> [!CAUTION]
> **Primary Threat**: Modern CPU hardware (Intel/AMD/ARM) contains "Ring -3" management engines (Intel ME / AMD PSP) that operate independently of the OS and can be used for remote surveillance or "Kill Switch" activation.

## 1. Neutralizing the Management Engine

To achieve absolute sovereignty, we must assume the silicon is compromised.

### 1.1 Intel ME / AMD PSP Mitigation

- **Me_cleaner**: For older Intel nodes, use `me_cleaner` to strip the Intel Management Engine firmware.
- **HAP Bit**: For newer nodes (Skylake+), set the High Assurance Platform (HAP) bit to disable the ME after boot.
- **Sovereign Silicon Project**: LONG-TERM: Migration to Open-Source ISA (RISC-V) hardware (e.g., Pine64, StarFive) where the design is auditable.

### 1.2 Encrypted Persistent Memory

- **The "Burn" Protocol**: If a node detects physical tampering (case opening, unauthorized BIOS change), it triggers a secure wipe of the ledger keys and enters **Static Mode**.
- **Cold Storage Sync**: The node's primary keys should exist on physical, non-networked storage (MicroSD/USB) that is only inserted for critical updates.

## 2. State-Level Suppression Defense

How to survive if a nation-state attempts to disconnect or seize the mesh.

### 2.1 P2P Obfuscation

- **Beyond NetBird**: Implement **WireGuard + ShadowSocks** or **Tor Snowflake** to hide OSE traffic as generic HTTPS.
- **Meshnet Fallback**: If global internet is killed, the node enters **LoRa/Satellite Mode**. Use Meshtastic/LoRa nodes to maintain slow-speed (text/ledger) sync within a 10km radius.

### 2.2 Biological Camouflage

- **Stealth Nodes**: A node shouldn't look like a server. It should look like a "Solar Charge Controller" or a "Smart Irrigation Hub."
- **Distributed Compute**: The OS logic is split across multiple small devices (Esp32, Raspberry Pi, Mac Mini). No single "Brain" to seize.

## 3. "Arms Damage" / Direct OS Hardening

- **ReadOnly Root**: The core OS files are stored on a Read-Only partition. Malware cannot overwrite the kernel.
- **Capability-Based Security**: Processes only have the specific permissions they need (e.g., the Wallet *cannot* use the camera; the Camera *cannot* access the ledger).

---
*Status: DEFENSIVE IMMUNITY ENGAGED*
