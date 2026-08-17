# 17 — API Specification

## Status
This is a **working draft** for the FastAPI backend, defined ahead of implementation so that dashboard, game UI, and experiment scripts can be developed in parallel against a stable contract. Exact request/response schemas should be refined once `18_DATABASE_SCHEMA.md` and `25_TRAFFIC_STATE_MODEL.md` (Phase 3) are finalized.

## Base
```text
Base URL (dev): http://localhost:8000
Format: JSON
```

## Endpoints

### `GET /traffic/state`
Returns the current unified `TrafficState` for the whole network (all junctions).

```text
Response:
{
  "timestamp": "...",
  "junctions": [ { junction_id, queues, avg_speed, density, ... } ]
}
```

### `GET /traffic/state/{junction_id}`
Returns `TrafficState` for a single junction.

### `GET /traffic/prediction`
Returns short-term forecast per junction (see `14_DATA_ARCHITECTURE.md` Prediction Output object).

```text
Query params: horizon_minutes (default 5)
```

### `POST /simulation/run`
Advances the "physical"/reference SUMO simulation by a given number of steps (used by both the demo loop and experiment scripts).

```text
Body: { "steps": 100 }
Response: { "new_state": TrafficState }
```

### `POST /strategy/evaluate`
Core Scenario Engine endpoint. Given the current Twin state (implicit) and an optional list of candidate strategy types, runs the clone-simulate-discard evaluation described in `13_DIGITAL_TWIN_ARCHITECTURE.md` and returns scored results for each candidate — but does **not** apply any of them.

```text
Body: { "strategies": ["green_extend", "diversion", "dynamic_lane", "emergency_priority"] }
Response: {
  "results": [
    { strategy_id, strategy_type, predicted_delay_s, predicted_queue_m,
      predicted_throughput, predicted_emissions, predicted_emergency_delay_s, score }
  ]
}
```

### `POST /strategy/apply`
Applies a chosen strategy (from a prior `/strategy/evaluate` call) to the Twin (and, in demo mode, the reference simulation), and returns the resulting `Decision` object including the explanation.

```text
Body: { "strategy_id": "..." }
Response: Decision  # see 14_DATA_ARCHITECTURE.md
```

### `GET /recommendation`
Convenience endpoint: runs `/strategy/evaluate` with the default candidate set and returns only the top-recommended strategy plus explanation, without applying it. Used by the game UI's "AI Recommendation" panel.

### `POST /incident/trigger`
Manually or procedurally injects an incident into the reference simulation (accident, road closure, surge, weather, emergency vehicle) — see `28_INCIDENT_ENGINE.md`.

```text
Body: { "incident_type": "accident", "location": "junction_3", "severity": "medium" }
```

### `GET /experiments/results`
Returns stored results for a given experiment run (backing `47_RESULTS_ANALYSIS.md`).

## Design Notes
- `/strategy/evaluate` and `/strategy/apply` are deliberately **separate** — this mirrors the "simulate before you act" design that is the project's core novelty claim (Contribution 3, `07_NOVELTY_AND_CONTRIBUTIONS.md`); the API should never make it possible to skip evaluation.
- All endpoints operate on a **single active session/run** for the prototype (no multi-tenant concerns) — consistent with `10_SCOPE_AND_NON_SCOPE.md`.
- Authentication/authorization is out of scope for the prototype.

## Future / Not in Round-2 Scope
- WebSocket streaming for live UI updates (nice-to-have if time allows).
- Multi-network / multi-session support.
- Persistent user accounts.
