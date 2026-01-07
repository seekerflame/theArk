from core.config import Config

# Ark OS Hardware Simulation
# Emulates Solar, Water, and Motion sensors providing "Civilization Proofs"

SERVER = Config.get('SERVER', "localhost:3000")
TOKEN = Config.get('HARDWARE_TOKEN', "GAIA_PROTO_SIM_2026")

def post_hardware_event(sensor_id, s_type, value):
    try:
        conn = http.client.HTTPConnection(SERVER)
        payload = json.dumps({
            "sensor_id": sensor_id,
            "type": s_type,
            "value": value,
            "at_earned": 1.0, # Energy Generation = AT Minting
            "timestamp": time.time()
        })
        headers = {
            'Content-Type': 'application/json',
            'X-Hardware-Secret': 'ARK_HW_001'
        }
        conn.request("POST", "/api/hardware", payload, headers)
        response = conn.getresponse()
        data = response.read().decode()
        print(f"📡 [HARDWARE] Sensor {sensor_id} ({s_type}) -> {value}. Response: {data}")
        conn.close()
    except Exception as e:
        print(f"❌ [HARDWARE] Error: {e}")

if __name__ == "__main__":
    print("🔋 Starting Ark OS Hardware Simulator...")
    print("---------------------------------------")
    
    sensors = [
        {"id": "SOLAR_01", "type": "ENERGY", "base": 500, "range": 50},
        {"id": "WATER_01", "type": "YIELD", "base": 100, "range": 10},
        {"id": "HVAC_01", "type": "EFFICIENCY", "base": 98, "range": 2}
    ]

    try:
        while True:
            for s in sensors:
                val = s['base'] + random.uniform(-s['range'], s['range'])
                post_hardware_event(s['id'], s['type'], round(val, 2))
                time.sleep(random.randint(5, 15))
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")
