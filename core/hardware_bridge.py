import time
import json
import random
import threading
import logging

logger = logging.getLogger("ArkOS.Hardware")

class HardwareBridge:
    def __init__(self, port_mask="/dev/ttyUSB*", baud=115200):
        self.port_mask = port_mask
        self.baud = baud
        self.connected = False
        self.serial_conn = None
        self.params = {
            "solar_volts": 12.0,
            "solar_amps": 5.0,
            "battery_level": 85.0,
            "water_flow": 0.0,
            "temp_c": 22.0,
            "humidity": 45.0
        }
        self.lock = threading.Lock()
        
        # Try to connect (non-blocking)
        self._connect()
        
        # Start background poller (simulation or real)
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _connect(self):
        try:
            import glob
            import serial
            ports = glob.glob(self.port_mask)
            if ports:
                port = ports[0]
                self.serial_conn = serial.Serial(port, self.baud, timeout=1)
                self.connected = True
                logger.info(f"🔌 Hardware Bridge CONNECTED to {port}")
            else:
                logger.info("🔌 No hardware sensors found. Using HIGH-FIDELITY SIMULATOR.")
                self.connected = False
        except ImportError:
            logger.warning("⚠️ pyserial not installed. Using SIMULATOR.")
            self.connected = False
        except Exception as e:
            logger.error(f"⚠️ Serial connection failed: {e}. Using SIMULATOR.")
            self.connected = False

    def _loop(self):
        while self.running:
            if self.connected and self.serial_conn:
                try:
                    line = self.serial_conn.readline()
                    if line:
                        data = json.loads(line.decode().strip())
                        with self.lock:
                            self.params.update(data)
                except Exception as e:
                    logger.error(f"Serial Read Error: {e}")
                    self.connected = False
            else:
                # Simulation Mode
                self._simulate()
            
            time.sleep(1.0)

    def _simulate(self):
        """Simulate realistic sensor drift and fluctuations"""
        with self.lock:
            # Solar fluctuates with "clouds"
            if random.random() > 0.9: 
                self.params["solar_volts"] = max(0, self.params["solar_volts"] - random.uniform(0, 2))
            else:
                self.params["solar_volts"] = min(14.4, self.params["solar_volts"] + random.uniform(-0.1, 0.2))
            
            # Amps follow volts roughly
            self.params["solar_amps"] = max(0, (self.params["solar_volts"] - 10) * 2) if self.params["solar_volts"] > 12 else 0

            # Battery level
            charge = (self.params["solar_amps"] * 12) - 50 # 50W base load
            self.params["battery_level"] = max(0, min(100, self.params["battery_level"] + (charge / 1000)))

            # Temp/Hum drift
            self.params["temp_c"] += random.uniform(-0.1, 0.1)
            self.params["humidity"] += random.uniform(-0.5, 0.5)

    def read_telemetry(self):
        with self.lock:
            return self.params.copy()
            
    def get_status(self):
        return "ONLINE (SERIAL)" if self.connected else "ONLINE (SIMULATED)"
