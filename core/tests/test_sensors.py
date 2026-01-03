import unittest
import os
import json
import time
from core.sensors import SensorRegistry

class TestSensorRegistry(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_registry.json"
        self.registry = SensorRegistry(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_update_sensor(self):
        self.registry.update("sensor1", "TEMP", 25.5)
        self.assertIn("sensor1", self.registry.sensors)
        self.assertEqual(self.registry.sensors["sensor1"]["type"], "TEMP")
        self.assertEqual(self.registry.sensors["sensor1"]["last_value"], 25.5)
        self.assertEqual(self.registry.sensors["sensor1"]["status"], "ONLINE")

    def test_save_load(self):
        self.registry.update("sensor1", "TEMP", 25.5)
        # Create a new registry instance to test loading
        new_registry = SensorRegistry(self.test_file)
        self.assertIn("sensor1", new_registry.sensors)
        self.assertEqual(new_registry.sensors["sensor1"]["last_value"], 25.5)

    def test_metabolic_yield(self):
        # No sensors
        self.assertEqual(self.registry.get_metabolic_yield(), 0.0)

        # One active sensor
        self.registry.update("sensor1", "TEMP", 25.5)
        self.assertGreater(self.registry.get_metabolic_yield(), 0.0)

        # Simulate stale sensor
        self.registry.sensors["sensor1"]["last_seen"] = time.time() - 100
        self.assertEqual(self.registry.get_metabolic_yield(), 0.0)

    def test_poll(self):
        self.registry.update("sensor1", "TEMP", 25.5)
        self.assertEqual(self.registry.sensors["sensor1"]["status"], "ONLINE")

        # Simulate time passing > 60s
        self.registry.sensors["sensor1"]["last_seen"] = time.time() - 61

        self.registry.poll()
        self.assertEqual(self.registry.sensors["sensor1"]["status"], "OFFLINE")

if __name__ == '__main__':
    unittest.main()
