#!/usr/bin/env python3
"""
Sovereign Hardware Bridge - Simulator
Simulates ESP32 nodes sending sensor data to the Village Node.
"""

import time
import json
import random
import urllib.request

API_URL = "http://localhost:3000/api/hardware"

SENSORS = [
    {"id": "solar_panel_cluster_01", "type": "SOLAR_GEN", "range": (50, 450)},
    {"id": "main_pump_01", "type": "WATER_PUMP", "range": (10, 80)},
    {"id": "workshop_pir_01", "type": "WORKSHOP_PRESENCE", "range": (0, 1)}
]

def simulate_sensor(sensor):
    if sensor['type'] == 'WORKSHOP_PRESENCE':
        # 10% chance of motion
        val = 1 if random.random() > 0.9 else 0
        payload = {
            "sensor_id": sensor['id'],
            "type": sensor['type'],
            "hours": val # Simulating 1 cycle of presence
        }
    elif sensor['type'] == 'WATER_PUMP':
        val = random.uniform(*sensor['range'])
        payload = {
            "sensor_id": sensor['id'],
            "type": sensor['type'],
            "gallons": val
        }
    else: # SOLAR_GEN
        val = random.uniform(*sensor['range'])
        payload = {
            "sensor_id": sensor['id'],
            "type": sensor['type'],
            "power_w": val
        }
    
    return payload

def send_data(payload):
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(API_URL, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
            print(f"📡 [{payload['sensor_id']}] Sent: {payload.get('power_w', payload.get('gallons', payload.get('hours')))} | Result: {result.get('status')} | Minted: {result.get('at_earned')} AT")
    except Exception as e:
        print(f"❌ Error sending data from {payload['sensor_id']}: {e}")

def main():
    print("🚀 Sovereign Hardware Simulator Started")
    print("Press Ctrl+C to stop.")
    
    while True:
        for sensor in SENSORS:
            payload = simulate_sensor(sensor)
            send_data(payload)
            time.sleep(1) # Spacing out sensor bursts
        
        print("-" * 40)
        time.sleep(10) # Wait 10s between full cycles

if __name__ == "__main__":
    main()
