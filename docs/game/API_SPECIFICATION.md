# API_SPECIFICATION.md — NEXUS-TWIN
## Unity ↔ Python Integration Contract v1.0

**Purpose**: this is the binding contract between the Unity client and the Python/FastAPI intelligence server. If a Unity developer and a Python developer each implement exactly what's in this document and nothing else, integration should require zero renegotiation. Where this document and any other document disagree on a field name or endpoint shape, **this document wins** — update the others to match, not the other way around.

---

## 1. Purpose
Define every REST endpoint, WebSocket message type, and data schema that crosses the Unity/Python boundary, so both sides can be built in parallel against a stable contract, per `UNITY_ARCHITECTURE.md` §16 and `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md` §17.

## 2. Architecture

```text
                    UNITY 6
                       │
             ┌─────────┴─────────┐
             │                   │
          REST                 WebSocket
             │                   │
             ▼                   ▼
                  FASTAPI
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   Prediction    Strategy     Explainability
    (XGBoost)     Engine       (template)
        │            │            │
        └────────────┼────────────┘
                     ▼
              SCENARIO ENGINE
                     │
                     ▼
                   SUMO
                     │
                   TraCI
                     │
                     ▼
               Traffic State
```

**Unity never needs to know how a number was produced** — e.g., it does not know or care that congestion probability came from XGBoost specifically; it only consumes the documented JSON shape.

## 3. Base URL / Ports

| Environment | Value |
|---|---|
| Local dev (Windows standalone, primary hackathon target) | `http://localhost:8000` |
| WebSocket | `ws://localhost:8000/ws` |
| Web build (if used) | Configurable via a launch-time config file/query param — must not be hardcoded into the build, since the server address may differ from `localhost` in that deployment |

## 4. Authentication
None for the prototype (single local session, no multi-tenant concerns — matches `17_API_SPECIFICATION.md` from the backend docs). Do not add auth machinery for Round 2; it adds surface area with no demo value.

## 5. Shared IDs
All `junction_id`, `strategy_type`, `vehicle_type`, and `incident_type` string values used anywhere in this document are defined once in `DATA_CONTRACT.md` and must not be altered independently by either side. If a new value is needed (e.g., a new strategy type), it is added to `DATA_CONTRACT.md` first, then implemented on both sides.

## 6. Common Error Format

All REST error responses use this shape, regardless of endpoint:
```json
{
  "error": true,
  "code": "SIMULATION_TIMEOUT",
  "message": "Scenario evaluation exceeded the configured time budget.",
  "detail": null
}
```
Unity's `ApiClient` checks for `"error": true` on every response before parsing the expected success schema, and on any error/timeout falls back to `Stub` mode data for that call (per `UNITY_ARCHITECTURE.md` §21) rather than leaving a panel blank or crashing the scene.

## 7. Traffic State API

### `GET /traffic/state`
Returns current `NetworkState` (all junctions).
```json
{
  "timestamp": 361.0,
  "junctions": [
    {
      "junction_id": "J2",
      "queue_north_m": 45.2,
      "queue_south_m": 30.1,
      "queue_east_m": 12.0,
      "queue_west_m": 8.5,
      "average_speed_kmh": 17.3,
      "vehicle_count": 42,
      "density": 58.0,
      "waiting_time_s": 22.4,
      "throughput_veh_per_min": 14.0,
      "signal_phase": "NS_GREEN",
      "incident_state": null
    }
  ]
}
```
Field names and units match `docs/phase-3-digital-twin/25_TRAFFIC_STATE_MODEL.md` exactly — this endpoint is a direct JSON serialization of that schema, not a reinterpretation of it.

### `GET /traffic/state/{junction_id}`
Same shape as above, single junction object (not wrapped in a `junctions` array).

## 8. Prediction API

