# NEXUS-TWIN API Contract
# Version: 1.0 — Frozen for hackathon sprint
# Integration Owner: Aashish
# Date: 2026-08-25

---

## Purpose
This document defines the stable API contract between:
- Unity game (Aashish)
- Web Command Center (Friend 1)
- FastAPI Backend (Friend 2)

No endpoint signature may change without updating this document
and notifying all three team members.

---

## Base URL
```
http://localhost:8000
```

---

## FROZEN ENDPOINTS (do not change signatures)

### GET /health
```json
{ "status": "ok" }
```

### GET /api/status
```json
{
  "predictor_accuracy": 0.8026,
  "model": "XGBoostClassifier",
  "uptime_seconds": 142,
  "mode": "mock"
}
```

### GET /traffic/state
```json
{
  "junctions": {
    "J1": { "queue_m": 12.4, "speed_kmh": 38.2, "flow_vph": 720 },
    "J2": { "queue_m": 35.0, "speed_kmh": 14.1, "flow_vph": 280, "incident": true },
    "J3": { "queue_m": 8.2,  "speed_kmh": 42.0, "flow_vph": 890 }
  },
  "timestamp": 361
}
```

### GET /traffic/prediction?junction_id=J2
```json
{
  "junction_id": "J2",
  "congestion_probability": 0.87,
  "confidence": 0.82,
  "forecast_horizon_seconds": 300
}
```

### POST /strategy/evaluate
Request:
```json
{
  "junction_id": "J2",
  "strategies": ["extend_green", "diversion", "emergency_priority", "do_nothing"]
}
```
Response:
```json
{
  "recommended": "diversion",
  "confidence": 0.82,
  "results": [
    {
      "strategy": "extend_green",
      "label": "Extend Green Phase by 25s",
      "delay_change_pct": -12.4,
      "queue_change_pct": -18.2,
      "emergency_eta_change_sec": 4.0,
      "emissions_change_pct": -8.1,
      "is_best": false,
      "explanation": "Flushes arterial queues before spillback occurs."
    },
    {
      "strategy": "diversion",
      "label": "Divert Traffic via Bypass",
      "delay_change_pct": -37.6,
      "queue_change_pct": -30.1,
      "emergency_eta_change_sec": -24.0,
      "emissions_change_pct": -14.2,
      "is_best": true,
      "explanation": "Prevents J2 gridlock and guarantees AMBULANCE_01 clearance."
    },
    {
      "strategy": "emergency_priority",
      "label": "Emergency Priority Corridor",
      "delay_change_pct": 8.0,
      "queue_change_pct": 12.0,
      "emergency_eta_change_sec": -31.0,
      "emissions_change_pct": 5.0,
      "is_best": false,
      "explanation": "Prioritizes ambulance at cost of +8% general network delay."
    },
    {
      "strategy": "do_nothing",
      "label": "No Action (Baseline)",
      "delay_change_pct": 45.0,
      "queue_change_pct": 62.0,
      "emergency_eta_change_sec": 24.0,
      "emissions_change_pct": 35.0,
      "is_best": false,
      "explanation": "Unmitigated congestion. Gridlock in ~90 seconds."
    }
  ]
}
```

### POST /strategy/apply
Request:
```json
{
  "junction_id": "J2",
  "strategy": "diversion",
  "approved_by": "human_operator"
}
```
Response:
```json
{
  "applied": true,
  "strategy": "diversion",
  "expected_duration_seconds": 300
}
```

---

## NEW ENDPOINTS (Friend 2 may add freely)

### GET /emergency/eta
```json
{
  "eta_seconds": 142.3,
  "delayed": false,
  "threshold_seconds": 30.0,
  "ambulance_id": "AMBULANCE_01"
}
```

### GET /events/active
```json
{
  "events": [
    { "junction": "J2", "type": "accident", "severity": "high", "started_at": 15 },
    { "junction": "J3", "type": "surge",    "severity": "medium", "started_at": 45 }
  ]
}
```

### GET /agents/status
```json
{
  "agents": [
    { "name": "TrafficAgent",    "status": "active", "last_recommendation": "extend_green" },
    { "name": "EmergencyAgent",  "status": "active", "last_recommendation": "emergency_priority" },
    { "name": "SafetyAgent",     "status": "active", "last_recommendation": "safe" }
  ]
}
```

---

## WebSocket (optional)

```
WS /ws/traffic
```
Emits every 100ms:
```json
{
  "type": "state_update",
  "junctions": { ... },
  "timestamp": 361
}
```

---

## Version history
| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-25 | Initial freeze for hackathon sprint |
