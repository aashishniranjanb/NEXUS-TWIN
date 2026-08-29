# API SPECIFICATION

| Field | Value |
|---|---|
| Status | Level-1 (authoritative) |
| Owner | Laptop 2 |
| Base URL | `http://localhost:8000` |
| Content type | `application/json` |
| Auth | None (P0). Not in scope. |

---

## 1. Purpose

Freeze the HTTP contract so frontend and backend can be built in parallel without waiting for each
other.

## 2. Rules

1. **Inspect before adding.** Existing routes are listed in section 4. Do not create a duplicate
   endpoint for something that already exists.
2. **Never break an existing contract.** Unity depends on several of these routes.
3. Every response includes the envelope fields in section 3.
4. Units are in field names (`_m`, `_s`, `_kmh`). Probabilities are floats in `[0,1]`, never
   percentages. The frontend formats for display.
5. `session_id` is required on every stateful call.

## 3. Response envelope

Every successful response includes:

```json
{
  "session_id": "s_7f3a",
  "generated_at": "2026-08-29T10:14:03Z",
  "mode": "LIVE",
  "degraded": false,
  "data_source": "geotab",
  "...": "endpoint-specific payload"
}
```

| Field | Meaning |
|---|---|
| `mode` | `LIVE` or `DEMO` |
| `degraded` | True when a model artifact was missing and a fallback was used |
| `data_source` | `geotab`, `simulation`, or `fixture` — displayed in the provenance panel |

Errors:

```json
{ "error": { "code": "MODEL_UNAVAILABLE", "message": "…", "retryable": true } }
```

| Status | When |
|---|---|
| 200 | Success, including degraded success |
| 400 | Validation failure (Pydantic) |
| 404 | Unknown `session_id` or `simulation_id` |
| 422 | Semantically invalid request (unknown junction or strategy type) |
| 500 | Unhandled server error |
| 503 | Dependency unavailable and no fallback exists |

## 4. Existing routes — preserve

| Method | Path | Status |
|---|---|---|
| GET | `/health` | Keep |
| GET | `/api/status` | Keep |
| GET | `/traffic/state`, `/api/state` | Keep as aliases of `/api/traffic/current` |
| GET | `/traffic/prediction` | Keep as alias |
| GET | `/recommendation` | Keep as alias |
| POST | `/strategy/evaluate`, `/api/evaluate` | Keep |
| POST | `/strategy/apply` | Keep |
| POST | `/incident/trigger` | Keep |
| POST | `/api/emergency` | Keep |
| POST | `/api/game/start`, `/move`, `/end`; GET `/api/game/leaderboard` | Keep, unused by web |
| WS | `/ws/traffic`, `/ws` | Keep for Unity |

## 5. Endpoints

### 5.1 `GET /api/health`

Response: `{ "status": "ok", "uptime_s": 412.5, "models_loaded": true, "database": "up" }`

Used by the frontend provider to choose `LIVE` or `DEMO`. Must respond in under 1.5 s.

---

### 5.2 `GET /api/traffic/current`

Query: `session_id` (required), `step` (optional int, demo scenario step).

```json
{
  "timestamp": 128.4,
  "scenario_step": 2,
  "network": {
    "active_vehicles": 148,
    "avg_speed_kmh": 31.2,
    "avg_waiting_time_s": 42.8,
    "mean_queue_length_m": 64.3,
    "flow_veh_min": 21.4,
    "density_pct": 68
  },
  "junctions": {
    "J2": {
      "junction_id": "J2",
      "state": "CRITICAL",
      "queue_length_m": 118.0,
      "avg_speed_kmh": 18.4,
      "avg_waiting_time_s": 74.2,
      "vehicle_count": 38,
      "flow_veh_min": 9.1,
      "density_pct": 88,
      "signal_phase": 1,
      "signal_phase_name": "N-S Green",
      "baseline": { "queue_length_m": 42.0, "avg_waiting_time_s": 26.5 },
      "deviation": { "queue_length_m": 2.81, "avg_speed_kmh": -1.94 }
    }
  }
}
```

