import os

docs_dir = "docs"
os.makedirs(docs_dir, exist_ok=True)

def write_doc(filename, content):
    filepath = os.path.join(docs_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created/Updated {filepath}")

# ---------------------------------------------------------
# 1. CURRENT_STATE_AUDIT.md
# ---------------------------------------------------------
audit_content = """# CURRENT_STATE_AUDIT.md — NEXUS-TWIN Repository Audit

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
"""
write_doc("CURRENT_STATE_AUDIT.md", audit_content)

# ---------------------------------------------------------
# 2. MIGRATION_MAP.md
# ---------------------------------------------------------
migration_map_content = """# MIGRATION_MAP.md — NEXUS-TWIN Architectural Migration Map

**Status**: [IMPLEMENTED] Canonical Repository Mapping  
**Last Updated**: 2026-08-23

---

## 1. Overview
This map details the precise migration path of legacy modules and files into their canonical homes within the NEXUS-TWIN architecture.

---

## 2. File Location Mapping

| Original Location | Canonical Location | Category | Status | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `src/traffic_state.py` | `simulation/bridge/traffic_state.py` | Simulation Bridge | `[IMPLEMENTED]` | Encapsulates TraCI query logic. |
| `src/scenario_engine.py` | `simulation/bridge/scenario_engine.py` | Simulation Bridge | `[IMPLEMENTED]` | Digital Twin counterfactual engine. |
| `src/metrics_collector.py` | `simulation/bridge/metrics_collector.py` | Simulation Bridge | `[IMPLEMENTED]` | Simulation metrics logger. |
| `src/scenario_models.py` | `backend/schemas/scenario_models.py` | Schemas | `[IMPLEMENTED]` | Shared DTO data models. |
| `src/decision_server.py` | `backend/api/decision_server.py` | API Layer | `[IMPLEMENTED]` | Backend REST API server. |
| `src/game_engine.py` | `backend/game_server/game_engine.py` | Game Server | `[IMPLEMENTED]` | Session, scoring, badges & leaderboard. |
| `src/strategy_generator.py` | `intelligence/strategy/strategy_generator.py` | Intelligence | `[IMPLEMENTED]` | Candidate strategy generation. |
| `src/strategy_optimizer.py` | `intelligence/strategy/strategy_optimizer.py` | Intelligence | `[IMPLEMENTED]` | Scoring & optimization algorithms. |
| `src/explainable_ai.py` | `intelligence/explainability/explainable_ai.py` | Intelligence | `[IMPLEMENTED]` | Natural language XAI engine. |
| `src/feature_engineering.py` | `intelligence/feature_engineering/feature_engineering.py` | Intelligence | `[IMPLEMENTED]` | Feature processing pipeline. |
| `prediction/congestion_predictor.py` | `intelligence/prediction/congestion_predictor.py` | Intelligence | `[IMPLEMENTED]` | XGBoost ML predictor. |
| `Resources/` | `docs/legacy/` | Documentation | `[LEGACY]` | Archived early research roadmaps. |
| `web/` | `docs/legacy/web_ui/` | Frontend | `[LEGACY]` | Archived 2D web UI in favor of Unity 3D client. |

---

## 3. Package & Import Reference Mapping

```python
# Old import style (DEPRECATED):
from src.scenario_models import Strategy, ScenarioResult
from prediction.congestion_predictor import CongestionPredictor

# Canonical import style (CURRENT):
from backend.schemas.scenario_models import Strategy, ScenarioResult
from intelligence.prediction.congestion_predictor import CongestionPredictor
from simulation.bridge.traffic_state import TrafficStateExtractor
```
"""
write_doc("MIGRATION_MAP.md", migration_map_content)

# ---------------------------------------------------------
# 3. DOCUMENTATION_CONFLICTS.md
# ---------------------------------------------------------
conflicts_content = """# DOCUMENTATION_CONFLICTS.md — Conflict Audit & Resolution Log

**Status**: [IMPLEMENTED] Active Resolution Record  
**Last Updated**: 2026-08-23

---

## 1. Overview
This document tracks all identified conflicts across product, technical, design, and plan specifications (`PRD.md`, `TECH_STACK.md`, `DESIGN_GUIDELINES.md`, `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md`), along with their authoritative resolutions.

---

## 2. Conflict Log

### Conflict 001: Web UI vs Unity 3D Client
- **Source Documents**: Legacy `Resources/phase-6-productization/` vs `PRD.md` & `TECH_STACK.md`.
- **Description**: Early documentation referenced a 2D web dashboard using HTML5 Canvas (`web/`). `PRD.md` and `TECH_STACK.md` mandate Unity 6 with URP as the canonical game client.
- **Resolution**: `web/` is archived as `[LEGACY]` in `docs/legacy/web_ui/`. **Unity 6 + URP is the authoritative client**.

### Conflict 002: Decision Server Technology (Python `http.server` vs FastAPI)
- **Source Documents**: `backend/api/decision_server.py` implementation vs `TECH_STACK.md` §12.
- **Description**: Current code uses Python standard `http.server`. `TECH_STACK.md` mandates FastAPI with WebSocket support.
- **Resolution**: Current `decision_server.py` is tagged `[PARTIALLY IMPLEMENTED]`. It serves MVP HTTP endpoints today, and will be upgraded to FastAPI + WebSockets during Unity integration.

### Conflict 003: Document Location (`docs/game/` vs `docs/`)
- **Source Documents**: Repository layout vs prompt specification §4 & §29.
- **Description**: `PRD.md`, `TECH_STACK.md`, `DESIGN_GUIDELINES.md`, and `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md` existed inside `docs/game/`.
- **Resolution**: Copies are maintained in `docs/` to satisfy both the modular layout (`docs/game/`) and the root documentation contract (`docs/`).

### Conflict 004: Multi-Agent Role in MVP
- **Source Documents**: Early design notes vs `PRD.md` §14 & `TECH_STACK.md` §17–21.
- **Description**: Ambiguity around whether LangGraph multi-agent orchestration is required for the initial hackathon demo.
- **Resolution**: **Multi-Agent is tagged [FUTURE] (Phase 2)**. The MVP relies strictly on deterministic Python Strategy Generator + XGBoost Predictor + Scenario Engine. Multi-agent architecture must be documented but NOT required for MVP execution.
"""
write_doc("DOCUMENTATION_CONFLICTS.md", conflicts_content)

print("Phase 1 docs generated successfully.")
