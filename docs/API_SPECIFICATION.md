# API_SPECIFICATION.md — Backend REST & WebSocket Specification

**Status**: [PARTIALLY IMPLEMENTED] Current Python HTTP server / [PLANNED] FastAPI Server  
**Base URL**: `http://localhost:8000/api`  
**WebSocket URL**: `ws://localhost:8000/ws`  
**Last Updated**: 2026-08-23

---

## 1. REST Endpoints

### 1.1 `GET /api/status`
- **Purpose**: System health check & version verification.
- **Method**: `GET`
- **Response**: `200 OK`
```json
{
  "status": "ONLINE",
  "system": "NEXUS-TWIN Digital Twin Engine",
  "version": "1.0.0",
  "simulation": "SUMO v1.27.1",
  "network": "3-Junction Corridor (J1/J2/J3)",
  "predictor_accuracy": "80.26%"
}
```

### 1.2 `GET /api/state`
- **Purpose**: Fetch live network traffic state snapshot.
- **Method**: `GET`
- **Response**: `200 OK`
```json
{
  "timestamp": 120.5,
  "network_metrics": {
    "active_vehicles": 142,
    "avg_waiting_time_s": 0.28,
    "avg_speed_kmh": 38.2,
    "mean_queue_length_m": 24.5,
    "total_throughput": 480
  },
  "junctions": {
    "J2": {
      "phase": 0,
      "phase_name": "N-S Green",
      "total_queue_m": 35.0,
      "avg_waiting_time_s": 0.32,
      "vehicle_count": 25
    }
  }
}
```

### 1.3 `POST /api/evaluate`
- **Purpose**: Evaluate a counterfactual strategy scenario in parallel future.
- **Method**: `POST`
- **Request Payload**:
```json
{
  "horizon_seconds": 180,
  "junction_id": "J2",
  "strategy_type": "green_extend",
  "extension_seconds": 20.0
}
```
- **Response**: `200 OK`
```json
{
  "timestamp": 1724390000.0,
  "horizon_seconds": 180,
  "recommended_strategy": {
    "strategy_id": "green_extend_J2",
    "strategy_type": "green_extend",
    "parameters": {"junction_id": "J2", "extension_seconds": 20.0}
  },
  "recommended_score": 0.185,
  "explanation": {
    "action": "Extend Green Phase by 20s at J2",
    "reason": "Prevents northbound queue buildup of 35.0m from crossing threshold",
    "expected_impact": "Reduces delay by 22% with 0.0m spillback transfer",
    "confidence": "88%"
  },
  "candidates": []
}
```

### 1.4 `POST /api/emergency`
- **Purpose**: Trigger emergency vehicle green wave priority override.
- **Method**: `POST`
- **Request Payload**:
```json
{
  "corridor": "J1-J2-J3",
  "vehicle_id": "AMBULANCE_01",
  "junction_id": "J2"
}
```
- **Response**: `200 OK`
```json
{
  "status": "PREEMPTION_ACTIVE",
  "vehicle_id": "AMBULANCE_01",
  "corridor": "J1-J2-J3",
  "estimated_clearance_time_s": 14.5
}
```

---

## 2. WebSocket Streaming Endpoints (`ws://localhost:8000/ws`)

### 2.1 Message Stream: `vehicle_state` (Frequency: 10 Hz)
```json
{
  "type": "vehicle_state",
  "step": 1245,
  "vehicles": [
    {
      "id": "veh_102",
      "type": "car",
      "x": 145.2,
      "y": 0.0,
      "z": 320.1,
      "speed_mps": 11.5,
      "angle_deg": 90.0,
      "lane_id": "J1_to_J2_0"
    }
  ]
}
```

### 2.2 Message Stream: `signal_state` (Frequency: Event-Driven)
```json
{
  "type": "signal_state",
  "junction_id": "J2",
  "phase_index": 2,
  "phase_state": "GGrrrrGGrrrr",
  "remaining_duration_s": 12.0
}
```
