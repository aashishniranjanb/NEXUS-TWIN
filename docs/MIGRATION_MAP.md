# MIGRATION_MAP.md — NEXUS-TWIN Architectural Migration Map

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
