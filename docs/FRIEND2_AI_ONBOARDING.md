# NEXUS-TWIN — Friend 2 (AI & Simulation Lead)
## Branch: `feature/ai-gameplay`

---

## Your job in one sentence
Make the underlying AI and simulation system smarter, more reliable, and more impactful:
better traffic events, real emergency ETA tracking, measurable strategy consequences,
multi-agent architecture groundwork — all without touching Unity scenes or UI.

---

## Setup (5 minutes)

```powershell
# Clone the repo
git clone https://github.com/aashishniranjanb/NEXUS-TWIN
cd NEXUS-TWIN

# Switch to your branch
git checkout feature/ai-gameplay

# Create virtualenv
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install deps
pip install -r requirements.txt

# Run tests to confirm baseline
python -m pytest tests/ -v
# Expected: all pass

# Start backend
python -m uvicorn backend.api.main:app --reload --port 8000
```

---

## What you own

```
intelligence/
├── prediction/
├── strategy/
├── explainability/
└── feature_engineering/

simulation/
├── bridge/
│   ├── scenario_engine.py
│   ├── traffic_state.py
│   └── metrics_collector.py

backend/
├── api/
│   ├── main.py
│   └── decision_server.py

experiments/
tests/

# Unity — NEW scripts ONLY in this folder:
game/unity/Assets/_NexusTwin/Scripts/Features/
```

---

## What to build (priority order)

---

### Priority 1 — Real Emergency ETA System

Currently ambulance delay is estimated. Make it measurable.

Create `simulation/bridge/emergency_eta.py`:
```python
class EmergencyETATracker:
    def start_dispatch(self, route: list[str]) -> None: ...
    def update_speed(self, junction_id: str, speed_mps: float) -> None: ...
    def get_current_eta_seconds(self) -> float: ...
    def is_delayed(self, threshold_seconds: float = 30.0) -> bool: ...
```

Expose via API:
```
GET /emergency/eta
→ { "eta_seconds": 142.3, "delayed": false, "threshold": 30.0 }
```

---

### Priority 2 — Traffic Event System

Expand `simulation/bridge/scenario_engine.py` with:
```python
class TrafficEvent(Enum):
    ACCIDENT = "accident"
    ROAD_CLOSURE = "closure"
    TRAFFIC_SURGE = "surge"
    SIGNAL_FAILURE = "signal_failure"
    EMERGENCY_DISPATCH = "emergency"
```

Each event must have measurable impact on:
- Queue length (meters)
- Junction throughput (vehicles/minute)
- Emergency ETA (seconds added)

---

### Priority 3 — Make Strategies Produce Different Outcomes

This is the most important thing you can do.

Currently all 4 strategies return similar numbers. Fix it.

In `intelligence/strategy/strategy_optimizer.py`, each strategy must produce verifiably different metric deltas:

| Strategy | Delay Δ | Queue Δ | ETA Δ |
|----------|---------|---------|-------|
| extend_green | -12.4% | -18.2% | +4s |
| diversion | -37.6% | -30.1% | -24s |
| emergency_priority | +8.0% | +12.0% | -31s |
| do_nothing | +45.0% | +62.0% | +24s |

These should be computed, not hard-coded.

---

### Priority 4 — Improve Scoring System

`backend/api/decision_server.py` — update the scoring to weight:
- Emergency safety: 35%
- Network flow: 25%
- Queue control: 20%
- Decision quality: 15%
- Responsible AI alignment: 5%

And score based on actual outcome vs predicted — not just which button was clicked.

---

### Priority 5 — Multi-Agent Architecture (only after above are stable)

Create `intelligence/agents/`:
```
intelligence/agents/
├── __init__.py
├── orchestrator.py          ← coordinates agents
├── traffic_agent.py         ← monitors J1/J2/J3 queues
├── emergency_agent.py       ← tracks ambulance ETA
├── safety_agent.py          ← checks for unsafe signal conflicts
├── strategy_agent.py        ← recommends strategies
└── simulation_agent.py      ← runs counterfactual rollouts
```

Each agent exposes a simple interface:
```python
class BaseAgent:
    def observe(self, state: TrafficState) -> dict: ...
    def recommend(self) -> AgentRecommendation: ...
    def explain(self) -> str: ...
```

The orchestrator aggregates all agent recommendations before
passing to the human operator.

---

### Priority 6 — Unity Feature Scripts (if needed)

If you need to surface new mechanics in the game, create scripts ONLY in:
```
game/unity/Assets/_NexusTwin/Scripts/Features/
```

Do NOT touch:
- `Scripts/Core/GameManager.cs`
- `Scripts/Core/SceneBootstrapper.cs`
- `Scripts/UI/HUDController.cs`
- `Scenes/Gameplay_J1J2J3.unity`

Send a PR to Aashish to integrate your feature scripts into the scene.

---

## API Contract (your backend endpoints that others depend on)

**Don't change these signatures without telling Aashish and Friend 1:**

```
GET  /health
GET  /api/status
GET  /traffic/state
GET  /traffic/prediction?junction_id=J2
POST /strategy/evaluate
POST /strategy/apply
```

**New endpoints you can add freely:**
```
GET  /emergency/eta
GET  /events/active
GET  /agents/status
POST /events/trigger
```

---

## Test requirements

Every new module needs tests in `tests/`.

Run before every commit:
```powershell
python -m pytest tests/ -v
```

All tests must pass. Do not break existing tests.

---

## Do NOT touch

```
game/unity/Assets/_NexusTwin/Scenes/   ← Aashish only
game/unity/Assets/_NexusTwin/Scripts/Core/
game/unity/Assets/_NexusTwin/Scripts/UI/
web/                                    ← Friend 1 only
```

---

## Daily git workflow

```powershell
# Start of day
git checkout feature/ai-gameplay
git merge main

# Work...

# Run tests
python -m pytest tests/ -v

# Commit
git add intelligence/ simulation/ backend/ experiments/ tests/
git commit -m "feat(ai): [what you did]"
git push origin feature/ai-gameplay
```

Then message Aashish to review your PR.

---

## The principle

> Do not make the AI more complex. Make it more honest, more measurable, and more impactful on the game world.

A judge who sees "Emergency Priority saved the ambulance 31 seconds and the simulation proves it"
is more impressed than "we have 5 agents with RAG and vector memory."
