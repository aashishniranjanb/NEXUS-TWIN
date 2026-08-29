# NEXUS-TWIN UI Integration Contract & Guide

> [!IMPORTANT]
> **No Fake Metrics**: All traffic intelligence, anomaly scores, fingerprint classifications, network propagation delays, simulation deltas, safety critic reviews, and routing directions must trace back to the deterministic API responses. Do not hard-code mock values.

---

## 1. Core Endpoints & URLs

- **Base URL**: `http://localhost:8000`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`

---

## 2. API Endpoints

### 1. Unified Decision Analysis
- **Method**: `POST`
- **Path**: `/api/v1/demo/analyze`
- **Purpose**: Runs the full end-to-end 10-stage decision pipeline. Used to populate the general Command Center view (State, Prediction, Anomaly, Fingerprint, Domino, Simulation, Critic).
- **Payload**:
  ```json
  {
    "city": "Philadelphia",
    "intersection_id": 0,
    "scenario": "INCIDENT_LIKE_DISRUPTION",
    "emergency_mode": false,
    "hour": 17,
    "weekend": 0,
    "seed": 42
  }
  ```

### 2. Progressive Streaming Endpoint (SSE)
- **Method**: `GET`
- **Path**: `/api/v1/decision/stream`
- **Params**: `?city=Philadelphia&intersection_id=0&scenario=INCIDENT_LIKE_DISRUPTION`
- **Purpose**: Progressive Server-Sent Events stream of the 12 agent reasoning stages. Excellent for loading state animations.

### 3. AI Dynamic Route & Spillover Optimizer
- **Method**: `POST`
- **Path**: `/api/v1/routing/optimize`
- **Purpose**: Calculates optimal routes and dynamic alternatives using travel times, congestion rates, spillover threat, and emergency-priority preemption.
- **Payload**:
  ```json
  {
    "origin": 889,
    "destination": 463,
    "mode": "emergency",
    "city": "Philadelphia",
    "hour": 17,
    "weekend": 0
  }
  ```

### 4. Human Decision Actuation
- **Method**: `POST`
- **Path**: `/api/v1/decision/human-action`
- **Purpose**: Dispatch signal actuation commands when the operator clicks Approve or Override.
- **Payload**:
  ```json
  {
    "event_id": "EVT_PHILADELPHIA_0_1724922875",
    "action": "APPROVE",
    "selected_strategy_id": "STRAT_DIVERT_TRAFFIC",
    "operator_notes": "Supervisor approved diversion to secondary corridor."
  }
  ```

### 5. System Status Probe
- **Method**: `GET`
- **Path**: `/api/v1/system/status`
- **Purpose**: Probe live model loading and dataset availability status.