`baseline` is the Geotab contextual expectation for this junction, hour, and weekend flag.
`deviation` is expressed in standard deviations. Both are required — the fingerprint and anomaly
panels are meaningless without them.

---

### 5.3 `POST /api/traffic/predict`

Request: `{ "session_id": "s_7f3a", "junction_id": "J2", "horizon_minutes": 5 }`

```json
{
  "junction_id": "J2",
  "horizon_minutes": 5,
  "congestion_probability": 0.87,
  "predicted_queue_m": 156.0,
  "predicted_avg_speed_kmh": 12.6,
  "will_congest": true,
  "confidence": 0.84,
  "model": "xgboost_classifier_v1",
  "feature_importances": { "queue_delta": 0.31, "avg_waiting_time_s": 0.22, "deviation_ratio": 0.17 }
}
```

---

### 5.4 `POST /api/anomaly/detect`

Request: `{ "session_id": "…", "junction_id": "J2" }`

```json
{
  "junction_id": "J2",
  "is_anomaly": true,
  "anomaly_score": 0.93,
  "threshold": 0.60,
  "model": "isolation_forest_v1",
  "top_deviations": [
    { "signal": "queue_growth", "z_score": 3.4 },
    { "signal": "speed_deviation", "z_score": -2.9 }
  ]
}
```

---

### 5.5 `POST /api/fingerprint/analyze`

Request: `{ "session_id": "…", "junction_id": "J2" }`

```json
{
  "junction_id": "J2",
  "type": "INCIDENT_LIKE",
  "confidence": 0.91,
  "signals": [
    { "name": "queue_growth", "value": 0.34, "z_score": 3.4, "contribution": 0.38 },
    { "name": "speed_deviation", "value": -21.6, "z_score": -2.9, "contribution": 0.29 },
    { "name": "direction_imbalance", "value": 0.72, "z_score": 2.2, "contribution": 0.18 },
    { "name": "waiting_time_deviation", "value": 47.7, "z_score": 2.6, "contribution": 0.15 }
  ],
  "alternatives": [ { "type": "DEMAND_SURGE", "confidence": 0.06 } ],
  "rationale": "Sharp speed drop with rapid one-directional queue growth and no matching demand increase."
}
```

`type` ∈ `NORMAL | RECURRING_CONGESTION | INCIDENT_LIKE | DEMAND_SURGE | SIGNAL_RELATED | UNKNOWN`.

---

### 5.6 `POST /api/domino/predict`

Request: `{ "session_id": "…", "source_junction": "J2", "horizon_minutes": 10 }`

```json
{
  "source": { "junction_id": "J2", "risk": 0.87 },
  "propagation": [
    { "junction_id": "J1", "risk": 0.73, "eta_minutes": 4, "path": ["J2","J1"], "mechanism": "upstream_queue_spillback" },
    { "junction_id": "J3", "risk": 0.41, "eta_minutes": 7, "path": ["J2","J3"], "mechanism": "downstream_flow_disruption" }
  ],
  "intervention_window": {
    "status": "CRITICAL",
    "remaining_seconds": 360,
    "expires_at": "2026-08-29T10:20:03Z",
    "consequence": "Predicted spillover reaches J1.",
    "urgency": "ACT_NOW"
  }
}
```

`propagation` is sorted by risk descending. The intervention window is returned here because it is
derived from the earliest ETA; it is not a separate model.

---

### 5.7 `POST /api/strategy/generate`

Request: `{ "session_id": "…", "junction_id": "J2" }`

```json
{
  "strategies": [
    { "strategy_id": "cand_do_nothing", "strategy_type": "do_nothing", "label": "DO NOTHING", "parameters": {}, "description": "Baseline control condition." },
    { "strategy_id": "cand_diversion_25", "strategy_type": "diversion", "label": "DIVERT TRAFFIC", "parameters": { "diversion_percent": 25.0, "junction_id": "J2" }, "description": "Divert 25% of J2 approach volume to the parallel corridor." },
    { "strategy_id": "cand_green_extend_20s", "strategy_type": "green_extend", "label": "EXTEND GREEN", "parameters": { "extension_seconds": 20.0, "junction_id": "J2" } },
    { "strategy_id": "cand_emergency_priority", "strategy_type": "emergency_priority", "label": "EMERGENCY PRIORITY", "parameters": { "corridor": "J1-J2-J3" } }
  ]
}
```

