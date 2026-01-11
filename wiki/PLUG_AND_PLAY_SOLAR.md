
# ARK OS: PLUG & PLAY SOLAR BASELINE

This guide provides the physical blueprint for achieving $0/month living by linking your server to the sun.

## 1. The Physical Stack (Stone Schedule)

To reach self-sufficiency for a single node (up to 3 people), we recommend the following "Plug & Play" kit:

### A. Energy Capture

- **Solar Panel**: 1x 400W Monocrystalline Panel (Rigid or Flexible).
- **Mounting**: Ground mount or southern-facing roof.

### B. Energy Storage

- **Battery**: 1x 100Ah 12V LiFePO4 Battery with BMS.
- **Charge Controller**: Victron SmartSolar MPPT 100/20 (This model is natively supported by the Ark Hardware Bridge).

### C. The Ark Server

- **Hardware**: Mac Mini (M1/M2) or Raspberry Pi 5.
- **Bridge**: USB-to-VE.Direct cable (connects MPPT to the Server).

## 2. Software Integration (Ark OS)

Once your hardware is wired, plug the USB bridge into your Ark Server:

1. **Activate Sensor**: Navigate to the **Admin Deck** -> **Hardware Monitor**.
2. **Enable Mining**: Select 'SOLAR_MINING' and map it to the Victron sensor.
3. **Set Quotient**: Link your 'People Count' to the Calorie Ratio logic.

## 3. The Abundance Loop

- **Energy In**: The sun charges the battery.
- **Data In**: The Ark OS reads the MPPT telemetry.
- **AT Out**: The system mints Abundance Tokens (AT) directly into your **True Wallet** based on the energy produced and stored.

> [!TIP]
> **Minecraft for Real Life**: Think of this as your "Power Generator" block. Once placed and plugged, it generates resources (AT) passively, allowing you to focus on 'Grinding' higher-level missions in the Academy or Care Swarms.

---
*Created as part of the Omaha Move. Verified for Alpha 1.5.*
