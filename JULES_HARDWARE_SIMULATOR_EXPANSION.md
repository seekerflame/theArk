# JULES DELEGATION: Hardware Simulator Expansion

**Mission Type**: INFRASTRUCTURE SIMULATION
**Priority**: MEDIUM
**Estimated Effort**: 10-15 hours

---

## OBJECTIVE

Expand the current `hardware_bridge.py` to simulate a High-Density Village Node ecosystem. This data is critical for the "Art Walk" maps and metabolic dashboard visualizations.

---

## CONTEXT

Read: `07_Code/The_Ark/core/hardware_bridge.py`

---

## DELIVERABLES

### 1. Multi-Node State Simulation

**File**: Update `07_Code/The_Ark/core/hardware_bridge.py`

- **Solar Array**: Simulate power generation across 12 hours (Sine wave).
- **Water Consumption**: Simulate reservoir levels with stochastic "usage spikes".
- **Team Swarms**: Simulate telemetry for 4 separate swarms (Chassis, Drivetrain, Systems, Body).
  - Metrics: Temperature, Power Draw, Active Quests.
- **Stochastic Faults**: Occasionally trigger "warning" states to test dashboard alerts.

### 2. Mesh Network Mock

- Simulate network latency and signal strength between 5 virtual "Village Nodes".

---

## TECHNICAL CONSTRAINTS

- Keep it in `hardware_bridge.py`.
- No new external libraries - use `random` and `math` for stochastic behavior.
- Data must be reflectable in the `/api/evolution` or `/api/system/status` endpoints.

---

## COMMIT FORMAT

```
[Jules/Hardware] Your descriptive message
```

---

**Status**: AWAITING JULES ACKNOWLEDGMENT
**Lead**: Antigravity