### `GET /traffic/prediction?horizon_minutes=5`
```json
{
  "junction_id": "J2",
  "congestion_probability": 0.87,
  "forecast_minutes": 5,
  "risk_level": "HIGH"
}
```
`risk_level` is a derived convenience field for the UI (`LOW` < 0.4, `MEDIUM` 0.4–0.7, `HIGH` > 0.7) — computed server-side so Unity never re-implements threshold logic that could drift out of sync with the backend's own thresholds.

Unity display mapping (`AIAlertPanel`):
```text
"J2 CONGESTION RISK — 87% — Forecast: 5 min"
```

## 9. Recommendation API

### `GET /recommendation`
Convenience endpoint — runs evaluation with the default candidate set and returns only the top recommendation plus its explanation, without applying it.
```json
{
  "strategy_type": "diversion",
  "label": "Divert Traffic",
  "confidence": 0.84,
  "explanation": { "...": "see §17 Explanation Schema" }
}
```

## 10. Strategy Evaluation API

### `POST /strategy/evaluate`
Request:
```json
{
  "junction_id": "J2",
  "strategies": ["green_extend", "diversion", "dynamic_lane", "emergency_priority"]
}
```
Response:
```json
{
  "scenario_id": "SCN_001",
  "results": [
    {
      "strategy_type": "green_extend",
      "label": "Extend Green (+20s)",
      "delay_delta_pct": -18.0,
      "queue_delta_pct": -14.0,
      "emissions_delta_pct": -6.0,
      "emergency_delay_delta_pct": -10.0,
      "is_best": false
    },
    {
      "strategy_type": "diversion",
      "label": "Divert Traffic",
      "delay_delta_pct": -31.0,
      "queue_delta_pct": -28.0,
      "emissions_delta_pct": -19.0,
      "emergency_delay_delta_pct": -41.0,
      "is_best": true
    }
  ]
}
```
**This endpoint only evaluates — it never applies a strategy.** This separation is the technical implementation of the "AI does not decide, the human does" product principle (`PRD.md` §11) and must never be collapsed into a single evaluate-and-apply call, even for convenience.

`is_best` is server-computed from the Optimization scorer (`docs/phase-4-ai-intelligence/35_STRATEGY_OPTIMIZATION.md`) — Unity does not re-rank candidates itself; it only highlights whichever one arrives with `is_best: true` (`DESIGN_GUIDELINES.md` §21).

## 11. Strategy Application API

### `POST /strategy/apply`
Request:
```json
{ "scenario_id": "SCN_001", "strategy_type": "diversion" }
```
Response:
```json
{
  "decision_id": "DEC_001",
  "applied": true,
  "explanation": { "...": "see §17" },
  "resulting_state": { "...": "NetworkState, same shape as §7" }
}
```
Only callable with a `scenario_id` that was previously returned by `/strategy/evaluate` — the backend should reject application of a strategy_type that wasn't actually evaluated for that scenario, to guarantee the explanation shown to the player always corresponds to a real simulation, not a guess.

## 12. Incident API

