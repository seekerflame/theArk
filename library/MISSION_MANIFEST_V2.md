# 📜 MISSION MANIFEST v2: The Path to Type 6

**Strategic Directives for Jules & Antigravity**
*Generated based on FBCC (Future Builders Crash Course) & FBA (Future Builders Academy) Alignment.*

## 🏗️ PHASE 1: INFRASTRUCTURE & FOUNDATION (Immediate Impact)
*Goal: Fix broken loops and establish a robust baseline for automation.*

1.  **[API] Feedback Loop Completion**: Implement `/api/feedback` to capture user reports directly into the Ledger. (✅ DONE)
2.  **[API] Federation Discovery**: Implement `/api/federation/villages` to serve dynamic peer data to the map (currently mocked in `app.js`).
3.  **[CORE] Hardware Bridge V2**: Upgrade `hardware_bridge.py` to support bi-directional control (e.g., turning a relay ON via API).
4.  **[DATA] Task Auto-Generation**: Create `tools/import_fbcc.py` to parse `web/fbcc_roles.json` and auto-populate the Job Board ledger.
5.  **[UX] Overclock UI Sync**: Update `web/hardware_monitor.js` to visualize the "Overclock" state (e.g., faster animations or red glow).

## 🧠 PHASE 2: INTELLIGENCE & AUTOMATION (The Steward)
*Goal: Evolve the "Steward" from a chatbot to an autonomous agent.*

6.  **[AI] Code Proposal Agent**: Upgrade `api/steward.py` to allow the Steward to draft actual git patches for simple requests.
7.  **[AI] Ledger Analysis**: Create a background job that analyzes ledger "Labor" blocks and suggests efficiency improvements.
8.  **[AI] Automated Testing**: The Steward should run `pytest` on the codebase daily and report regressions to the "Chronicle".
9.  **[SYS] Self-Healing**: Implement a watchdog that restarts the `sensor_polling_loop` if it crashes (improve `server.py` robustness).
10. **[KNOWLEDGE] Wiki-Ledger Sync**: Automate the export of Ledger "Chronicle" events to a local Markdown Wiki file for readability.

## 💰 PHASE 3: ECONOMY & SOVEREIGNTY (Mycelium)
*Goal: Harden the economic engine and resource tracking.*

11. **[ECO] Resource Decay**: Implement logic where "Water" and "Heat" buffers decay over time, generating "Emergency" quests automatically.
12. **[ECO] Dynamic Pricing**: Update `api/store` to adjust item prices based on scarcity (Ledger supply vs. demand).
13. **[WALLET] Peer-to-Peer Transfer UI**: Build a frontend modal for `/api/transfer` to enable easy user-to-user AT transactions.
14. **[FED] Cross-Node Trading**: Protocol design for trading AT/Resources between different Ark nodes (Federated Ledger).
15. **[SEC] Role-Based Auth**: Enforce strictly that only `Maslow Prime` role can verify `CRITICAL` tasks (update `api/economy.py`).

## 🌌 PHASE 4: TYPE 6 EVOLUTION (Long-Term)
*Goal: Prepare the software for multi-generational, interstellar durability.*

16. **[CORE] IPFS / Torrent Backup**: Integrate a decentralized storage mechanism for the `village_ledger.db` backups.
17. **[SIM] Kardashev Calculator V2**: Refine `core/energy.py` to use real sensor data (if available) mixed with simulation for a truer K-Level.
18. **[UI] 3D Tangle Visualization**: Replace the 2D canvas graph with a Three.js 3D representation of the block DAG (Tangle).
19. **[GAME] "The Game of Life"**: Implement a cellular automata simulation on the dashboard that evolves based on system health.
20. **[META] Quine-Self-Replication**: A script that packages the entire `ark-os` into a single installable ISO/Script for new nodes.

---
**Status**: Phase 1 Active.
**Next Directive**: Execute Task #2 (Federation Discovery).