`do_nothing` is always present and always first.

---

### 5.8 `POST /api/simulation/run`

Request:

```json
{ "session_id": "…", "horizon_seconds": 180, "strategy_ids": ["cand_do_nothing","cand_diversion_25","cand_green_extend_20s","cand_emergency_priority"] }
```

Response (synchronous when under 5 s; otherwise returns `202` with `simulation_id` and status
`running`):

```json
{
  "simulation_id": "sim_a91c",
  "status": "complete",
  "horizon_seconds": 180,
  "baseline_strategy_id": "cand_do_nothing",
  "results": [
    {
      "strategy_id": "cand_diversion_25",
      "strategy_type": "diversion",
      "predicted_queue_m": 68.0,
      "predicted_delay_s": 34.2,
      "predicted_throughput": 512,
      "spillover_risk": 0.21,
      "emergency_eta_s": 96.0,
      "per_junction_metrics": { "J1": { "queue_m": 44.0 }, "J2": { "queue_m": 68.0 }, "J3": { "queue_m": 29.0 } },
      "score": 118.4,
      "delta_vs_baseline": { "queue_m": -0.41, "delay_s": -0.36, "spillover_risk": -0.52 },
      "success": true
    }
  ],
  "best": { "overall": "cand_diversion_25", "lowest_spillover": "cand_diversion_25", "best_emergency": "cand_emergency_priority" }
}
```

Lower `score` is better. `delta_vs_baseline` is fractional change against `do_nothing`.

---

### 5.9 `GET /api/simulation/{simulation_id}`

Returns the same body. Used for polling when `run` returned `202`.

---

### 5.10 `POST /api/decision/evaluate`

Request: `{ "session_id": "…", "simulation_id": "sim_a91c" }`

```json
{
  "recommended_strategy_id": "cand_diversion_25",
  "action_label": "DIVERT TRAFFIC",
  "confidence": 0.89,
  "evidence": [
    { "label": "J2 queue growth", "value": "+34%", "source": "traffic_state" },
    { "label": "J1 spillover probability", "value": "73%", "source": "domino" },
    { "label": "Predicted queue reduction", "value": "-41%", "source": "simulation" },
    { "label": "Emergency corridor", "value": "preserved", "source": "simulation" }
  ],
  "tradeoffs": [ { "label": "Alternate corridor delay", "value": "+8%" } ],
  "safety": { "status": "PASS", "checks": [ { "name": "emergency_access", "status": "PASS" }, { "name": "no_junction_worsened", "status": "PASS" } ] },
  "rationale": "Diversion reduces predicted downstream spillover while maintaining acceptable emergency access.",
  "alternatives_considered": 4
}
```

`safety.status` ∈ `PASS | WARN | FAIL`. A `FAIL` blocks approval in the UI.

---

### 5.11 `POST /api/decision/approve`

Request:

```json
{ "session_id": "…", "simulation_id": "sim_a91c", "strategy_id": "cand_diversion_25", "decision": "APPROVE", "operator_note": "" }
```

`decision` ∈ `APPROVE | OVERRIDE`. On `OVERRIDE`, `strategy_id` is the operator's choice.

```json
{
  "decision_id": "dec_31b7",
  "applied_strategy_id": "cand_diversion_25",
  "decision": "APPROVE",
  "outcome": {
    "before": { "queue_m": 118.0, "delay_s": 53.4, "spillover_risk": 0.73 },
    "after":  { "queue_m": 68.0,  "delay_s": 34.2, "spillover_risk": 0.21 },
    "delta":  { "queue_m": -0.42, "delay_s": -0.36, "spillover_risk": -0.71 },
    "spillover_prevented": true,
    "network_score": 87
  },
  "ai_vs_human": { "ai_strategy_id": "cand_diversion_25", "human_strategy_id": "cand_diversion_25", "agreed": true, "score_difference": 0.0 }
}
```

