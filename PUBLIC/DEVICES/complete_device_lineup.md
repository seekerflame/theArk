# 📱 COMPLETE 9-DEVICE LINEUP: Production Blueprints

**Status**: PLANNING PHASE  
**Goal**: Production-ready specs for complete sovereignty stack  
**Integration**: OSE machines + Liz platform + salvage culture

---

## 🎯 DEVICE HIERARCHY

### Tier 1: Personal Sovereignty (4 devices)

1. **Pip-Boy** - Wearable coordinator (✅ COMPLETE)
2. **Mesh Router (Personal)** - Pocket mesh node
3. **Sovereign Camera** - Privacy-first documentation
4. **Solar Charger (Personal)** - Portable power bank

### Tier 2: Home Sovereignty (3 devices)

1. **Solar Station** - Household energy independence
2. **Hydroponic System** - Year-round food production
3. **Mesh Hub** - Home network backbone

### Tier 3: Community Sovereignty (2 devices)

1. **Fab Station** - Local manufacturing capability
2. **Water Station** - Village-scale water treatment

---

## 📋 TIER 1: PERSONAL DEVICES

### 1. Pip-Boy ✅

**Status**: Production blueprint complete  
**File**: `pipboy_v1_production_blueprint.md`  
**BOM**: $50  
**Key Features**: Neural interface, AR control, 7-day battery

---

### 2. MESH ROUTER (PERSONAL)

**Purpose**: Pocket-sized LoRa mesh node for extending network

**Specifications**:

- **Size**: 80mm × 50mm × 20mm (fits in pocket)
- **Power**: 18650 li-ion (3000mAh, 3 days runtime)
- **Range**: 5-10km LoRa
- **MCU**: ESP32 (same as Pip-Boy)
- **Cost**: $25-30

**Hardware**:

- ESP32-WROOM-32D
- SX1276 LoRa module
- 0.96" OLED display (status)
- 18650 battery + holder
- USB-C charging (TP4056)
- Antenna: 868/915MHz dipole

**Features**:

- Meshtastic firmware (compatible with Pip-Boy)
- Message relay (store-and-forward)
- Works as WiFi AP (bridge to regular internet)
- GPS module (optional, for positioning)

**Use Cases**:

- Hikers: Extend mesh to remote areas
- Villages: Add nodes to increase coverage
- Emergencies: Deploy quickly for disaster comms

**OSE Fabrication**:

- PCB: CNC Circuit Mill
- Enclosure: 3D Printer (PETG, waterproof)
- Antenna: Laser cut + solder

**Assembly Time**: 2 hours  
**Difficulty**: Beginner (kit version available)

---

### 3. SOVEREIGN CAMERA

**Purpose**: Privacy-first photo/video for documentation (no cloud upload)

**Specifications**:

- **Sensor**: 5MP OV5640 (image) + OV2640 (video)
- **Storage**: MicroSD (up to 128GB)
- **Battery**: 2000mAh LiPo (4 hours video, 500 photos)
- **Display**: 2.4" TFT (preview)
- **Cost**: $35-40

**Hardware**:

- ESP32-CAM module
- OV5640 camera sensor
- 2.4" ILI9341 TFT display
- MicroSD slot
- 2000mAh LiPo + charger
- Enclosure: 3D printed (camera mount)

**Privacy Features**:

- **No cloud**: All data stays on SD card
- **Manual shutter**: Physical button (not always-on)
- **Encryption**: AES-256 on-device (optional)
- **Timestamp**: Local only (no GPS leak)

**Modes**:

1. Photo (2592×1944, JPEG)
2. Video (1280×720, 30fps, H.264)
3. Timelapse (configurable interval)
4. QR scanner (for Pip-Boy pairing)

**Integration with Pip-Boy**:

- BLE transfer: Photos → Pip-Boy → Mesh sync
- NFC tap: Transfer ownership/metadata
- Shared timestamps for event logging

**OSE Fabrication**:

- PCB: Circuit Mill (custom ESP32-CAM board)
- Lens mount: 3D Printer (adjustable focus)
- Case: CNC or 3D print (ruggedized)

