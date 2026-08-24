# CURRENT_STATE_AUDIT.md — NEXUS-TWIN Repository Audit

**Status**: [IMPLEMENTED] / [PARTIALLY IMPLEMENTED] / [PLANNED] / [FUTURE] / [LEGACY] Audit Record  
**Last Updated**: 2026-08-23

---

## 1. Executive Summary
This document records the empirical audit of the NEXUS-TWIN codebase. It categorizes all modules, files, and resources into exact status categories to ensure implementation decisions align strictly with real code evidence.

---

## 2. Component Categorization

### A. Implemented & Verified Components [IMPLEMENTED]
- **Traffic State Extraction (`simulation/bridge/traffic_state.py`)**: Queries TraCI live for active vehicle count, average network speed, waiting times, and per-junction/lane queue metrics.
- **Digital Twin Scenario Engine (`simulation/bridge/scenario_engine.py`)**: Implements snapshot (`saveState`) -> apply candidate strategy -> forward horizon simulation -> metric collection -> restore (`loadState`) loop.
- **Congestion Predictor (`intelligence/prediction/congestion_predictor.py`)**: XGBoost classifier (will congest in 5 min) and regressor (5 min future queue in meters). Enforces run-based train/test splits.
- **Strategy Generator (`intelligence/strategy/strategy_generator.py`)**: Formulates counterfactual candidates (`green_extend`, `diversion`, `dynamic_lane`, `emergency_priority`, `do_nothing`).
- **Strategy Optimizer (`intelligence/strategy/strategy_optimizer.py`)**: Evaluates candidate scenario results against baseline using weighted scoring & penalty formulas.
- **Explainable AI Engine (`intelligence/explainability/explainable_ai.py`)**: Generates structured explanations, contrastive rationale, and dynamic confidence calibration for recommendations.
- **Python Game Engine & Scoring (`backend/game_server/game_engine.py`)**: Manages session state, contextual event spawning, beat-the-AI scoring, streaks, multipliers, badge unlocks, and persistent leaderboard.
- **Decision Server REST API (`backend/api/decision_server.py`)**: HTTP server exposing status, live state, what-if evaluation, emergency override, and game session endpoints.
- **Metrics Collection (`simulation/bridge/metrics_collector.py`)**: Aggregates step history, throughput, travel time, and emission stats.
- **SUMO Network (`simulation/network/`)**: 3-junction corridor (`nexus.net.xml`, `nexus.edg.xml`, `nexus.nod.xml`).

### B. Partially Implemented Components [PARTIALLY IMPLEMENTED]
- **Decision REST API Server (`backend/api/decision_server.py`)**: Currently runs on Python `http.server`. Migration to **FastAPI** with WebSocket support is `[PLANNED]`.
- **Perception Layer (`perception/`)**: Contains package initializers (`perception/traffic`, `perception/vision`). YOLO edge integration is `[FUTURE]`.

### C. Planned Components [PLANNED]
- **Unity 6 Game Client (`game/unity/`)**: 3D low-poly playable client using URP and Cinemachine.
- **FastAPI Routing Layer (`backend/api/`)**: Production FastAPI app with WebSocket streaming for vehicle and signal state.

### D. Future Extensions [FUTURE]
- **Multi-Agent Orchestration (`backend/agents/`)**: LangGraph supervisor pattern for perception, strategy, safety, and explanation agents.
- **Hardware / Edge Signal Controller (`hardware/esp32/`)**: ESP32 microcontroller receiving signal phase commands via MQTT.
- **Computer Vision Perception (`perception/traffic/`)**: Real-time camera feed vehicle detection & queue estimation.

### E. Legacy & Archived Components [LEGACY]
- **Old Phase Documentation (`docs/legacy/phase-*`)**: Legacy research and setup roadmaps preserved in `docs/legacy/`.
- **Simplistic Web Dashboard (`docs/legacy/web_ui/`)**: Old HTML/JS frontend archived in favor of Unity 3D client.

---

## 3. Module Dependency Matrix

| Module | Primary Dependencies | Status |
| :--- | :--- | :--- |
| `simulation/bridge/traffic_state.py` | `traci` | `[IMPLEMENTED]` |
| `simulation/bridge/scenario_engine.py` | `traci`, `traffic_state`, `metrics_collector` | `[IMPLEMENTED]` |
| `intelligence/prediction/congestion_predictor.py` | `xgboost`, `pandas`, `sklearn` | `[IMPLEMENTED]` |
| `intelligence/strategy/strategy_optimizer.py` | `backend/schemas/scenario_models` | `[IMPLEMENTED]` |
| `intelligence/explainability/explainable_ai.py` | `strategy_optimizer`, `scenario_models` | `[IMPLEMENTED]` |
| `backend/game_server/game_engine.py` | `strategy_optimizer`, `scenario_models` | `[IMPLEMENTED]` |
| `backend/api/decision_server.py` | `game_engine`, `explainable_ai`, `strategy_generator` | `[PARTIALLY IMPLEMENTED]` |
| `game/unity/` | Unity 6, URP, Cinemachine, REST/WebSocket | `[PLANNED]` |

---

## 4. Test Coverage Summary
- `tests/test_prediction.py`: Passed (XGBoost training & prediction evaluation).
- `tests/test_scenario_engine.py`: Passed (SUMO snapshot/restore loop).
- `tests/test_phase7_game_engine.py`: Passed (Game session scoring & badges).
- `tests/test_phase6_decision_ui.py`: Passed (REST API endpoints).
- `tests/test_phase5_experiments.py`: Passed (Baseline experiment suite).
