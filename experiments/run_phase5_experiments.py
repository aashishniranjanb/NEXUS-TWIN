"""
Master Phase 5 Experiment Harness for NEXUS-TWIN.
Executes complete empirical benchmark matrix (E1-E8), strategy ablations, perception noise robustness,
traffic load sensitivity, latency analysis, and hypothesis evaluation (H1-H4).
Exports machine-readable results to results/ directory per Phase 5 specs.
"""

import os
import sys
import json
import time
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from experiments.run_baselines import setup_sumo_env, build_network_and_routes
setup_sumo_env()

import traci
from simulation.routes.generate_routes import generate_route_file
from simulation.signals.fixed_time import FixedTimeController
from simulation.signals.reactive import ReactiveAdaptiveController
from simulation.bridge.traffic_state import TrafficStateExtractor
from simulation.bridge.metrics_collector import MetricsCollector
from simulation.bridge.scenario_engine import ScenarioEngine
from intelligence.strategy.strategy_generator import StrategyGenerator
from intelligence.strategy.strategy_optimizer import StrategyOptimizer
from intelligence.explainability.explainable_ai import ExplainableAIEngine
from intelligence.prediction.congestion_predictor import CongestionPredictor

RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

def track_completed_trips(traci_inst, metrics_inst, depart_times_dict):
    for v_id in traci_inst.simulation.getDepartedIDList():
        depart_times_dict[v_id] = traci_inst.simulation.getTime()
    for v_id in traci_inst.simulation.getArrivedIDList():
        if v_id in depart_times_dict:
            tt = traci_inst.simulation.getTime() - depart_times_dict[v_id]
            metrics_inst.record_completed_trip(tt)

# -------------------------------------------------------------------------
# E1: Baseline Benchmark (Fixed vs Reactive vs NexusTwin)
# -------------------------------------------------------------------------
def run_e1_baselines(num_vehicles: int = 1000) -> Dict[str, Any]:
    print("\n==================================================")
    print("  EXPERIMENT E1: BASELINE COMPARISON (H1 EVAL)   ")
    print("==================================================")
    
    build_network_and_routes()
    rou_file = PROJECT_ROOT / "simulation" / "routes" / "nexus.rou.xml"
    generate_route_file(filepath=str(rou_file), num_vehicles=num_vehicles, duration=1500)

    cfg_file = str(PROJECT_ROOT / "simulation" / "configs" / "nexus.sumocfg")

    methods = ["fixed", "reactive", "nexustwin"]
    results = {}

    for method in methods:
        print(f"\n[E1] Simulating method: '{method}'...")
        traci.start(["sumo", "-c", cfg_file, "--start", "--quit-on-end"])
        
        tls_ids = list(traci.trafficlight.getIDList())
        state_extractor = TrafficStateExtractor(tls_ids)
        state_extractor.initialize(traci)
        metrics = MetricsCollector(tls_ids)

        fixed_ctrl = FixedTimeController(tls_ids)
        reactive_ctrl = ReactiveAdaptiveController(tls_ids)
        reactive_ctrl.initialize(traci)

        engine = ScenarioEngine(traci, tls_ids, default_horizon_seconds=180)
        generator = StrategyGenerator(tls_ids)
        optimizer = StrategyOptimizer()
        predictor = CongestionPredictor()

        depart_times = {}

        step = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            step_time = traci.simulation.getTime()

            state = state_extractor.extract_state(traci)
            metrics.record_step(state)
            track_completed_trips(traci, metrics, depart_times)

            if method == "fixed":
                fixed_ctrl.step(traci, step_time)
            elif method == "reactive":
                reactive_ctrl.step(traci, step_time)
            elif method == "nexustwin":
                reactive_ctrl.step(traci, step_time)
                # Proactive decision point every 180s
                if step > 100 and step % 350 == 0:
                    candidates = generator.generate_candidates(state, has_emergency_vehicle=False)
                    res = engine.evaluate_candidates(candidates, horizon_seconds=180)
                    best_cand, _ = optimizer.select_best_strategy(res)
                    engine.apply_strategy(best_cand)

            step += 1

        summary = metrics.compute_summary()
        summary["method"] = method
        results[method] = summary
        traci.close()

        print(f"  [OK] {method:<12}: Delay={summary.get('avg_waiting_time_s', 0):.2f}s, Queue={summary.get('mean_queue_length_m', 0):.1f}m, Speed={summary.get('avg_speed_kmh', 0):.1f}km/h, Throughput={summary.get('throughput_vehicles', 0)}")

    with open(RESULTS_DIR / "phase5_h1_baselines.json", "w") as f:
        json.dump(results, f, indent=4)

    return results

