# TEST_PLAN.md — Verification & Quality Assurance Plan

**Status**: [IMPLEMENTED] Pytest Suite / [PLANNED] Unity Integration Testing  
**Last Updated**: 2026-08-23

---

## 1. Test Execution Commands

### 1.1 Python Backend & Intelligence Test Suite
```bash
# Run complete test suite
python -m pytest tests/

# Run specific test modules
python -m pytest tests/test_prediction.py
python -m pytest tests/test_scenario_engine.py
python -m pytest tests/test_phase7_game_engine.py
python -m pytest tests/test_phase6_decision_ui.py
python -m pytest tests/test_phase5_experiments.py
```

### 1.2 End-to-End Integration Verification Command
```bash
python experiments/run_scenario_engine.py
```

---

## 2. Test Coverage Matrix

| Test Level | Module Target | Verification Goal | Status |
| :--- | :--- | :--- | :--- |
| **Unit** | `intelligence/prediction/` | Accuracy > 75%, MAE < 40m | `[IMPLEMENTED]` |
| **Unit** | `backend/game_server/` | Scoring, multipliers, badge logic | `[IMPLEMENTED]` |
| **Integration** | `simulation/bridge/` | SUMO snapshot & restore state loop | `[IMPLEMENTED]` |
| **API** | `backend/api/` | REST endpoint status & payload parsing | `[IMPLEMENTED]` |
| **Client** | `game/unity/` | Unity uGUI event handling & movement | `[PLANNED]` |
| **E2E** | Full Pipeline | Unity -> FastAPI -> XGBoost -> SUMO -> Unity | `[PLANNED]` |