### `POST /incident/trigger`
```json
{ "incident_type": "accident", "junction_id": "J2", "severity": "medium" }
```
Used both by the procedural generator (backend-driven) and, during development/testing, manually — e.g., to force the exact accident-at-J2 moment for a rehearsed demo (matches `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md` §7.1's scripted trigger, once that trigger is backend-driven in Stage B).

## 13. WebSocket Protocol

Single connection, `ws://localhost:8000/ws`, all messages share the envelope:
```json
{ "type": "<message_type>", "simulation_time": 361.0, "payload": { "...": "..." } }
```
`WebSocketClient` (Unity) dispatches on `type`. Three message types are defined for MVP:

| `type` | Payload shape | Consumed by |
|---|---|---|
| `vehicle_state` | §14 | `VehicleStateReceiver` |
| `signal_state` | §15 | `TrafficLightController` (via `Junction`) |
| `incident_event` | §16 | `IncidentTrigger` |

## 14. Vehicle State Message

```json
{
  "type": "vehicle_state",
  "simulation_time": 361.0,
  "payload": {
    "vehicles": [
      { "id": "car_104", "vehicle_type": "car", "x": 124.5, "y": 0, "z": 48.2,
        "rotation_y": 92.0, "speed_kmh": 8.4, "lane": "J2_N_0" }
    ]
  }
}
```
`vehicle_type` values are restricted to `DATA_CONTRACT.md`'s `vehicle_types` list. `x/y/z` are Unity world-space coordinates — the backend is responsible for the SUMO-coordinate → Unity-coordinate transform (not Unity), so that a coordinate-system change never requires a Unity code change.

## 15. Signal State Message

```json
{
  "type": "signal_state",
  "simulation_time": 361.0,
  "payload": { "junction_id": "J2", "phase": "NS_GREEN", "seconds_remaining": 18 }
}
```

## 16. Incident Event Message

```json
{
  "type": "incident_event",
  "simulation_time": 380.0,
  "payload": {
    "incident_type": "accident",
    "junction_id": "J2",
    "severity": "medium",
    "active": true
  }
}
```
`active: false` on the same `incident_type`/`junction_id` pair signals resolution (matches the `end_time` concept in `docs/phase-3-digital-twin/28_INCIDENT_ENGINE.md`) — Unity clears the corresponding visual marker when it receives this.

## 17. Explanation Schema

Used by `/recommendation` and `/strategy/apply` responses. **Fixed four-field shape, no exceptions**:
```json
{
  "action": "Divert Traffic",
  "why": "Reduces queue spillback at J2 while preserving the emergency route.",
  "evidence": {
    "delay_change": "-31%",
    "queue_change": "-28%",
    "spillback_risk": "LOW",
    "emergency_route": "SAFE"
  },
  "confidence": 0.84
}
```
Unity's `ExplanationPanel.Show()` renders exactly these four fields in this order (`ACTION / WHY / EVIDENCE / CONFIDENCE`) — it does not add, omit, or reorder fields, and it does not fabricate additional claims not present in `evidence`. This mirrors `docs/phase-4-ai-intelligence/37_EXPLAINABLE_AI.md` and `DESIGN_GUIDELINES.md` §24 precisely; this schema is the single point where those two documents' requirements become an enforceable contract.

**Language constraint carried into the schema**: `why` and any string in `evidence` must use predicted/probabilistic phrasing ("Predicted to reduce...", not "Will eliminate...") — this is a backend authoring responsibility, not something Unity can fix by rewording on display (`DESIGN_GUIDELINES.md` §49).

## 18. Strategy Schema

```json
{
  "strategy_type": "diversion",
  "label": "Divert Traffic",
  "parameters": { "diversion_percent": 30 }
}
```
`strategy_type` ∈ `DATA_CONTRACT.md`'s `strategy_types`. `label` is the human-readable string Unity displays directly — the backend owns copy for this field so wording stays consistent with `EXPLAINABLE_AI` language rules without Unity needing its own lookup table.

## 19. Scenario Result Schema

```json
{
  "scenario_id": "SCN_001",
  "junction_id": "J2",
  "results": [ { "...": "see §10 for full shape" } ]
}
```

## 20. Game Session Schema

```json
{
  "session_id": "SESSION_20260823_001",
  "scenario_seed": 42,
  "level": 3,
  "player_decisions": [
    { "scenario_id": "SCN_001", "recommended": "diversion",
      "player_action": "approve", "outcome_score_delta": 17 }
  ]
}
```
Matches the logging shape already frozen in `TECH_STACK.md` §29 — this schema is what gets persisted for research/reproducibility purposes and is not itself rendered directly in the UI.

## 21. API State Machine

The sequence of calls per decision point is fixed and must be followed in order — the backend may reject out-of-order calls:
```text
GET /traffic/prediction
      ↓ (if risk_level >= MEDIUM, or on incident_event)
GET /recommendation                (optional convenience — for the initial alert)
      ↓ (player presses SIMULATE)
POST /strategy/evaluate            → returns scenario_id + results
      ↓ (player reviews CounterfactualCardPanel, picks or accepts best)
POST /strategy/apply               → must reference the scenario_id from above
      ↓
resulting_state consumed → HUD/score update
```
This ordering is what the `ScenarioDirector`/`GameState` phase machine (`UNITY_ARCHITECTURE.md` §11) is built to drive — the Unity state machine and this API state machine are two views of the same sequence and must be kept in lockstep if either changes.

## 22. Mock/Stub Mode

Every endpoint and message type in this document must have a corresponding fixture (hand-authored JSON matching the exact schema above) usable by Unity's `Stub` connection mode (`UNITY_ARCHITECTURE.md` §21). **Fixtures are generated from real backend output where possible** (run the real endpoint once, save the response as a fixture) rather than hand-typed from imagination, so Stub mode data stays structurally honest even before live integration is stable.

## 23. Timeout & Recovery

| Call | Timeout budget | On timeout |
|---|---|---|
| `GET /traffic/state`, `/prediction` | 1s | Retry once, then fall back to last-known value or Stub fixture |
| `POST /strategy/evaluate` | 3s (matches the latency budget target in `docs/phase-3-digital-twin/27_SCENARIO_ENGINE.md` / `46_LATENCY_ANALYSIS.md`) | Fall back to Stub fixture results for that scenario; do not block the UI indefinitely |
| `POST /strategy/apply` | 2s | Retry once; if it still fails, treat as a soft error and let the player retry the APPROVE action rather than silently failing |
| WebSocket | Reconnect with backoff (1s, 2s, 4s, capped at 10s) | If reconnection fails after 3 attempts, drop to Stub mode for the remainder of the session |

These budgets exist specifically to protect the live demo — a hung request must never freeze the game on stage.

## 24. Versioning

No formal API versioning scheme for the hackathon build (single client, single server, deployed together). If this contract needs to change after Round 1 submission but before Round 2 implementation, **update this document and treat the previous version as void** — do not maintain parallel versions during the build window.

## 25. Integration Tests

Minimum verification before considering Phase 5 (backend integration) done, per `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md` §17.4's one-at-a-time swap rule:

```text
[ ] GET /traffic/state returns a NetworkState Unity can deserialize without error
[ ] GET /traffic/prediction risk_level matches the probability banding rule in §8
[ ] POST /strategy/evaluate returns 3-4 results with exactly one is_best: true
[ ] POST /strategy/apply rejects a strategy_type not present in the referenced
    scenario_id's prior /strategy/evaluate results
[ ] A full evaluate → apply round trip produces an Explanation whose evidence
    values match the applied strategy's actual ScenarioResult numbers
    (no drift between what was simulated and what was explained)
[ ] WebSocket vehicle_state stream drives at least one VehicleAgent visibly,
    end to end, for a 30-second observation window without desync
[ ] Simulated timeout (kill the backend mid-call) triggers Stub-mode fallback
    without a Unity exception or frozen UI
```

## Cross-References
- Unity-side consumer of every schema in this document: `UNITY_ARCHITECTURE.md` §16–19
- Backend-side source of truth these endpoints wrap: `docs/phase-2-architecture/17_API_SPECIFICATION.md` (original backend-only spec — this document is its Unity-facing superset/restatement; if they diverge, reconcile toward this one being the actual implemented contract)
- Shared ID values referenced throughout: `DATA_CONTRACT.md`
- Explanation content rules enforced by §17: `docs/phase-4-ai-intelligence/37_EXPLAINABLE_AI.md`, `DESIGN_GUIDELINES.md` §24 & §49
- Latency budgets referenced in §23: `docs/phase-3-digital-twin/27_SCENARIO_ENGINE.md`, `docs/phase-5-validation/46_LATENCY_ANALYSIS.md`
