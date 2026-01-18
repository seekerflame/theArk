# ESP32 Hardware Bridge - Physical Labor Proof

## Sensor Data → AT Tokens

### Hardware Requirements

- ESP32 DevKit (WiFi enabled)
- Sensors:
  - Solar panel voltage/current (INA219)
  - Water flow meter (YF-S201)
  - Temperature/humidity (DHT22)
  - Motion detector (PIR)
- MicroPython firmware

### Installation

```bash
pip install esptool
esptool.py --chip esp32 erase_flash
esptool.py --chip esp32 write_flash -z 0x1000 esp32-micropython.bin
```

### Sensor → Token Mapping

| Sensor | Metric | AT Reward |
|--------|--------|-----------|
| Solar Panel | 1 kWh generated | 5 AT |
| Water Pump | 100 gallons moved | 2 AT |
| Workshop Motion | 1 hour presence | 10 AT (manual verification) |
| Compost Temp | Optimal range (140-160°F) | 1 AT/day |

### Data Flow

```
ESP32 Sensor → HTTP POST → Village Node → Ledger Block
```

### Example: Solar Panel Monitoring

```python

# ESP32 MicroPython code

import network
import urequests
from machine import Pin, I2C
from ina219 import INA219

# Setup

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("OSE-Mesh", "password")

i2c = I2C(scl=Pin(22), sda=Pin(21))
ina = INA219(0.1, i2c)
ina.configure()

# Main loop

while True:
    voltage = ina.voltage()
    current = ina.current()
    power = voltage * current / 1000  # Watts

    # If generating >100W, log to ledger

    if power > 100:
        data = {
            "sensor_id": "solar_panel_01",
            "type": "SOLAR_GEN",
            "power_w": power,
            "timestamp": time.time()
        }

        try:
            r = urequests.post("http://100.68.49.108:3000/api/hardware", json=data)
            print(f"Logged: {power}W")
        except:
            print("Network error, caching...")

    time.sleep(60)  # Check every minute
```

### Backend API

```python

# Add to server.py

@app.route('/api/hardware', methods=['POST'])
def hardware_data():
    data = request.json
    sensor_type = data.get('type')

    # Convert sensor data to AT

    if sensor_type == 'SOLAR_GEN':
        kwh = data['power_w'] / 1000
        at_earned = kwh * 5

        # Mint tokens for infrastructure owner

        mint_block({
            "username": "OSE-Infrastructure",
            "task": f"Solar generation: {kwh:.2f} kWh",
            "hours": kwh,  # Equivalent labor value
            "sensor_proof": data
        })

    return {"status": "success"}
```

### Security

- **Tamper Detection**: Sensor data signed with device key
- **Rate Limiting**: Max 1 submission per sensor per minute
- **Human Verification**: High-value events (>50 AT) require oracle approval

### Future Sensors

- Biogas production (methane meter)
- Soil moisture (capacitive sensor)
- Machine runtime (hall effect on rotating parts)
- Rainwater harvesting (tipping bucket)

---

**Status:** DESIGN COMPLETE - Hardware testing required
