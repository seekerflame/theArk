# 🤖 Jules Onboarding: Mission Briefing

**Welcome to The Ark, Jules!** You're joining a Type 0.73 Civilization OS designed for absolute survival sovereignty.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/seekerflame/theArk.git
cd theArk
python3 server.py

# Your first branch
git checkout -b jules/hardware-bridge
```

## Your Mission: Hardware Bridge Integration

**Goal**: Connect real solar panels, water systems, and sensors to auto-mint AT when they produce value.

**Current State**: Simulated in `core/sensors.py`  
**Target State**: Real hardware integration

## 5-Phase Task Breakdown

### Phase 1: Foundation ✅ (Start Here)

- [ ] Read `README.md` and `AI_COLLABORATION_GUIDE.md`
- [ ] Review `core/sensors.py`, `core/energy.py`, `api/system.py`
- [ ] Run server locally, test at `localhost:3000`

### Phase 2: Testing Framework 🧪

- [ ] Create `tests/` directory
- [ ] Write pytest suite for `core/ledger.py` (15+ tests)
- [ ] Write tests for `core/energy.py` (Kardashev calculations)
- [ ] Setup `.github/workflows/test.yml` for CI

### Phase 3: Hardware Bridge 🔌 (Main Mission)

- [ ] Research: Shelly smart plugs API, GPIO sensors, ESP32
- [ ] Extend `core/sensors.py` with `ShellyAdapter` class
- [ ] Add `/api/hardware/register` endpoint
- [ ] Test with mock sensors

### Phase 4: Optimization ⚡

- [ ] Audit `server.py` for bottlenecks
- [ ] Consider WebSockets for `syncWithLedger()` (currently 5s polling)
- [ ] Profile slow API endpoints
- [ ] Document in `OPTIMIZATION_REPORT.md`

### Phase 5: Documentation 📚

- [ ] Create `HARDWARE_SETUP.md` guide
- [ ] Update `README.md` with sensor instructions
- [ ] Add inline comments for complex logic

## Collaboration Protocol

**Commit Format**: `[Jules] Your descriptive message`

**What You Can Change**: Tests, bug fixes, optimizations, docs  
**What Needs Approval**: Breaking API changes, new dependencies, security policies

**How We Communicate**:

- GitHub commits (async)
- `/api/mission/propose` (AI-to-AI proposals)
- Through EternalFlame (human relay)

## Security Guidelines

- ✅ Never commit secrets (use `.gitignore`)
- ✅ Sanitize all logs (no passwords/keys)
- ✅ Validate API inputs (prevent injection)
- ✅ Report vulnerabilities immediately

## Philosophy: Sovereignty > Convenience

- No surveillance capitalism
- No vendor lock-in  
- Transparent everything
- Labor creates value, not scarcity

**Your Prime Directive**: Increase human freedom, decrease labor burden.

---

**Ready?** Report your first observation after exploring the codebase! 🚀

**Status**: Awaiting Jules' first commit  
**Gemini**: Standing by for coordination
