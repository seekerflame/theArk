import time

class EnergyMining:
    """
    The Energy Mining Engine (Omaha Move).
    Converts Solar Watts into AT rewards.
    Links physical power to survival autonomy.
    """
    def __init__(self, ledger, sensors):
        self.ledger = ledger
        self.sensors = sensors
        self.conversion_rate = 0.01 # 100 Watts for 1 hour = 1 AT (Example)
        self.people_per_calorie_day = 2500 # Avg daily need

    def calculate_reward(self, watts, duration_hours):
        """Formula: Watts * Duration * Efficiency = AT"""
        raw_reward = (watts * duration_hours) * self.conversion_rate
        return round(raw_reward, 2)

    def get_survival_autonomy(self, total_daily_watts):
        """
        Calculates how many people can be sustained based on energy surplus.
        Energy -> Light -> Food (Hydroponics) logic.
        """
        # 1 kWh (1000 Watts for 1h) roughly equals growth energy for X calories
        # This is a simplified model for the 'Plug & Play' baseline.
        daily_calories = total_daily_watts * 0.5 # Simplified efficiency factor
        people_sustained = daily_calories / self.people_per_calorie_day
        
        return {
            "daily_watts": total_daily_watts,
            "people_sustained": round(people_sustained, 1),
            "autonomy_level": "OPTIMAL" if people_sustained >= 1 else "CRITICAL"
        }

    def verify_clean_energy(self, samples):
        """
        Detects if energy is 'Natural' (Solar/Wind) or 'Mechanical' (Generator).
        Natural energy has fractal variance. Mechanical is flat/consistent.
        """
        if not samples or len(samples) < 10: return True # Benefit of doubt used for Alpha
        
        # Calculate Variance and Change rate
        mean = sum(samples) / len(samples)
        if mean == 0: return False
        
        variance = sum((x - mean) ** 2 for x in samples) / len(samples)
        
        # Generator Signature: Variance is extremely low (perfectly steady voltage/amps)
        # Solar Signature: Variance exists due to clouds, angle, temp drift (Fractal)
        
        # 1. Check for Absolute Flatline (Fake/Generator)
        if variance < (mean * 0.0001): 
            return False
            
        # 2. Check for Fractal Jitter (Natural signatures are never perfectly periodic)
        diffs = [abs(samples[i] - samples[i-1]) for i in range(1, len(samples))]
        avg_diff = sum(diffs) / len(diffs)
        
        if avg_diff < 0.005: # Too smooth for nature
            return False

        return True

    def mint_energy_labor(self, username, watts, duration_hours, samples=None):
        """Mints AT for maintaining/running energy infrastructure."""
        
        # 1. Source Verification (The Generator Trap)
        if samples and not self.verify_clean_energy(samples):
            return False, "Energy Signature Rejected: Mechanical/Artificial source detected."
            
        reward = self.calculate_reward(watts, duration_hours)
        if reward <= 0: return False, "No energy output detected."

        # 2. Streak Multiplier (The "Fun" part)
        # In a real system, we'd check previous blocks for consistency.
        # For this demo, we'll assume a 'Thriving Provider' bonus.
        streak_bonus = 1.0
        if watts > 200: streak_bonus = 1.2 # High Output bonus

        total_reward = round(reward * streak_bonus, 2)

        tx_data = {
            "username": username,
            "type": "ENERGY_MINT",
            "watts": watts,
            "hours": duration_hours,
            "reward": total_reward,
            "streak_bonus": streak_bonus,
            "timestamp": time.time()
        }
        self.ledger.add_block('LABOR', tx_data)
        return True, f"Minted {total_reward} AT for Energy Contribution (Bonus: {streak_bonus}x)."

def get_plug_and_play_instructions():
    """Returns the 'True Baseline' hardware setup guide."""
    return """
# ARK OS: PLUG & PLAY SOLAR BASELINE

To reach $0/month living, follow this baseline hardware spec:

## 1. The Energy Hub
- **Panel**: 200W-400W Solar Panel (Local source recommended).
- **Controller**: Victron MPPT (Easy communication).
- **Battery**: 100Ah LiFePO4 (The 'Stone Schedule' storage).

## 2. The Server (The Ark)
- **Computer**: Raspberry Pi 4/5 or Mac Mini (High efficiency).
- **Connection**: USB-to-VE.Direct (Cable link to controller).

## 3. Engagement
- **Login**: Connect your Ark Wallet.
- **Sync**: Enable 'Energy Mining' in Settings.
- **Result**: Your server converts sun into AT while you sleep.
    """
