# LoRa Mesh Network - Disaster-Proof Communications

## Long-Range Radio for Village-to-Village Coordination

### Hardware

- **LoRa Module**: SX1276/SX1278 (915MHz for North America, 868MHz for Europe)
- **Microcontroller**: ESP32 or Raspberry Pi Pico
- **Antenna**: 3dBi omni-directional (outdoor mounting recommended)
- **Power**: Solar + Li-Ion battery (autonomous operation)

### Specifications

- **Range**: Up to 10km line-of-sight
- **Data Rate**: 300bps - 50kbps (configurable)
- **Frequency**: 915MHz (ISM band, license-free)
- **Encryption**: AES-256 for all messages

### Use Cases

1. **Emergency Coordination** - Natural disasters, grid down
2. **Quest Notifications** - "New quest available at Village B"
3. **Trade Alerts** - "Village C has surplus tomatoes"
4. **Ledger Sync** (slow but reliable fallback)

### Network Topology

```
Village A (Gateway)  ─┬─  Village B (Relay)
                      │
                      ├─  Village C (Edge Node)
                      │
                      └─  Village D (Edge Node)
```

### Message Protocol

```json
{
  "from": "village-a-node-01",
  "to": "village-b-node-01",
  "type": "QUEST_ALERT",
  "payload": {
    "quest_id": "seh7_023",
    "bounty_at": 40,
    "urgent": false
  },
  "timestamp": 1703462400,
  "signature": "..."
}
```

### Arduino/ESP32 Code Starter

```cpp

#include <SPI.h>

#include <LoRa.h>

#define LORA_FREQUENCY 915E6

#define LORA_BANDWIDTH 125E3

#define LORA_SPREAD_FACTOR 7

void setup() {
  Serial.begin(115200);

  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("LoRa init failed!");
    while (1);
  }

  LoRa.setSpreadingFactor(LORA_SPREAD_FACTOR);
  LoRa.setSignalBandwidth(LORA_BANDWIDTH);
  LoRa.enableCrc();

  Serial.println("LoRa Mesh Node Online");
}

void loop() {
  // Listen for messages
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String message = "";
    while (LoRa.available()) {
      message += (char)LoRa.read();
    }
    Serial.println("Received: " + message);

    // Parse and forward to local server
    // POST to http://localhost:3000/api/lora
  }

  // Check for outbound messages
  if (Serial.available()) {
    String outbound = Serial.readStringUntil('\n');
    LoRa.beginPacket();
    LoRa.print(outbound);
    LoRa.endPacket();
    Serial.println("Sent: " + outbound);
  }

  delay(100);
}
```

### Integration with Village Node

```python

# Add to server.py

@app.route('/api/lora', methods=['POST'])
def lora_message():
    data = request.json
    msg_type = data.get('type')

    if msg_type == 'QUEST_ALERT':

        # Add quest to local board

        quest_id = data['payload']['quest_id']
        logToTerminal(f"[LORA] New quest from network: {quest_id}")

    elif msg_type == 'LEDGER_SYNC':

        # Merge remote blocks

        blocks = data['payload']['blocks']
        merge_blocks(blocks)

    return {"status": "received"}
```

### Deployment Checklist

- [ ] Mount antenna at highest point (roof/tower)
- [ ] Configure frequency (check local regulations)
- [ ] Test range with handheld transceiver
- [ ] Set up solar charging circuit
- [ ] Weatherproof enclosure
- [ ] Register node in village network map

### Future Enhancements

- **Meshtastic Integration** - Use existing Meshtastic protocol
- **Satellite Fallback** - Iridium for truly remote locations
- **Store-and-Forward** - Automatic message relay when villages are offline

---

**Status:** DESIGN COMPLETE - Hardware procurement needed