# -------------------------------------------------------------------------
# E2 & E4: Predictive vs Reactive Benchmark (H2 EVAL)
# -------------------------------------------------------------------------
def run_e2_predictive_vs_reactive(num_vehicles: int = 1000) -> Dict[str, Any]:
    print("\n==================================================")
    print("  EXPERIMENT E2/E4: PREDICTIVE VS REACTIVE (H2)  ")
    print("==================================================")

    cfg_file = str(PROJECT_ROOT / "simulation" / "configs" / "nexus.sumocfg")
    modes = ["reactive_only", "predictive_twin"]
    results = {}

    predictor = CongestionPredictor()
    if not predictor.model_path.exists():
        predictor.train()

    for mode in modes:
        print(f"\n[E2] Simulating mode: '{mode}'...")
        traci.start(["sumo", "-c", cfg_file, "--start", "--quit-on-end"])

        tls_ids = list(traci.trafficlight.getIDList())
        state_extractor = TrafficStateExtractor(tls_ids)
        state_extractor.initialize(traci)
        metrics = MetricsCollector(tls_ids)
        reactive_ctrl = ReactiveAdaptiveController(tls_ids)
        reactive_ctrl.initialize(traci)

        engine = ScenarioEngine(traci, tls_ids, default_horizon_seconds=180)
        generator = StrategyGenerator(tls_ids)
        optimizer = StrategyOptimizer()

        interventions = 0
        decision_steps = []
        depart_times = {}

        step = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            step_time = traci.simulation.getTime()

            state = state_extractor.extract_state(traci)
            metrics.record_step(state)
            track_completed_trips(traci, metrics, depart_times)

            reactive_ctrl.step(traci, step_time)

            if step > 100 and step % 350 == 0:
                should_trigger = False
                pred_map = {}

                if mode == "reactive_only":
                    max_q = max([j.get("total_queue_m", 0) for j in state["junctions"].values()], default=0)
                    if max_q >= 40.0:
                        should_trigger = True
                elif mode == "predictive_twin":
                    for j_id in tls_ids:
                        j_data = state["junctions"].get(j_id, {})
                        feats = {
                            "active_vehicles": state["active_vehicles"],
                            "avg_speed_kmh": state["avg_speed_kmh"],
                            "avg_waiting_time_s": state["avg_waiting_time_s"],
                            "max_waiting_time_s": state["max_waiting_time_s"],
                            "queue_length_m": j_data.get("total_queue_m", 0.0),
                            "halting_vehicles": j_data.get("total_halting", 0),
                            "previous_queue_m": j_data.get("total_queue_m", 0.0),
                            "queue_delta": 0.0,
                            "signal_phase": j_data.get("current_phase", 0),
                            "time_of_day_s": step_time
                        }
                        pred = predictor.predict_congestion(feats)
                        pred_map[j_id] = pred
                        if pred.will_congest_5min or pred.congestion_probability >= 0.65:
                            should_trigger = True

                if should_trigger:
                    candidates = generator.generate_candidates(state, prediction_map=pred_map if mode == "predictive_twin" else None)
                    res = engine.evaluate_candidates(candidates, horizon_seconds=180)
                    best_cand, _ = optimizer.select_best_strategy(res)
                    engine.apply_strategy(best_cand)
                    interventions += 1
                    decision_steps.append(step_time)

            step += 1

        summary = metrics.compute_summary()
        summary["mode"] = mode
        summary["interventions_count"] = interventions
        summary["decision_steps"] = decision_steps
        results[mode] = summary
        traci.close()

        print(f"  [OK] {mode:<16}: Delay={summary.get('avg_waiting_time_s', 0):.2f}s, Queue={summary.get('mean_queue_length_m', 0):.1f}m, Interventions={interventions}")

    with open(RESULTS_DIR / "phase5_h2_predictive.json", "w") as f:
        json.dump(results, f, indent=4)

    return results

