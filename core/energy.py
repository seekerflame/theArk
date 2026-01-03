import time
import math
import logging
import os

logger = logging.getLogger("ArkOS.Energy")

class EnergyMonitor:
    def __init__(self, ledger):
        self.ledger = ledger
        self.start_time = time.time()
        self.baseline_power = 15.0 # Base Watts for a Mac Mini / PC Node
        self.peak_power = 120.0 # Peak Watts during AI thinking
        self.overclock_power = 250.0 # Watts during Overclock Mode
        self.current_watts = self.baseline_power
        self.total_energy_kwh = 0.0
        self.last_update = time.time()
        self.overclock_file = "overclock.flag"

    def is_overclocked(self):
        return os.path.exists(self.overclock_file)

    def get_performance_factor(self):
        return 5.0 if self.is_overclocked() else 1.0

    def get_current_power(self, is_thinking=False):
        # Simulate power fluctuation
        noise = math.sin(time.time() * 0.1) * 2.0

        if self.is_overclocked():
             self.current_watts = self.overclock_power + (noise * 5) # High instability
        elif is_thinking:
            self.current_watts = self.peak_power + noise
        else:
            self.current_watts = self.baseline_power + noise
        
        # Calculate Energy (kWh) since last update
        now = time.time()
        dt = (now - self.last_update) / 3600 # hours
        self.total_energy_kwh += (self.current_watts / 1000) * dt
        self.last_update = now
        
        return self.current_watts

    def calculate_kardashev(self, aggregate_power_watts=None):
        """
        K = (log10(P) - 6) / 10
        Type I = 10^16 W
        Type II = 10^26 W
        Type III = 10^36 W
        Aggregate Humanity is ~0.73 (~10^13 W)
        """
        # If no aggregate provided, we use the global estimate + our node contribution
        humanity_aggregate = 1.8e13 # ~18 Terawatts
        p = aggregate_power_watts if aggregate_power_watts else (humanity_aggregate + self.current_watts)
        
        try:
            k = (math.log10(p) - 6) / 10
            return round(k, 8)
        except:
            return 0.73 # Fallback

    def get_status(self, is_thinking=False):
        power = self.get_current_power(is_thinking)
        return {
            "power_watts": round(power, 2),
            "energy_kwh": round(self.total_energy_kwh, 6),
            "kardashev_level": self.calculate_kardashev(),
            "aggregate_humanity_mw": 18000000.0,
            "node_contribution_percent": (power / 1.8e13) * 100,
            "overclock_active": self.is_overclocked()
        }
