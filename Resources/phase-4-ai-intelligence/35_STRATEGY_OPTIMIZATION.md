# 35 — Strategy Optimization

## Purpose
The decision-making core: given the Scenario Engine's simulated metrics for each candidate (`27_SCENARIO_ENGINE.md`), select the one with the best **network-level** outcome. This directly implements O6 and is what makes NexusTwin's `"nexustwin"` control mode (referenced in `29_BASELINE_CONTROLLER.md`) different from the two baselines.

## Phase 1 (Required) — Deterministic Multi-Objective Scoring

```python
def score(candidate_metrics: ScenarioResult, weights: dict) -> float:
    return (
        weights["delay"]      * candidate_metrics.predicted_delay_s
        + weights["queue"]      * candidate_metrics.predicted_queue_m
        + weights["spillback"]  * spillback_penalty(candidate_metrics)
        + weights["emissions"]  * candidate_metrics.predicted_emissions
        + weights["emergency"]  * candidate_metrics.predicted_emergency_delay_s
    )
    # Lowest score wins.
```

- All terms are **network-wide** (summed/aggregated across all junctions), not just the junction the candidate directly targets — this is what operationalizes H3 (network-level optimization reduces spillback vs. isolated intersection optimization).

## Spillback Penalty (Key Differentiator)

```python
def spillback_penalty(candidate_metrics: ScenarioResult) -> float:
    """
    Penalizes candidates where queue reduction at the targeted
    junction is offset by queue increase elsewhere in the network.
    E.g.: compare per-junction queue deltas vs. the 'do_nothing'
    baseline candidate; penalize net negative transfers.
    """
```

This is the mechanism that makes the worked example in `27_SCENARIO_ENGINE.md` (Dynamic Lane winning over Diversion despite Diversion looking good at Junction A alone) actually happen in code, not just in the pitch narrative.

## Default Weights (tune during Phase 3/4/5 testing)

```text
delay:      1.0
queue:      1.0
spillback:  1.5   # weighted higher — this is our differentiator
emissions:  0.5
emergency:  3.0   # weighted much higher — safety priority (38_EMERGENCY_PRIORITY.md)
```

Weights should be documented and version-controlled (e.g., in a `config/optimization_weights.yaml`) rather than hardcoded inline, so they can be tuned without code changes and so any changes are traceable for reproducibility (`49_REPRODUCIBILITY.md`).

## Selection Logic

```python
def select_strategy(candidates: list[ScenarioResult], weights: dict) -> ScenarioResult:
    scored = [(c, score(c, weights)) for c in candidates]
    best = min(scored, key=lambda x: x[1])
    return best[0]
```

- If the `do_nothing` baseline candidate (from `34_STRATEGY_GENERATION.md`) scores best, NexusTwin should recommend/apply **no intervention** — this is an important, honest behavior to demonstrate (the system isn't intervention-happy; it validates that action actually helps before acting).

## Phase 2 (Stretch Goal) — Reinforcement Learning

- RL is treated strictly as an **optional replacement or augmentation** for this scoring function, trained against the Twin as the environment.
- See `36_REINFORCEMENT_LEARNING.md` for scope and why it is not a dependency for the core system.

## Integration with the Baseline Controller Interface

Implements the `"nexustwin"` branch of the common controller function defined in `29_BASELINE_CONTROLLER.md`:

```python
def run_controller(method="nexustwin", scenario, run_id):
    # at each decision point (per 34_STRATEGY_GENERATION.md triggers):
    candidates = generate_candidates(...)
    results = scenario_engine.evaluate(candidates)   # 27_SCENARIO_ENGINE.md
    chosen = select_strategy(results, weights)         # this document
    apply_to_reference_simulation(chosen)
    explain(chosen, results)                            # 37_EXPLAINABLE_AI.md
```

## Implementation Status

- [x] Multi-objective scoring function (`src/strategy_optimizer.py`)
- [x] Spillback penalty detection (`compute_spillback_penalty`)
- [x] Weighted scoring config (`configs/optimization_weights.json`)
- [x] Do-nothing control candidate fallback evaluation
- [x] Deterministic strategy selection

