# UNITY_ARCHITECTURE.md — Unity 6 Game Client Architecture

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