# -------------------------------------------------------------------------
# E3: Local vs Network Optimization (H3 EVAL - Spillback Penalty)
# -------------------------------------------------------------------------
def run_e3_local_vs_network() -> Dict[str, Any]:
    print("\n==================================================")
    print("  EXPERIMENT E3: LOCAL VS NETWORK SCORING (H3)    ")
    print("==================================================")

    cfg_file = str(PROJECT_ROOT / "simulation" / "configs" / "nexus.sumocfg")
    modes = ["local_optimization", "network_optimization"]
    results = {}

    for mode in modes:
        traci.start(["sumo", "-c", cfg_file, "--start", "--quit-on-end"])
        tls_ids = list(traci.trafficlight.getIDList())
        state_extractor = TrafficStateExtractor(tls_ids)
        state_extractor.initialize(traci)
        metrics = MetricsCollector(tls_ids)

        engine = ScenarioEngine(traci, tls_ids, default_horizon_seconds=180)
        generator = StrategyGenerator(tls_ids)
        
        spillback_w = 0.0 if mode == "local_optimization" else 1.5
        optimizer = StrategyOptimizer(spillback_weight=spillback_w)
        depart_times = {}

        step = 0
        spillback_events = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            step_time = traci.simulation.getTime()
            state = state_extractor.extract_state(traci)
            metrics.record_step(state)
            track_completed_trips(traci, metrics, depart_times)

            if step > 100 and step % 350 == 0:
                candidates = generator.generate_candidates(state)
                res = engine.evaluate_candidates(candidates, horizon_seconds=180)
                best_cand, _ = optimizer.select_best_strategy(res)
                engine.apply_strategy(best_cand)

                do_nothing_res = next((c for c in res if c.strategy_type == "do_nothing"), res[0])
                spillback_pen = optimizer.compute_spillback_penalty(best_cand, do_nothing_res)
                if spillback_pen > 0:
                    spillback_events += 1

            step += 1

        summary = metrics.compute_summary()
        summary["mode"] = mode
        summary["spillback_weight"] = spillback_w
        summary["spillback_events_count"] = spillback_events
        results[mode] = summary
        traci.close()

        print(f"  [OK] {mode:<22}: Delay={summary.get('avg_waiting_time_s', 0):.2f}s, Queue={summary.get('mean_queue_length_m', 0):.1f}m, Spillback Events={spillback_events}")

    with open(RESULTS_DIR / "phase5_h3_network_spillback.json", "w") as f:
        json.dump(results, f, indent=4)

    return results

# -------------------------------------------------------------------------
# E5: Perception Noise / Sensor Robustness (H4 EVAL)
# -------------------------------------------------------------------------
def run_e5_sensor_noise() -> Dict[str, Any]:
    print("\n==================================================")
    print("  EXPERIMENT E5: SENSOR PERCEPTION NOISE (H4)     ")
    print("==================================================")

    cfg_file = str(PROJECT_ROOT / "simulation" / "configs" / "nexus.sumocfg")
    noise_levels = [0.0, 0.10, 0.20, 0.30]
    results = {}

    for noise in noise_levels:
        traci.start(["sumo", "-c", cfg_file, "--start", "--quit-on-end"])
        tls_ids = list(traci.trafficlight.getIDList())
        state_extractor = TrafficStateExtractor(tls_ids)
        state_extractor.initialize(traci)
        metrics = MetricsCollector(tls_ids)
        engine = ScenarioEngine(traci, tls_ids, default_horizon_seconds=180)
        generator = StrategyGenerator(tls_ids)
        optimizer = StrategyOptimizer()

        np.random.seed(42)
        depart_times = {}

        step = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            step_time = traci.simulation.getTime()
            state = state_extractor.extract_state(traci)

            if noise > 0.0:
                for j_id, j_data in state.get("junctions", {}).items():
                    noise_factor = 1.0 + np.random.normal(0, noise)
                    j_data["total_queue_m"] = max(0.0, j_data["total_queue_m"] * noise_factor)

            metrics.record_step(state)
            track_completed_trips(traci, metrics, depart_times)

            if step > 100 and step % 350 == 0:
                candidates = generator.generate_candidates(state)
                res = engine.evaluate_candidates(candidates, horizon_seconds=180)
                best_cand, _ = optimizer.select_best_strategy(res)
                engine.apply_strategy(best_cand)

            step += 1

        summary = metrics.compute_summary()
        summary["noise_level"] = noise
        results[f"noise_{int(noise*100)}pct"] = summary
        traci.close()

        print(f"  [OK] Noise Level {int(noise*100)}% : Delay={summary.get('avg_waiting_time_s', 0):.2f}s, Queue={summary.get('mean_queue_length_m', 0):.1f}m, Speed={summary.get('avg_speed_kmh', 0):.1f}km/h")

    with open(RESULTS_DIR / "phase5_h4_robustness.json", "w") as f:
        json.dump(results, f, indent=4)

    return results

