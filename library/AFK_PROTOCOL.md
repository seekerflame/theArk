# 🛡️ AFK Protocol: Unattended Operation

**To the Builder:**
You are leaving the physical terminal. The Ark is designed to survive without you, but the physical machine must support it.

## 1. Physical Requirements

- **Power**: The machine must remain **ON**.
    - *Mac*: System Settings > Energy Saver > "Prevent computer from sleeping automatically when display is off".
    - *Laptop*: Ensure it is plugged in.
- **Network**: WiFi must remain connected.

## 2. Launch Sequence

Before you leave, run the permanence script:
```bash
cd THE_ARK_v0.7
./ESTABLISH_PERMANENCE.sh
```
once you see "THE ARK IS NOW AUTONOMOUS", you can close the terminal window.

## 3. Remote Monitoring

You can monitor the system from any device on your local network (Phone/Laptop):

- **URL**: `http://192.168.0.104:3000/web/gaia.html`
- **Console**: `http://192.168.0.104:3000/web/antigravity.html`

> [!IMPORTANT]
> Your phone must be connected to the **SAME WiFi Network** as this computer.
> If it doesn't load, check your Mac's firewall settings (`System Settings > Network > Firewall`).

## 4. What I Will Do

While you are gone, I (Antigravity) will:
1.  **Maintain the Ledger**: The `auto_operator` will continue ensuring the chain structure is healthy.
2.  **Sync Knowledge**: The `ark_steward` will push any local changes to the Wiki every 5 minutes.
3.  **Evolve**: The "Evolution Cycle" count in the console will grow, marking the passage of autonomous time.

**Go build IRL. I have the watch.**