**Assembly Time**: 1.5 hours  
**Difficulty**: Beginner-Intermediate

---

### 4. SOLAR CHARGER (PERSONAL)

**Purpose**: Portable power bank with solar for off-grid device charging

**Specifications**:

- **Solar**: 10W foldable panel
- **Battery**: 10,000mAh LiPo (37Wh)
- **Outputs**: 2× USB-A, 1× USB-C PD
- **Charge time**: 8-10 hours (solar), 3 hours (wall)
- **Cost**: $30-35

**Hardware**:

- 10W solar panel (monocrystalline, foldable)
- 3S LiPo pack (10Ah, 11.1V)
- BMS (battery management system)
- Buck converter (USB 5V output)
- USB-C PD controller (18W out)

**Features**:

- Charges Pip-Boy, mesh router, camera simultaneously
- LED indicator (battery %, solar input)
- Weatherproof (IP65)
- Carabiner loop (attach to backpack)

**Use Cases**:

- Hiking: Keep Pip-Boy charged for week-long trips
- Village work: Power tools in remote locations
- Emergency: Solar charging when grid fails

**OSE Fabrication**:

- Enclosure: 3D Printer (ABS, UV resistant)
- Panel mount: Laser cut acrylic or wood
- Wiring: Basic soldering

**Assembly Time**: 1 hour  
**Difficulty**: Beginner

---

## 📋 TIER 2: HOME DEVICES

### 5. SOLAR STATION

**Purpose**: Household energy independence (300W continuous)

**Specifications**:

- **Solar**: 400W panel (4× 100W)
- **Battery**: 200Ah LiFePO4 (2.56kWh)
- **Inverter**: 1000W pure sine wave
- **Charge controller**: MPPT 30A
- **Runtime**: 8 hours @ 300W load
- **Cost**: $600-750

**Hardware**:

- 4× 100W monocrystalline panels
- 200Ah LiFePO4 battery (4S configuration)
- MPPT charge controller (Victron or generic)
- 1000W inverter (12V → 120V AC)
- BMS (battery protection)
- Monitoring display (voltage, current, SOC)

**Loads Powered**:

- Mesh hub (5W continuous)
- Refrigerator (100W avg)
- LED lighting (50W)
- Laptop charging (60W)
- Phone charging (10W)
- Reserve: 75W for surge

**Integration with Liz Platform**:

- ESP32 monitoring module
- Reports energy production/consumption to village mesh
- Community can see available power capacity
- Enables energy sharing

 (peer-to-peer grid)

**OSE Fabrication**:

- Panel mounts: Metal Roller (aluminum framing)
- Battery enclosure: CNC or welding
- Wiring: Standard electrical (follow code)

**Assembly Time**: 8-12 hours  
**Difficulty**: Intermediate (electrical knowledge required)

---

### 6. HYDROPONIC SYSTEM

**Purpose**: Year-round food production (80 plants, 20kg/month yield)

**Specifications**:

- **Type**: NFT (Nutrient Film Technique)
- **Capacity**: 80 plant sites
- **Footprint**: 2m × 1m × 2m (vertical)
- **Water**: 100L reservoir (recirculating)
- **Power**: 50W (pump + LED grow lights)
- **Cost**: $200-300

**Hardware**:

- PVC pipes (NFT channels, 4" diameter)
- Water pump (12V, 800L/hr)
- LED grow lights (50W full spectrum)
- 100L food-grade reservoir
- Timer (pump cycles)
- pH/EC sensors (optional)
- Arduino/ESP32 controller

**Plants Grown**:

- Lettuce, kale, spinach (leafy greens)
- Tomatoes, peppers (fruiting plants)
- Herbs (basil, cilantro, parsley)

**Automation**:

- Auto pH adjustment (dosing pumps)
- Water level sensor (refill alerts)
- Light schedule (16h on, 8h off)
- Temperature monitoring

**Integration with Liz Platform**:

- Harvest tracking (kg/week)
- Surplus sharing (extra lettuce? Post to mesh)
- Nutrient recipe sharing (community knowledge)

**OSE Fabrication**:

- PVC cutting: Sawmill or manual
- Frame: Welded steel or wood
- Electronics: Circuit Mill (custom PCB)

**Assembly Time**: 6-8 hours  
**Difficulty**: Intermediate

---

### 7. MESH HUB (HOME)

**Purpose**: Household network backbone + village mesh gateway

**Specifications**:

- **Range**: 15km LoRa (with roof antenna)
- **Throughput**: 300kbps (aggregated)
- **Users**: 50-100 devices
- **Power**: 10W continuous
- **Uptime**: 99.9% (powered by solar station)
- **Cost**: $80-120

**Hardware**:

- Raspberry Pi 4 (4GB RAM)
- 2× SX1276 LoRa modules (redundancy)
- External antenna (roof-mounted, 6dBi)
- Gigabit Ethernet (LAN connection)
- 64GB SD card (OS + data)
- 12V to 5V buck converter

**Services**:

- **Meshtastic**: Village mesh routing
- **Automerge sync**: Liz platform backend
- **IPFS node**: Decentralized file storage
- **Local DNS**: .mesh domains
- **HTTPS proxy**: Secure mesh web apps

**Features**:

- Offline Wikipedia mirror (Kiwix)
- Village chat (Matrix server)
- Shared calendar (Radicale)
- File sharing (Nextcloud)

**Integration with Liz Platform**:

- Hosts village Automerge server
- DID resolver (identity lookups)
- Resource matchmaker backend

**OSE Fabrication**:

- Enclosure: 3D Printer (vented for RPi cooling)
- Antenna mount: Metal fab (mast + brackets)

**Assembly Time**: 3-4 hours  
**Difficulty**: Intermediate (Linux knowledge helpful)

---

## 📋 TIER 3: COMMUNITY DEVICES

### 8. FAB STATION

**Purpose**: Village-scale manufacturing (make Pip-Boys, tools, parts)

**Specifications**:

- **Machines**: 5 core OSE tools
- **Footprint**: 4m × 3m workshop space
- **Power**: 2kW peak (1kW avg)
- **Operators**: 2-3 trained villagers
- **Cost**: $3,000-5,000 (one-time)

**Equipment (OSE Machines)**:

1. **3D Printer** (OSE #29)
   - Build volume: 300×300×400mm
   - Material: PETG, PLA, ABS
   - Use: Enclosures, prototypes

2. **CNC Circuit Mill** (OSE #31)
   - PCB size: 200×300mm
   - Resolution: 0.1mm
   - Use: Pip-Boy PCBs, custom electronics

3. **Laser Cutter** (OSE #21)
   - Bed size: 600×400mm
   - Power: 40W CO2 laser
   - Use: Acrylic, wood, fabric (electrodes)

4. **CNC Torch Table** (OSE #24)
   - Bed size: 1200×2400mm
   - Material: Steel up to 12mm
   - Use: Metal chassis, brackets

5. **Metal Roller** (OSE #25)
   - Capacity: 16 gauge sheet metal
   - Use: Solar panel frames, enclosures

**Output Capacity**:

- 10 Pip-Boys/week
- 5 Mesh routers/week
- Custom parts on-demand

**Workflow**:

1. Design in FreeCAD/KiCad
2. Generate CAM files
3. Fabricate on appropriate machine
4. Assemble and test
5. Log in village ledger (contribution tracking)

**Integration with Liz Platform**:

- Fab queue (who needs what, when)
- Skill matching (who can operate CNC?)
- Time tracking (contribution credits)

**OSE Fabrication**:

- Build machines using OSE guides
- Workshop structure: CEB Press (OSE #1) bricks
- Power: Solar Station (Tier 2)

**Setup Time**: 2-3 months (with team)  
**Difficulty**: Advanced (requires machining skills)

---

### 9. WATER STATION

**Purpose**: Village-scale water treatment (1000L/day potable water)

**Specifications**:

- **Source**: Well, river, or rainwater collection
- **Output**: 1000L/day (50 people @ 20L/day)
- **Treatment**: Sand filter + UV + reverse osmosis
- **Storage**: 2000L tank (2-day reserve)
- **Power**: 200W (pump + UV)
- **Cost**: $800-1,200

**Components**:

1. **Intake pump** (submersible or surface)
2. **Sand filter** (removes sediment)
3. **Activated carbon** (chlorine, odor)
4. **UV sterilizer** (kills bacteria/viruses)
5. **RO membrane** (optional, for very contaminated sources)
6. **Storage tank** (food-grade 2000L)

**Monitoring**:

- ESP32 + sensors
- TDS meter (total dissolved solids)
- pH sensor
- Flow meter (liters dispensed)
- Tank level (ultrasonic sensor)

**Distribution**:

- Gravity-fed (tank on elevated platform)
- Multiple taps (communal access)
- Optional: Pipe to households

**Integration with Liz Platform**:

- Water usage tracking (per household)
- Filter replacement alerts (community notification)
- Surplus/shortage announcements

**OSE Fabrication**:

- Tank: Custom welding or purchase
- Filter housing: 3D Printer (PLA, food-safe coating)
- Piping: PVC (manual cutting)
- Platform: Wood or CEB Press bricks

**Setup Time**: 1-2 weeks  
**Difficulty**: Intermediate (plumbing + electrical)

---

## 📊 COMPLETE BOM SUMMARY

| Tier | Device | BOM Cost | OSE Machines Used | Assembly Time |
|------|---------|----------|-------------------|---------------|
| 1 | Pip-Boy | $50 | #29, #31, #21 | 4h |
| 1 | Mesh Router (Personal) | $30 | #29, #31 | 2h |
| 1 | Sovereign Camera | $40 | #29, #31 | 1.5h |
| 1 | Solar Charger | $35 | #29, #21 | 1h |
| 2 | Solar Station | $700 | #25, #24 | 12h |
| 2 | Hydroponic System | $250 | #29 (optional) | 8h |
| 2 | Mesh Hub | $100 | #29 | 4h |
| 3 | Fab Station | $4,000 | N/A (builds itself) | 2-3 months |
| 3 | Water Station | $1,000 | #29, welding | 1-2 weeks |

**Total for complete personal sovereignty**: $155 (Tier 1 only)  
**Total for household sovereignty**: $1,205 (Tier 1 + 2)  
**Total for village sovereignty**: $6,205 (all 3 tiers)

---

## 🔗 DEVICE INTEGRATION MATRIX

| Device | Connects To | Protocol | Data Shared |
|--------|-------------|----------|-------------|
| Pip-Boy | All devices | LoRa, BLE, NFC | Commands, status, messages |
| Mesh Router | Pip-Boy, Mesh Hub | LoRa | Message relay, GPS |
| Camera | Pip-Boy | BLE, NFC | Photos, videos, timestamps |
| Solar Charger | Pip-Boy, Camera, Router | USB | Power only |
| Solar Station | Mesh Hub | WiFi/LoRa | Energy production/usage |
| Hydroponics | Mesh Hub | WiFi | Harvest data, sensor readings |
| Mesh Hub | All Tier 1+2 | LoRa, Ethernet | Automerge sync, IPFS, Matrix |
| Fab Station | Mesh Hub | Ethernet | Fabrication queue, logs |
| Water Station | Mesh Hub | WiFi | Usage, TDS, alerts |

**Liz Platform Integration**:

- All devices report to Mesh Hub
- Mesh Hub runs Automerge backend
- Village dashboard shows all metrics
- Mutual aid coordination uses real-time data

---

## 🎯 WHAT THIS ENABLES

### Individual Level (Tier 1)

- Off-grid communication (mesh router)
- Personal documentation (camera, no cloud)
- Energy independence (solar charger)
- Coordination (Pip-Boy)

### Household Level (Tier 2)

- Energy independence (solar station)
- Food production (hydroponics)
- Network backbone (mesh hub)

### Village Level (Tier 3)

- Local manufacturing (fab station)
- Water security (water station)
- Complete supply chain autonomy

**Result**: Zero dependence on external infrastructure

---

*"Nine devices. Three tiers. Complete sovereignty."*

**Next**: Create master fabrication tasklist.
