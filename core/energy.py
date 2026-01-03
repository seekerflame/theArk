import time
import math
import logging
import os

logger = logging.getLogger("ArkOS.Energy")

class EnergyMonitor:
    def __init__(self, ledger, sensors=None):
        self.ledger = ledger
        self.sensors = sensors
        self.start_time = time.time()
        self.baseline_power = 15.0 # Base Watts for a Mac Mini / PC Node
        self.peak_power = 120.0 # Peak Watts during AI thinking
        self.current_watts = self.baseline_power
        self.current_generation = 0.0
        self.total_energy_kwh = 0.0
        self.total_generation_kwh = 0.0
        self.last_update = time.time()

    def get_current_power(self, is_thinking=False):
        # 1. Calculate Consumption (Simulated)
        noise = math.sin(time.time() * 0.1) * 2.0
        if is_thinking:
            consumption = self.peak_power + noise
        else:
            consumption = self.baseline_power + noise
        
        # 2. Calculate Generation (Real from Sensors)
        generation = 0.0
        if self.sensors:
            generation = self.sensors.get_aggregate_value('solar')
            # Add other generation types here if needed (e.g. 'wind', 'hydro')

        self.current_watts = consumption
        self.current_generation = generation

        # 3. Update Energy Accumulators
        now = time.time()
        dt = (now - self.last_update) / 3600 # hours

        self.total_energy_kwh += (consumption / 1000) * dt
        self.total_generation_kwh += (generation / 1000) * dt

        self.last_update = now
        
        # Return Net Power (Consumption - Generation)
        # Note: If generation > consumption, this is negative (feeding grid/battery)
        return consumption - generation

    def calculate_kardashev(self, aggregate_power_watts=None):
        """
        K = (log10(P) - 6) / 10
        Type I = 10^16 W (Kardashev original uses 10^16, but many use 10^17 for Type I.
        Carl Sagan formula: K = (log10(P) - 6) / 10 is standard).

        P is in Watts.
        """
        # If no aggregate provided, we use the global estimate + our node contribution
        humanity_aggregate = 1.8e13 # ~18 Terawatts

        # We use our Consumption + Generation for Kardashev score?
        # Usually Kardashev measures energy *consumption* / mastery.
        # So we should probably add our generation to the global pool.

        my_contribution = self.current_watts + self.current_generation

        p = aggregate_power_watts if aggregate_power_watts else (humanity_aggregate + my_contribution)
        
        try:
            if p <= 0: return 0.0 # Should not happen unless humanity disappears
            k = (math.log10(p) - 6) / 10
            return round(k, 8)
        except:
            return 0.73 # Fallback

    def get_status(self, is_thinking=False):
        net_power = self.get_current_power(is_thinking)
        return {
            "power_consumption_watts": round(self.current_watts, 2),
            "power_generation_watts": round(self.current_generation, 2),
            "net_power_watts": round(net_power, 2),
            "energy_consumed_kwh": round(self.total_energy_kwh, 6),
            "energy_generated_kwh": round(self.total_generation_kwh, 6),
            "kardashev_level": self.calculate_kardashev(),
            "aggregate_humanity_mw": 18000000.0,
            "node_contribution_percent": ((self.current_watts + self.current_generation) / 1.8e13) * 100
        }
