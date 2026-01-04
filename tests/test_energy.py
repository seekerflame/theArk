def test_energy_monitor_init(energy_monitor):
    assert energy_monitor.current_watts == 15.0 # baseline
    assert energy_monitor.total_energy_kwh == 0.0

def test_get_current_power_no_generation(energy_monitor):
    net_power = energy_monitor.get_current_power(is_thinking=False)
    # Baseline 15 + noise (max 2) -> 13 to 17. Gen 0. Net ~15.
    assert 13.0 <= net_power <= 17.0
    assert energy_monitor.current_generation == 0.0

def test_get_current_power_with_generation(energy_monitor, sensor_registry):
    # Add solar generation
    sensor_registry.update("s1", "solar", 100.0)

    net_power = energy_monitor.get_current_power(is_thinking=False)
    # Consumption ~15. Generation 100. Net ~ -85.
    assert -87.0 <= net_power <= -83.0
    assert energy_monitor.current_generation == 100.0

def test_status_structure(energy_monitor):
    status = energy_monitor.get_status()
    assert "power_consumption_watts" in status
    assert "power_generation_watts" in status
    assert "net_power_watts" in status
    assert "energy_generated_kwh" in status

def test_kardashev_calculation(energy_monitor):
    k = energy_monitor.calculate_kardashev()
    assert k > 0.0
    # Humanity aggregate is ~0.73
    assert 0.72 <= k <= 0.74
