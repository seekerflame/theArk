import time
import json
import random
import argparse
import requests
import sys
import socket

# Defaults
DEFAULT_SERVER = "http://localhost:3000/api/hardware"
DEFAULT_POLL_INTERVAL = 5

class Sensor:
    def __init__(self, device_id, sensor_suffix, sensor_type):
        self.device_id = device_id
        self.sensor_suffix = sensor_suffix
        self.sensor_type = sensor_type
        self.full_id = f"{device_id}:{sensor_suffix}"

    def read(self):
        return {}

class SolarSensor(Sensor):
    def __init__(self, device_id, suffix="SOLAR_MAIN"):
        super().__init__(device_id, suffix, "SOLAR_GEN")
        self.battery_bank_soc = 88.5 # State of Charge

    def read(self):
        # Simulate day/night cycle
        hour = time.localtime().tm_hour
        base_watts = 0
        if 6 <= hour <= 18:
            peak_factor = 1 - abs(12 - hour) / 6
            base_watts = 2400 * peak_factor # Upgraded capacity
        
        watts = max(0, base_watts + random.uniform(-50, 50))
        
        # Simulate battery drain/charge
        if watts > 500: self.battery_bank_soc = min(100, self.battery_bank_soc + 0.1)
        else: self.battery_bank_soc = max(10, self.battery_bank_soc - 0.05)

        return {
            "power_w": round(watts, 2),
            "voltage": 48.2, # 48V System upgrade
            "current": round(watts / 48.2, 2),
            "battery_soc": round(self.battery_bank_soc, 1),
            "efficiency": round(0.94 + random.uniform(-0.02, 0.02), 2)
        }

class WaterSensor(Sensor):
    def __init__(self, device_id, suffix="PUMP_MAIN"):
        super().__init__(device_id, suffix, "WATER_PUMP")
        self.tank_level = 85.0

    def read(self):
        is_pumping = random.random() > 0.7
        gpm = random.uniform(5, 12) if is_pumping else 0
        
        if is_pumping: self.tank_level = min(100, self.tank_level + 0.2)
        else: self.tank_level = max(20, self.tank_level - 0.05)

        return {
            "gallons": round(gpm * (DEFAULT_POLL_INTERVAL / 60), 2),
            "flow_rate_gpm": round(gpm, 2),
            "status": "ON" if is_pumping else "IDLE",
            "tank_level_pct": round(self.tank_level, 1),
            "pressure_psi": round(55 + random.uniform(-2, 2), 1)
        }

class SecuritySensor(Sensor):
    def __init__(self, device_id, suffix="PIR_01"):
        super().__init__(device_id, suffix, "WORKSHOP_PRESENCE")
    
    def read(self):
        has_motion = random.random() > 0.8
        return {
            "motion_detected": has_motion,
            "hours": round(DEFAULT_POLL_INTERVAL / 3600, 4) if has_motion else 0
        }

class GodzillaTelematics(Sensor):
    def __init__(self, device_id, suffix="CRATE_7.3L"):
        super().__init__(device_id, suffix, "GODZILLA_TELEMETRY")
        self.rpm = 0
        self.oil_temp = 70
        self.coolant_temp = 70
        self.running = False
    
    def read(self):
        # Simulate Dyno Run
        if random.random() > 0.9: self.running = not self.running
        
        if self.running:
            target_rpm = random.randint(2000, 5500)
            self.rpm += (target_rpm - self.rpm) * 0.2
            self.oil_temp = min(210, self.oil_temp + 0.5)
            self.coolant_temp = min(195, self.coolant_temp + 0.8)
        else:
            self.rpm = 0
            self.oil_temp = max(70, self.oil_temp - 0.2)
            self.coolant_temp = max(70, self.coolant_temp - 0.4)
            
        return {
            "rpm": int(self.rpm),
            "oil_temp_f": round(self.oil_temp, 1),
            "coolant_temp_f": round(self.coolant_temp, 1),
            "oil_pressure_psi": round(self.rpm / 100 + 20, 1) if self.rpm > 0 else 0
        }

def run_bridge(server_url, device_id, sim_mode=True):
    print(f"[BRIDGE] 🌉 Hardware Bridge Active")
    print(f"         📍 Device ID: {device_id}")
    print(f"         🔗 Server:    {server_url}")
    print(f"         📡 Mode:      {'SIMULATION' if sim_mode else 'PHYSICAL'}")

    # Initialize Sensors attached to THIS device
    sensors = [
        SolarSensor(device_id, "SOLAR"),
        WaterSensor(device_id, "WATER"),
        SecuritySensor(device_id, "SECURITY"),
        GodzillaTelematics(device_id, "ENGINE_01")
    ]

    while True:
        try:
            for sensor in sensors:
                data = sensor.read()
                
                # Logic to reduce chatter
                should_send = True
                if sensor.sensor_type == "WATER_PUMP" and data['gallons'] == 0: should_send = False
                if sensor.sensor_type == "WORKSHOP_PRESENCE" and not data['motion_detected']: should_send = False
                if sensor.sensor_type == "SOLAR_GEN": should_send = True
                if sensor.sensor_type == "GODZILLA_TELEMETRY" and data['rpm'] > 0: should_send = True

                if should_send:
                    payload = {
                        "sensor_id": sensor.full_id,
                        "type": sensor.sensor_type,
                        "device_id": device_id, # Extra context
                        **data
                    }
                    
                    try:
                        resp = requests.post(server_url, json=payload, timeout=2)
                        if resp.status_code == 200:
                            print(f"[SENT] {sensor.full_id}: {json.dumps(data)}")

                            # Handle Commands
                            r_json = resp.json()
                            if r_json.get('data') and 'commands' in r_json['data']:
                                for cmd in r_json['data']['commands']:
                                    print(f"⚡ [CMD] {cmd.get('action')}: {cmd.get('params')}")
                                    # Execute command logic here (simulation)
                                    if cmd.get('action') == 'REBOOT':
                                        print("   > REBOOTING SENSOR...")
                                    if cmd.get('action') == 'SET_POLL':
                                        global DEFAULT_POLL_INTERVAL
                                        DEFAULT_POLL_INTERVAL = int(cmd.get('params', 5))
                                        print(f"   > POLL INTERVAL SET TO {DEFAULT_POLL_INTERVAL}s")

                        else:
                            print(f"[FAIL] Server Error: {resp.status_code}")
                    except requests.exceptions.ConnectionError:
                         print(f"[FAIL] Could not connect to {server_url}")

            time.sleep(DEFAULT_POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n[BRIDGE] Stopping...")
            sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ark Hardware Bridge")
    parser.add_argument("--server", type=str, default=DEFAULT_SERVER, help="Ark Server Endpoint URL")
    parser.add_argument("--device-id", type=str, default=socket.gethostname(), help="Unique Name for this Device")
    parser.add_argument("--sim", action="store_true", help="Run in simulation mode")
    
    args = parser.parse_args()

    run_bridge(args.server, args.device_id, sim_mode=args.sim)
