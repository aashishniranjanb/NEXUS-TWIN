# 34 — Strategy Generation

## Purpose
Defines exactly how the Scenario Engine (`27_SCENARIO_ENGINE.md`) decides **which** candidate strategies to generate at a given decision point — the step that happens just before "simulate each candidate."

## Trigger Conditions for a Decision Point

A decision point (a moment where candidate strategies should be generated and evaluated) is triggered when any of the following hold:

```text
1. Predicted congestion (33_CONGESTION_PREDICTION.md) exceeds a
   threshold for any junction within the forecast horizon
   → proactive/predictive trigger (supports H2)

2. Current queue length at any junction exceeds a threshold
   → reactive trigger (fallback, always active even if prediction
     is unavailable or low-confidence)

3. An incident is newly triggered (28_INCIDENT_ENGINE.md)
   → event-driven trigger (accident, closure, surge, weather,
     emergency all immediately warrant evaluation)
```

## Candidate Generation Rules

For each decision point, generate candidates from the strategy types defined in `27_SCENARIO_ENGINE.md`, filtered/parameterized by context:

| Context | Candidates generated |
|---|---|
| General rising congestion (no incident) | `green_extend` (+20s, +40s), `diversion` (20%, 30%) |
| Accident on an edge | `diversion` (route around it), `green_extend` on the detour junction, `dynamic_lane` if a parallel lane can absorb flow |
| Road closure | `diversion` (mandatory — closed edge is unusable), `green_extend` at the junction absorbing diverted flow |
| Emergency vehicle present | `emergency_priority` (always included as a candidate, weighted heavily in scoring — see `38_EMERGENCY_PRIORITY.md`), plus normal candidates for comparison |
| Festival/surge / stadium egress | `dynamic_lane`, `diversion`, `green_extend` at the surge-adjacent junction |
| Weather (network-wide) | `green_extend` at multiple junctions simultaneously (since the effect is network-wide, a single-junction fix is unlikely to be sufficient) |

## Candidate Count Constraint

- **3–4 candidates per decision point**, per the scope defined in `10_SCOPE_AND_NON_SCOPE.md` — enough to demonstrate genuine comparison without blowing the latency budget (`46_LATENCY_ANALYSIS.md`).
- Always include a **"do nothing" / baseline candidate** (i.e., what happens if the current control mode continues unchanged) so the Optimization layer can confirm intervention is actually beneficial before recommending one — this also gives a natural fallback if all active candidates score worse than doing nothing.

## Parameterization Ranges (defaults, tune during Phase 3/4 testing)

```text
green_extend:      extension_seconds in {20, 40}
diversion:         diversion_percent in {20, 30}
dynamic_lane:       single configuration per candidate (binary: open/not open)
emergency_priority: always a single candidate when an emergency vehicle is present
```

## Generation Function (interface)

```python
def generate_candidates(network_state: NetworkState,
                         active_incidents: list[Incident],
                         prediction: PredictionOutput) -> list[Strategy]:
    """
    Returns a list of 3-4 Strategy objects (including a baseline
    'do_nothing' candidate) for the current decision point, per the
    context rules above.
    """
```

## Dependencies
- Consumes `25_TRAFFIC_STATE_MODEL.md`, `28_INCIDENT_ENGINE.md`, and `33_CONGESTION_PREDICTION.md` outputs.
- Feeds directly into the "simulate each candidate" step of `27_SCENARIO_ENGINE.md`, and downstream into `35_STRATEGY_OPTIMIZATION.md`.
