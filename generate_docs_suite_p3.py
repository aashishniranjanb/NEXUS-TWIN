import os

docs_dir = "docs"
os.makedirs(docs_dir, exist_ok=True)

def write_doc(filename, content):
    filepath = os.path.join(docs_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created/Updated {filepath}")

# ---------------------------------------------------------
# 11. TEST_PLAN.md (PHASE 9)
# ---------------------------------------------------------
test_plan_content = """# TEST_PLAN.md — Verification & Quality Assurance Plan

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
"""
write_doc("TEST_PLAN.md", test_plan_content)

# ---------------------------------------------------------
# 12. EXPERIMENT_PLAN.md (PHASE 10)
# ---------------------------------------------------------
exp_plan_content = """# EXPERIMENT_PLAN.md — Benchmark & Evaluation Experiments

**Status**: [IMPLEMENTED] Existing Experiment Suite (`experiments/`)  
**Last Updated**: 2026-08-23

---

## 1. Defensible Experiment Designs

### Experiment 1: Control Benchmark (Fixed-Time vs Reactive vs NEXUS-TWIN)
- **Goal**: Measure network-wide delay reduction.
- **Execution Script**: `python experiments/run_baselines.py`
- **Metrics**: Average vehicle delay (s), mean queue length (m), throughput (veh/hr).

### Experiment 2: AI Recommendation vs Simulated Optimal Strategy
- **Goal**: Validate if XGBoost + Strategy Optimizer selects the global optimal strategy.
- **Execution Script**: `python experiments/run_scenario_engine.py`

### Experiment 3: Human-Only vs AI-Assisted Gameplay
- **Goal**: Evaluate player score and decision speed with vs without XAI explanation.
- **Execution**: Unity game session logging.

---

## 2. Empirical Baseline Metrics (Recorded in `results/`)
- Fixed-Time Baseline Delay: **0.42 s/veh**
- Reactive Adaptive Delay: **0.28 s/veh**
- Digital Twin Counterfactual Optimal: **0.18 s/veh** (**57% delay reduction**)
"""
write_doc("EXPERIMENT_PLAN.md", exp_plan_content)

# ---------------------------------------------------------
# 13. DEPLOYMENT.md (PHASE 11)
# ---------------------------------------------------------
deployment_content = """# DEPLOYMENT.md — Local Setup & Build Pipeline

**Status**: [IMPLEMENTED] Local Dev Environment / [PLANNED] Standalone Builds  
**Last Updated**: 2026-08-23

---

## 1. Prerequisites
- **Python**: 3.12+ (Virtual environment recommended)
- **SUMO**: 1.27.1 (with `SUMO_HOME` environment variable set)
- **Unity**: Unity 6 LTS (6000.0.x) with URP package

---

## 2. Startup Sequence (Local Execution)

```bash
# Step 1: Start Backend API & Game Engine
python backend/api/decision_server.py

# Step 2: Verify Backend Status
curl http://localhost:8000/api/status

# Step 3: Launch Unity Client (from Unity Editor or Standalone Build)
# Open project in game/unity/ and press Play
```
"""
write_doc("DEPLOYMENT.md", deployment_content)

# ---------------------------------------------------------
# 14. ASSET_PIPELINE.md (PHASE 12)
# ---------------------------------------------------------
asset_content = """# ASSET_PIPELINE.md — Visual & Audio Asset Roster

**Status**: [PLANNED] Unity Asset Pipeline  
**Visual Style**: Low-Poly Stylized Smart City  
**Last Updated**: 2026-08-23

---

## 1. Asset Attribution Roster

| Asset Category | Source / Pack | Author | License | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Vehicles** | Kenney Car Kit / City Kit | Kenney.nl | CC0 1.0 Universal | Sedan, Bus, Truck, Police, Fire |
| **Emergency** | Low Poly Ambulance | CC0 Asset Pack | CC0 | Priority Ambulance Model |
| **Buildings** | Low-Poly City Assets | OpenGameArt | CC0 / MIT | Background Buildings |
| **UI Icons** | Game-Icons.net | Various | CC BY 3.0 | Traffic light, ambulance, shield icons |
"""
write_doc("ASSET_PIPELINE.md", asset_content)

# ---------------------------------------------------------
# 15. PERFORMANCE_GUIDELINES.md (PHASE 13)
# ---------------------------------------------------------
perf_content = """# PERFORMANCE_GUIDELINES.md — Performance Budgets & Optimization

**Status**: [PLANNED] Technical Performance Budget  
**Target FPS**: 60 FPS (Desktop Target) / 30 FPS Minimum  
**Last Updated**: 2026-08-23

---

## 1. Performance Budgets

| Metric | Desktop Target | WebGL Limit |
| :--- | :--- | :--- |
| **Frame Rate** | 60 FPS | 30 FPS |
| **Draw Calls** | < 150 | < 80 |
| **Triangles / Scene** | < 100k | < 50k |
| **Active Vehicles** | Up to 500 pooled | Up to 200 pooled |
| **WebSocket Update Rate**| 10 Hz | 5 Hz |

---

## 2. Key Optimization Strategies
1. **Vehicle Prefab Pooling**: Pre-instantiate 300 vehicle GameObjects at startup (`VehiclePoolManager.cs`). Never `Instantiate()` or `Destroy()` during simulation.
2. **URP Material Batching**: Use a single master palette texture for all low-poly environment meshes.
"""
write_doc("PERFORMANCE_GUIDELINES.md", perf_content)

# ---------------------------------------------------------
# 16. ERROR_HANDLING.md (PHASE 14)
# ---------------------------------------------------------
err_content = """# ERROR_HANDLING.md — Resilience & Fallback Matrix

**Status**: [IMPLEMENTED] Python Exception Handling / [PLANNED] Unity Mock Mode  
**Last Updated**: 2026-08-23

---

## 1. Failure Resilience Matrix

| Failure Mode | Detection Mechanism | Recovery Action | User Experience |
| :--- | :--- | :--- | :--- |
| **SUMO Crashes / Timeout** | TraCI connection reset | Restart SUMO instance; restore snapshot | Notification banner; simulation resets |
| **FastAPI Offline** | Unity REST request timeout (3s) | Switch Unity client to Mock Offline Mode | HUD banner: *"Offline Mode Active"* |
| **WebSocket Disconnect** | Socket error handler | Auto-reconnect with exponential backoff | Signal status indicator turns yellow |
| **Invalid Strategy** | API `400 Bad Request` | Fallback to `do_nothing` strategy | Error dialog: *"Invalid action"* |
"""
write_doc("ERROR_HANDLING.md", err_content)

# ---------------------------------------------------------
# 17. SECURITY.md (PHASE 15)
# ---------------------------------------------------------
sec_content = """# SECURITY.md — Payload Validation & Security Specs

**Status**: [IMPLEMENTED] Input Sanitize Contracts  
**Last Updated**: 2026-08-23

---

## 1. Security & Validation Rules
1. **Input Payload Validation**: All incoming REST/WebSocket JSON payloads are strictly validated against Pydantic schemas in `backend/schemas/scenario_models.py`.
2. **Localhost Scoping**: The API server binds to `127.0.0.1` by default for local development.
3. **Model Artifact Integrity**: Trained XGBoost pickle files (`congestion_model.pkl`) are loaded strictly from the local `data/` directory.
"""
write_doc("SECURITY.md", sec_content)

print("Phases 9-15 docs generated successfully.")
