# 27 — Scenario Engine

## Why This Is the Most Important Document in Phase 3
The Scenario Engine implements **Contribution 3** from `07_NOVELTY_AND_CONTRIBUTIONS.md` — the core claimed novelty of NexusTwin: testing multiple candidate interventions inside the Digital Twin *before* choosing one, rather than applying a single learned policy's output directly.

## Core Loop

```text
Current (synchronized) Twin State
              │
              ▼
     Generate Candidate Actions
   (green_extend, diversion,
    dynamic_lane, emergency_priority
    — see Strategy Types below)
              │
              ▼
   For each candidate:
     1. Snapshot Twin state
     2. Apply candidate action (via TraCI)
     3. Step simulation forward N ticks
        (short horizon, e.g., 2-5 simulated minutes)
     4. Collect metrics (see Metrics below)
     5. Restore Twin to pre-candidate snapshot
              │
              ▼
      Collected metrics per candidate
              │
              ▼
   Pass to Optimization (35_STRATEGY_OPTIMIZATION.md)
   for scoring and selection
```

## Strategy Types (Candidate Generation)

| Strategy type | Parameters | Implementation (TraCI) |
|---|---|---|
| `green_extend` | `junction_id`, `extension_seconds` | Extend current green phase duration |
| `diversion` | `from_edge`, `to_edge`, `diversion_percent` | Reroute a percentage of a route's flow via `traci.vehicle.setRoute` or edge weight adjustment |
| `dynamic_lane` | `edge_id`, `lane_config` | Temporarily reassign a lane's allowed direction/use |
| `emergency_priority` | `vehicle_id`, `corridor_edges` | Grant priority (extended green, cleared path) along a corridor for one vehicle |

Multiple parameter variants of the same type can be generated as separate candidates (e.g., `green_extend +20s` and `green_extend +40s`, or `diversion 20%` and `diversion 30%`) — this mirrors the worked example in `03_IDEATION.md`.

## Metrics Collected Per Candidate

Matches the `Scenario Result` object in `14_DATA_ARCHITECTURE.md`:

```text
predicted_delay_s
predicted_queue_m
predicted_throughput
predicted_emissions          # estimated from vehicle-time / stop-start behavior
predicted_emergency_delay_s  # only meaningfully non-trivial if an emergency
                              # vehicle is present in the scenario
```

All metrics are computed **network-wide**, not just at the junction the candidate directly targets — this is what allows spillback (H3) to be detected: a candidate that helps one junction but worsens the network total should score worse than one that helps the network overall.

## Worked Example (from ideation notes, kept as the canonical demo case)

```text
Junction A congestion = 88%, Junction B = 64%, Junction C = 32%

Strategy       A Queue   B Queue   Avg Delay   Emergency
Fixed          1.8 km    1.2 km    17 min      9 min
Green +20      1.4 km    1.6 km    14 min      7 min
Diversion      0.9 km    1.4 km    10 min      5 min
Dynamic lane   0.7 km    1.0 km    8 min       3 min   ← selected
```

Dynamic lane is selected because it produces the best **network-wide** outcome, not because it is individually the largest change — this is the demo moment referenced in `56_DEMO_SCRIPT.md`.

## Performance Budget

- Candidate simulations must complete quickly enough for a live demo — target end-to-end `/strategy/evaluate` latency is defined in `46_LATENCY_ANALYSIS.md`.
- Keep the number of candidates per decision point small (3–4) and the simulation horizon short (a few simulated minutes) to stay within budget; this is a deliberate scope constraint, not a limitation to hide.

## API Surface
Implements the backend logic behind `POST /strategy/evaluate` in `17_API_SPECIFICATION.md`.

## Implementation Status

- [x] Snapshot/restore via TraCI `saveState` / `loadState`
- [x] Candidate Strategy model (`src/scenario_models.py`)
- [x] Do-nothing control candidate
- [x] Green extension strategy (`green_extend`)
- [x] Diversion strategy (`diversion` via parallel bypass route)
- [x] Dynamic lane strategy (`dynamic_lane` via shoulder lane activation)
- [x] Emergency priority strategy (`emergency_priority` corridor clearing)
- [x] Network-wide metrics & CO2 emissions tracking
- [x] Multi-objective optimization & spillback penalty scoring
- [x] Grounded Explainable AI recommendation engine (`src/explainable_ai.py`)
- [x] Scenario Engine CLI demonstration (`experiments/run_scenario_engine.py`)
- [x] Comprehensive Unit & Integration test suite (`tests/test_scenario_engine.py`)
- [x] Baseline regression test verified (`experiments/run_baselines.py`)
- [x] Performance latency logging (`results/scenario_performance.json`)

