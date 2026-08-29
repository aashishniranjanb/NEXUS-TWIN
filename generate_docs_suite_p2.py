import os

docs_dir = "docs"
os.makedirs(docs_dir, exist_ok=True)

def write_doc(filename, content):
    filepath = os.path.join(docs_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created/Updated {filepath}")

# ---------------------------------------------------------
# 4. UNITY_ARCHITECTURE.md (PHASE 2)
# ---------------------------------------------------------
unity_arch_content = """# UNITY_ARCHITECTURE.md — Unity 6 Game Client Architecture

**Status**: [PLANNED] Canonical Unity Client Architecture Spec  
**Target Engine**: Unity 6 (URP)  
**Last Updated**: 2026-08-23

---

## 1. Executive Summary
This document defines the complete software architecture for the NEXUS-TWIN Unity 6 game client. Unity acts exclusively as the **visualization, rendering, UI, and player interaction layer**. All traffic simulation, AI prediction, strategy scoring, and explainability remain authoritative in the Python backend.

---

## 2. Technology Stack & Packages
- **Engine**: Unity 6 LTS (6000.x)
- **Render Pipeline**: Universal Render Pipeline (URP) - Performance-focused low-poly style
- **Camera System**: Cinemachine 3.0 (Isometric strategic camera with focus presets)
- **Input System**: Unity Input System package (Mouse, Keyboard, Touch support)
- **UI System**: Unity UI (uGUI) + Canvas Scaler
- **Networking**: `UnityWebRequest` (HTTP/REST) + Native WebSockets (Realtime state streaming)

---

## 3. Project Directory Structure (`game/unity/`)

```text
game/unity/
├── Assets/
│   ├── Scenes/
│   │   ├── MainMenu.unity
│   │   ├── GameplayCorridor.unity
│   │   └── ResultSummary.unity
│   ├── Scripts/
│   │   ├── Core/
│   │   │   ├── GameManager.cs
│   │   │   ├── GameStateMachine.cs
│   │   │   └── EventBus.cs
│   │   ├── Traffic/
│   │   │   ├── TrafficRenderer.cs
│   │   │   ├── VehicleController.cs
│   │   │   ├── VehiclePoolManager.cs
│   │   │   └── SignalController.cs
│   │   ├── Gameplay/
│   │   │   ├── IncidentManager.cs
│   │   │   ├── PlayerController.cs
│   │   │   └── ChallengeEvaluator.cs
│   │   ├── UI/
│   │   │   ├── HUDController.cs
│   │   │   ├── RecommendationPanel.cs
│   │   │   ├── CounterfactualUI.cs
│   │   │   ├── ExplainabilityPanel.cs
│   │   │   └── LeaderboardUI.cs
│   │   ├── DigitalTwin/
│   │   │   ├── TwinStateSynchronizer.cs
│   │   │   └── GhostFutureVisualizer.cs
│   │   ├── Networking/
│   │   │   ├── ApiClient.cs
│   │   │   ├── WebSocketClient.cs
│   │   │   └── DTOs/
│   │   └── Scoring/
│   │       ├── ScoreManager.cs
│   │       └── TrustManager.cs
│   ├── Prefabs/
│   │   ├── Vehicles/ (Car, Bus, Truck, EmergencyAmbulance)
│   │   ├── Signals/ (TrafficLightPrefab)
│   │   └── UI/ (DialogPrefabs, ScorePopups)
│   ├── Materials/ (URP Low-Poly Palettes)
│   ├── Models/ (Low-poly environment & vehicle meshes)
│   ├── Audio/ (SFX & ambient city loops)
│   └── Resources/
```

---

## 4. Scene GameObject Hierarchy (`GameplayCorridor.unity`)

```text
[Scene Root]
├── World/
│   ├── Environment/ (Buildings, Terrain, Props)
│   ├── RoadNetwork/ (J1, J2, J3 Intersections & Connectors)
│   ├── TrafficLights/ (TL_J1, TL_J2, TL_J3)
│   └── VehicleHolder/ (Pooled vehicle GameObjects)
├── Cameras/
│   ├── MainCamera (URP Base Camera)
│   ├── CinemachineBrain
│   ├── CM_StrategicIsometric (Primary view)
│   ├── CM_IncidentFocus (Focus on J2 accident)
│   └── CM_EmergencyFollow (Follows Ambulance)
├── Managers/
│   ├── GameManager (Persists session state)
│   ├── TwinStateSynchronizer (REST & WebSocket receiver)
│   ├── VehiclePoolManager (Instantiates & reuses 500+ cars)
│   └── AudioServer
└── Canvas_HUD/
    ├── HeaderZone (Timer, Streak, Points, Active Incident)
    ├── WorldOverlayZone (3D World Labels, Queue Indicators)
    ├── ActionZone (Strategy Selection Buttons, Emergency Preempt)
    └── ExplanationPanel (XAI Rationale & AI Trust Bar)
```

---

## 5. Division of Responsibility
- **Python Backend**: Computes SUMO steps, extracts vehicle states, trains XGBoost, evaluates counterfactual futures, scores moves, generates XAI text.
- **Unity Client**: Renders vehicle positions received via WebSocket at 30-60 FPS, interpolates smooth movement, handles player button clicks, displays HUD, plays audio.
"""
write_doc("UNITY_ARCHITECTURE.md", unity_arch_content)

# ---------------------------------------------------------
# 5. API_SPECIFICATION.md (PHASE 3)
# ---------------------------------------------------------
api_spec_content = """# API_SPECIFICATION.md — Backend REST & WebSocket Specification

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
"""
write_doc("API_SPECIFICATION.md", api_spec_content)

# ---------------------------------------------------------
# 6. DATA_CONTRACT.md (PHASE 4)
# ---------------------------------------------------------
data_contract_content = """# DATA_CONTRACT.md — Single Source of Truth Data Schemas

**Status**: [IMPLEMENTED] Authoritative Data Contract  
**Last Updated**: 2026-08-23

---

## 1. Overview
This document serves as the **single source of truth** for all data structures exchanged between Unity, FastAPI, Python Intelligence, and SUMO.

---

## 2. Identifiers & Enums

### 2.1 Junction Identifiers
- `J1`: North Intersection
- `J2`: Central Bottleneck Intersection
- `J3`: South Intersection

### 2.2 Vehicle Types
- `car`: Standard passenger car
- `bus`: Public transit vehicle
- `truck`: Heavy freight transport
- `motorcycle`: Two-wheeled light vehicle
- `ambulance`: Priority emergency vehicle (Red LED)
- `police`: Emergency law enforcement
- `fire`: Emergency fire engine

### 2.3 Strategy Types
- `do_nothing`: Maintain baseline controller unchanged
- `green_extend`: Extend green light phase duration on target junction
- `diversion`: Reroute percentage of incoming traffic to alternate edges
- `dynamic_lane`: Open shoulder/dynamic lane for traffic flow
- `emergency_priority`: Force green wave corridor for priority vehicle

---

## 3. Core JSON Schemas

### 3.1 `TrafficState` Schema
```json
{
  "type": "object",
  "required": ["step", "active_vehicles", "avg_speed_kmh", "total_waiting_time_s", "junctions"],
  "properties": {
    "step": {"type": "number", "minimum": 0, "description": "Simulation time in seconds"},
    "active_vehicles": {"type": "integer", "minimum": 0},
    "avg_speed_kmh": {"type": "number", "minimum": 0.0, "unit": "km/h"},
    "total_waiting_time_s": {"type": "number", "minimum": 0.0, "unit": "seconds"},
    "junctions": {"type": "object"}
  }
}
```

### 3.2 `Strategy` Schema
```json
{
  "type": "object",
  "required": ["strategy_id", "strategy_type", "parameters"],
  "properties": {
    "strategy_id": {"type": "string", "example": "green_extend_J2"},
    "strategy_type": {"type": "string", "enum": ["do_nothing", "green_extend", "diversion", "dynamic_lane", "emergency_priority"]},
    "parameters": {"type": "object"}
  }
}
```
"""
write_doc("DATA_CONTRACT.md", data_contract_content)

# ---------------------------------------------------------
# 7. DIGITAL_TWIN_INTEGRATION.md (PHASE 5)
# ---------------------------------------------------------
digital_twin_content = """# DIGITAL_TWIN_INTEGRATION.md — Digital Twin & Scenario Isolation

**Status**: [IMPLEMENTED] Core Simulation Architecture  
**Authoritative Simulator**: SUMO 1.27.1 via TraCI  
**Last Updated**: 2026-08-23

---

## 1. Architecture Overview
The Digital Twin maintains a strict separation between the **Authoritative Live World** and **Counterfactual Exploratory Futures**.

```text
AUTHORITATIVE LIVE SUMO WORLD
         │
         ▼ (Snapshot: saveState)
TEMPORARY STATE MEMORY / XML SNAPSHOT
         │
  ┌──────┴─────────────────────────┐
  ▼                                ▼
FUTURE A (Do Nothing)      FUTURE B (Apply Green Extend)
  │                                │
  ▼ (Simulate Horizon 180s)        ▼ (Simulate Horizon 180s)
Metrics A                        Metrics B
  └──────┬─────────────────────────┘
         ▼ (Restore: loadState)
AUTHORITATIVE LIVE SUMO WORLD (Unmutated State)
```

---

## 2. State Snapshot & Isolation Rules
1. **Never Mutate Authoritative Live State During Exploration**: Any counterfactual evaluation MUST call `saveState()` before modifying signals or routes.
2. **Mandatory State Restoration**: After the simulation horizon (e.g., 180s forward) completes and metrics are recorded, `loadState()` MUST restore the exact pre-evaluation snapshot.
3. **Deterministic Seeding**: Counterfactual runs MUST use identical random seeds to ensure valid comparison against baseline.
"""
write_doc("DIGITAL_TWIN_INTEGRATION.md", digital_twin_content)

# ---------------------------------------------------------
# 8. GAMEPLAY_SYSTEM.md (PHASE 6)
# ---------------------------------------------------------
gameplay_content = """# GAMEPLAY_SYSTEM.md — Gameplay Loop & Player Mechanics

**Status**: [IMPLEMENTED] Python Core Engine / [PLANNED] Unity UI Integration  
**Player Role**: Traffic Crisis Commander  
**Last Updated**: 2026-08-23

---

## 1. Core Gameplay Loop
```text
TRAFFIC EVENT (Accident/Surge/Emergency)
  └─► AI CONGESTION DETECTION & PREDICTION
        └─► AI STRATEGY RECOMMENDATION (With XAI Rationale)
              └─► PLAYER DECISION (Accept AI / Modify / Override)
                    └─► DIGITAL TWIN SIMULATION & COMPARISON
                          └─► SCORE, STREAK & BADGE REWARD
```

---

## 2. 3-Minute Judge Demo Scenario
1. **00:00 - 00:30 (Baseline)**: Steady traffic flow through J1, J2, J3. Player views isometric 3D corridor.
2. **00:30 (Accident Spawn)**: Minor collision on approach to J2 blocking Lane 1. Queue starts building.
3. **00:45 (AI Alert & Prediction)**: AI warns: *"Congestion risk at J2 within 5 minutes (Confidence: 88%)"*.
4. **01:00 (Emergency Event)**: Ambulance enters N_to_J1 edge heading towards South Hospital.
5. **01:15 (Recommendation)**: AI recommends *"Emergency Green Corridor + Route Diversion via E1"*.
6. **01:30 (Player Action)**: Player approves recommendation. Digital Twin simulates outcomes.
7. **02:00 (Execution)**: Ambulance clears corridor with 0.0s delay. Queue dissipates.
8. **02:45 (Results & Score)**: Player earns +1200 Points, Beat-the-AI Multiplier (x2.0), and unlocks "Emergency Ace" Badge.
"""
write_doc("GAMEPLAY_SYSTEM.md", gameplay_content)

# ---------------------------------------------------------
# 9. GAME_STATE_MACHINE.md (PHASE 7)
# ---------------------------------------------------------
gsm_content = """# GAME_STATE_MACHINE.md — Game State Machine Specification

**Status**: [IMPLEMENTED] Python Engine Logic / [PLANNED] Unity State Machine  
**Last Updated**: 2026-08-23

---

## 1. State Diagram

```text
[IDLE] ──► [EVENT] ──► [ANALYSIS] ──► [DECISION] ──► [SIMULATION] ──► [RESULT] ──► [SCORE] ──► [IDLE]
```

---

## 2. State Definitions

| State | Entry Condition | Valid Transitions | API Call | Timeout |
| :--- | :--- | :--- | :--- | :--- |
| `IDLE` | Game session started | `EVENT` | `GET /api/state` | N/A |
| `EVENT` | Queue > threshold or Emergency | `ANALYSIS` | `GET /api/game/event` | N/A |
| `ANALYSIS` | Event spawned | `DECISION` | `GET /api/traffic/prediction` | 10s |
| `DECISION` | AI recommendation ready | `SIMULATION` | `POST /api/game/move` | 30s |
| `SIMULATION` | Player move submitted | `RESULT` | `POST /api/evaluate` | 15s |
| `RESULT` | Horizon evaluation done | `SCORE` | None | 5s |
| `SCORE` | Result acknowledged | `IDLE`, `NEXT_EVENT` | `POST /api/game/end` | N/A |
"""
write_doc("GAME_STATE_MACHINE.md", gsm_content)

# ---------------------------------------------------------
# 10. AI_INTEGRATION.md (PHASE 8)
# ---------------------------------------------------------
ai_content = """# AI_INTEGRATION.md — Intelligence, Prediction & Explainability

**Status**: [IMPLEMENTED] Active Python Machine Learning Pipeline  
**Last Updated**: 2026-08-23

---

## 1. AI Pipeline Overview
```text
TraCI Traffic State ──► Feature Engineering ──► XGBoost Predictor ──► Strategy Generator ──► XAI Engine
```

---

## 2. XGBoost Congestion Predictor Specifications
- **Model Files**: `data/congestion_model.pkl`
- **Classifier Target**: `will_congest_5min` (Binary: Queue > 40m)
- **Regressor Target**: `future_queue_5min_m` (Continuous meters)
- **Verified Metrics**:
  - Accuracy: **80.26%**
  - F1 Score: **0.8079**
  - Queue MAE: **33.68 meters**

---

## 3. Explainable AI (XAI) Rationale Format
Explanations must follow the non-negotiable Responsible AI semantics:
- **Action**: Clear statement of intervention.
- **Reason**: Quantitative metric driver.
- **Expected Impact**: Delay reduction & spillback transfer evaluation.
- **Confidence**: Expressed as dynamic probability score (never absolute certainty).
"""
write_doc("AI_INTEGRATION.md", ai_content)

print("Phases 2-8 docs generated successfully.")
