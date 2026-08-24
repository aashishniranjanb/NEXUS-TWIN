# EXPERIMENT_PLAN.md — Benchmark & Evaluation Experiments

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
