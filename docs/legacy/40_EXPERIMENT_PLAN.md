# 40 — Experiment Plan

## Purpose
Defines the concrete set of experiments that turn NexusTwin from "a working demo" into "a research-grade evaluated system." Every experiment here maps back to a hypothesis in `08_OBJECTIVES_AND_HYPOTHESES.md` and uses the common controller interface from `29_BASELINE_CONTROLLER.md` so runs are directly comparable.

## Experiment Summary Table

| ID | Name | Compares | Tests |
|---|---|---|---|
| E1 | Fixed vs NexusTwin | `method="fixed"` vs `method="nexustwin"` | H1 |
| E2 | Reactive vs Predictive | `method="reactive"` vs `method="nexustwin"` | H1, H2 |
| E3 | Local vs Network-Level Optimization | NexusTwin scorer with `spillback` weight = 0 vs default | H1, H3 |
| E4 | With vs Without Prediction | NexusTwin triggering on reactive-only thresholds vs including predictive triggers (`34_STRATEGY_GENERATION.md`) | H2 |
| E5 | Sensor Noise | Clean perception vs injected noise/latency/occlusion (`45_ROBUSTNESS_TESTING.md`) | H4 |
| E6 | Accident Scenario | Fixed / Reactive / NexusTwin under UC2 | H1, H2 |
| E7 | Emergency Vehicle Scenario | Fixed / Reactive / NexusTwin under UC3 | H1 (emergency-weighted) |
| E8 | Extreme Traffic | Fixed / Reactive / NexusTwin under a surge/festival-level demand multiplier | H1, H3 |

## E1 — Fixed vs NexusTwin

- **Scenario**: UC1 (rush hour), same demand file across both runs.
- **Metrics**: average waiting time, average travel time, max queue, throughput.
- **Expected direction (H1)**: NexusTwin reduces delay/queue relative to fixed-time.
- **Runs**: ≥3 repetitions per method (with different random seeds for demand generation) to guard against single-run noise, if time allows; minimum 1 run each is the hard floor.

## E2 — Reactive vs Predictive

- **Scenario**: UC1 with a demand spike inserted partway through (to create a moment where "seeing it coming" matters).
- **Metrics**: same as E1, plus **time between trigger and intervention** (should be negative/earlier for the predictive/NexusTwin run vs. reactive, which only responds after the queue is already large).

## E3 — Local vs Network-Level Optimization

- **Method**: run NexusTwin twice — once with the `spillback` weight in `35_STRATEGY_OPTIMIZATION.md` set to 0 (effectively local/junction-level optimization) and once with the default (network-level).
- **Scenario**: a scenario where the network has a clear "downstream" junction that could absorb displaced congestion (network topology from `22_ROAD_NETWORK.md` should support this — verify during Phase 3).
- **Metrics**: per-junction queue deltas vs. baseline, and count of "spillback events" (junctions whose queue got worse specifically because congestion was pushed there).
- **Expected direction (H3)**: default (network-level) run should show fewer/less severe spillback events than the zero-weight run.

## E4 — Prediction vs No Prediction

- **Method**: NexusTwin with predictive triggers disabled (decision points fire only on reactive queue thresholds) vs. enabled (`34_STRATEGY_GENERATION.md` trigger conditions 1+2 vs. condition 2 only).
- **Scenario**: UC1 with a sharp demand ramp (so "before it happens" vs. "after it happens" is meaningfully different).

## E5 — Sensor Noise

- See `45_ROBUSTNESS_TESTING.md` for the full injection methodology; this experiment slot runs NexusTwin at 0%, 10%, 20%, 30% simulated sensor error and reports how selection quality (score of chosen candidate vs. the best possible candidate under ground truth) degrades.

## E6 / E7 / E8 — Scenario-Specific Runs

- Run all three methods (fixed, reactive, nexustwin) under each of UC2 (accident), UC3 (emergency vehicle), and a high-demand variant of UC1/UC5 (extreme traffic), logging the same core metrics plus the scenario-specific one (emergency response time for E7, spillback events for E8).

## Experiment Execution Order

```text
1. E1 (simplest, confirms basic pipeline correctness)
2. E6 (accident) — reuses E1 infrastructure with incident injection
3. E7 (emergency) — highest-value demo scenario, prioritize early
4. E2, E4 (predictive vs reactive — needs prediction model working)
5. E3 (network vs local — needs spillback penalty working)
6. E8 (extreme traffic)
7. E5 (sensor noise — can run last, needs perception noise injection)
```

This ordering front-loads the experiments most critical to the demo narrative (E1, E6, E7) so that even if time runs out, the most important comparisons exist.

## Output
All experiment runs write to `simulation_runs` / `strategies` / `results` tables (`18_DATABASE_SCHEMA.md`), tagged with a `scenario` and `method` so `47_RESULTS_ANALYSIS.md` can generate comparison tables and charts programmatically rather than by hand.

## Hard Rule
**No fabricated numbers.** Every value in `43_BASELINE_COMPARISON.md` and the final pitch must trace back to an actual logged `results` row from one of these experiments.
