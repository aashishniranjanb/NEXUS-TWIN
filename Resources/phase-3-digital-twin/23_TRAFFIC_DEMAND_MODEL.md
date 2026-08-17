# 23 — Traffic Demand Model

## Purpose
Define how vehicles are generated and routed through the network defined in `22_ROAD_NETWORK.md`, at three levels of realism, matching the staged dataset strategy in `41_DATASET_PLAN.md`.

## Vehicle Classes

| Class | SUMO vClass | Notes |
|---|---|---|
| Car | `passenger` | Majority of demand |
| Bus | `bus` | Fixed/scheduled or random, lower frequency |
| Truck | `truck` | Lower frequency, larger footprint (affects queue length more per vehicle) |
| Motorcycle | `motorcycle` | Higher frequency in dense urban corridors, smaller footprint |
| Emergency | `emergency` | Rare, triggered specifically for UC3 (`09_USE_CASES.md`) |

## Stage 1 — Synthetic / Random Demand (baseline development)

- Use SUMO's random trip generation tooling to produce a `.rou.xml` quickly for early development and testing of the network and signal logic before realism matters.
- Parameters to control: total vehicle count, spawn rate, vehicle class mix.

## Stage 2 — Structured Demand (rush-hour shaping)

- Move from uniform random trips to a **time-varying demand profile** that approximates rush-hour build-up and decay:

```text
Time (min)   Relative demand
0–10         30%   (light morning traffic)
10–25        70%   (build-up)
25–45        100%  (peak / rush hour)
45–60        50%   (decay)
```

- Directional bias: heavier inbound flow toward the arterial during morning peak, heavier outbound during evening peak (choose one framing consistently for the demo, per `56_DEMO_SCRIPT.md`).

## Stage 3 — Observation-Based Demand (if time allows)

- If representative traffic count data is available (public traffic count datasets, or manually estimated counts for the chosen real corridor), use SUMO's routes-from-observation-points tooling to generate demand that better matches real turning-movement counts at each junction, rather than assumed random routing.
- This stage is optional and should not block Phase 3 completion if data isn't readily available in time.

## Scenario-Specific Demand Variants

Each use case in `09_USE_CASES.md` needs its own demand configuration, saved under `simulation/scenarios/`:

| Scenario | Demand characteristic |
|---|---|
| UC1 Rush hour | Stage 2 time-varying profile above |
| UC2 Accident | Stage 2 profile + a mid-run capacity drop on one edge (paired with `28_INCIDENT_ENGINE.md`) |
| UC3 Emergency vehicle | Stage 2 profile + a single `emergency`-class vehicle injected with priority routing |
| UC4 Road closure | Stage 2 profile + an edge disabled mid-run |
| UC5/UC7 Festival/Stadium | A localized demand spike concentrated near one junction over a short window |
| UC6 Flood/weather | Stage 2 profile + reduced speed/capacity applied network-wide |
| UC8 Sensor failure | No demand change — this is a perception-layer fault, injected separately (`45_ROBUSTNESS_TESTING.md`) |

## Deliverables

- `simulation/routes/nexustwin_baseline.rou.xml` (Stage 1/2 demand)
- `simulation/scenarios/<scenario_name>.rou.xml` or config overlay per use case
- Short notes on assumed peak vehicle counts, to be referenced consistently in `56_DEMO_SCRIPT.md` and any reported numbers in `47_RESULTS_ANALYSIS.md`

## Dependency Note
Demand realism should not block Phase 3 completion — Stage 1 (random trips) is sufficient to prove the pipeline; Stage 2/3 refinement can continue in parallel with Phase 4 (AI layer) work.