---

### 5.12 `POST /api/copilot/query` — P1

Request: `{ "session_id": "…", "question": "why divert instead of extending green?" }`

```json
{
  "answer": "…",
  "tool_calls": [ { "tool": "compare_strategies", "arguments": {}, "result_summary": "…" } ],
  "citations": [ { "claim": "spillover risk 0.21", "tool": "simulate_strategy" } ]
}
```

Every numeric claim must have a citation. Uncited numbers are stripped before the response is
returned.

---

### 5.13 `GET /api/events/stream` — P1

Server-Sent Events. Event types: `state_update`, `anomaly_detected`, `prediction_update`,
`simulation_progress`, `decision_recorded`. Not required for the demo; polling is the P0 path.

---

### 5.14 `GET /api/provenance`

```json
{
  "dataset": "BigQuery-Geotab Intersection Congestion Dataset",
  "city": "Chicago",
  "intersections": { "J1": 1234, "J2": 5678, "J3": 9012 },
  "rows_used": 184230,
  "pipeline": ["Provided Traffic Data","Feature Engineering","AI Intelligence","Prediction","Simulation","Decision"],
  "models": [
    { "name": "congestion_classifier", "inputs": ["queue_length_m","queue_delta","hour_sin","baseline_stopped_p50"] },
    { "name": "anomaly_detector", "inputs": ["deviation_vector"] }
  ]
}
```

This endpoint is what makes the dataset claim auditable rather than asserted.

## 6. Endpoint summary

| Method | Path | Priority | Frontend consumer |
|---|---|---|---|
| GET | `/api/health` | MUST | Provider mode selection |
| GET | `/api/traffic/current` | MUST | Map, Current State |
| POST | `/api/traffic/predict` | MUST | AI Forecast |
| POST | `/api/anomaly/detect` | MUST | Fingerprint panel |
| POST | `/api/fingerprint/analyze` | MUST | Fingerprint panel |
| POST | `/api/domino/predict` | MUST | Domino panel, map overlay, Intervention Window |
| POST | `/api/strategy/generate` | MUST | Strategy panel |
| POST | `/api/simulation/run` | MUST | Digital Twin panel |
| GET | `/api/simulation/{id}` | MUST | Digital Twin polling |
| POST | `/api/decision/evaluate` | MUST | Explanation panel |
| POST | `/api/decision/approve` | MUST | Decision + Outcome panels |
| GET | `/api/provenance` | MUST | Provenance indicator |
| POST | `/api/copilot/query` | OPTIONAL (P1) | Copilot |
| GET | `/api/events/stream` | OPTIONAL (P1) | Live updates |

## 7. Failure modes

| Condition | Response |
|---|---|
| Model missing | 200 with `degraded: true` and fallback values |
| Unknown junction | 422 `UNKNOWN_JUNCTION` |
| Unknown strategy type | 422 `UNKNOWN_STRATEGY_TYPE` |
| Simulation timeout | 200 with per-strategy `success: false` |
| Database down | 200; write skipped; `degraded: true` |

No endpoint returns 500 for a condition the system can anticipate.

## 8. Testing

- Pytest contract test per endpoint against its Pydantic model.
- Golden-file test for the demo scenario: fixed `session_id` and step produce byte-stable payloads.
- Alias test: legacy routes still return their original shapes.
- Frontend Zod parse test against committed fixtures.

## 9. Acceptance criteria

1. OpenAPI schema generated at `/docs` covers every endpoint in section 6.
2. Frontend fixtures and backend responses validate against the same schemas.
3. All legacy routes unchanged.
4. Every `MUST` endpoint returns a valid response with model artifacts deleted.

## 10. Future work

Versioned `/api/v1` prefix, pagination for historical runs, SSE, idempotency keys on decisions.