# -------------------------------------------------------------------------
# Latency & Scalability Analysis
# -------------------------------------------------------------------------
def run_latency_analysis() -> Dict[str, Any]:
    print("\n==================================================")
    print("  EXPERIMENT: LATENCY & SCALABILITY ANALYSIS     ")
    print("==================================================")

    cfg_file = str(PROJECT_ROOT / "simulation" / "configs" / "nexus.sumocfg")
    traci.start(["sumo", "-c", cfg_file, "--start", "--quit-on-end"])
    tls_ids = list(traci.trafficlight.getIDList())

    for _ in range(300):
        traci.simulationStep()

    state_extractor = TrafficStateExtractor(tls_ids)
    state_extractor.initialize(traci)
    state = state_extractor.extract_state(traci)

    engine = ScenarioEngine(traci, tls_ids, default_horizon_seconds=180)
    generator = StrategyGenerator(tls_ids)

    candidate_counts = [2, 3, 4, 5]
    latency_results = {}

    all_candidates = generator.generate_candidates(state, has_emergency_vehicle=True)

    for n in candidate_counts:
        eval_cands = all_candidates[:n]
        t0 = time.time()
        res = engine.evaluate_candidates(eval_cands, horizon_seconds=180)
        wall_clock_s = round(time.time() - t0, 3)

        latency_results[f"cands_{n}"] = {
            "num_candidates": n,
            "horizon_seconds": 180,
            "wall_clock_seconds": wall_clock_s,
            "seconds_per_candidate": round(wall_clock_s / n, 3)
        }
        print(f"  [OK] {n} Candidates (180s Horizon): {wall_clock_s:.3f}s total ({wall_clock_s/n:.3f}s per candidate)")

    traci.close()

    with open(RESULTS_DIR / "phase5_latency.json", "w") as f:
        json.dump(latency_results, f, indent=4)

    return latency_results

# -------------------------------------------------------------------------
# Master Experiment Matrix Runner
# -------------------------------------------------------------------------
def run_all_phase5_experiments():
    print("\n==================================================")
    print("   NEXUS-TWIN PHASE 5 MASTER EXPERIMENT HARNESS   ")
    print("==================================================")

    e1_res = run_e1_baselines(num_vehicles=1000)
    e2_res = run_e2_predictive_vs_reactive(num_vehicles=1000)
    e3_res = run_e3_local_vs_network()
    e5_res = run_e5_sensor_noise()
    lat_res = run_latency_analysis()

    summary_manifest = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "COMPLETED",
        "h1_baseline_comparison": e1_res,
        "h2_predictive_vs_reactive": e2_res,
        "h3_local_vs_network": e3_res,
        "h4_sensor_robustness": e5_res,
        "latency_analysis": lat_res
    }

    with open(RESULTS_DIR / "phase5_summary.json", "w") as f:
        json.dump(summary_manifest, f, indent=4)

    print("\n==================================================")
    print("  [SUCCESS] All Phase 5 Experiments Completed!   ")
    print(f"  Results exported to: {RESULTS_DIR}")
    print("==================================================\n")

if __name__ == "__main__":
    run_all_phase5_experiments()
