"""
Predictive Digital Twin Execution & Benchmark Pipeline for NEXUS-TWIN.
Demonstrates proactive decision-making driven by XGBoost 5-minute congestion forecasts vs reactive control.
Outputs results/predictive_vs_reactive.json per Phase 4 specifications.
"""

import os
import sys
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from experiments.run_baselines import setup_sumo_env, build_network_and_routes
setup_sumo_env()

import traci
from simulation.bridge.traffic_state import TrafficStateExtractor
from intelligence.feature_engineering.feature_engineering import FeatureExtractor
from intelligence.prediction.congestion_predictor import CongestionPredictor
from intelligence.strategy.strategy_generator import StrategyGenerator
from simulation.bridge.scenario_engine import ScenarioEngine
from intelligence.strategy.strategy_optimizer import StrategyOptimizer
from intelligence.explainability.explainable_ai import ExplainableAIEngine

def run_predictive_simulation(gui: bool = False, horizon: int = 180):
    build_network_and_routes()

    cfg_file = str(PROJECT_ROOT / "simulation" / "configs" / "nexus.sumocfg")
    sumo_cmd = ["sumo-gui" if gui else "sumo", "-c", cfg_file, "--start", "--quit-on-end"]

    print("\n==================================================")
    print("   STARTING PREDICTIVE DIGITAL TWIN SIMULATION    ")
    print("==================================================")

    traci.start(sumo_cmd)
    
    tls_ids = list(traci.trafficlight.getIDList())
    state_extractor = TrafficStateExtractor(tls_ids)
    state_extractor.initialize(traci)

    fe = FeatureExtractor(lag_steps=5)
    predictor = CongestionPredictor()
    # Train predictor if model file doesn't exist
    if not predictor.model_path.exists():
        print("[Predictor] Training XGBoost congestion model...")
        predictor.train()

    generator = StrategyGenerator(tls_ids)
    optimizer = StrategyOptimizer()
    explain_engine = ExplainableAIEngine()

    proactive_interventions_count = 0
    decision_log = []

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step_time = traci.simulation.getTime()

        # 1. Extract live state & push to feature extractor
        state = state_extractor.extract_state(traci)
        fe.push_state(state)

        # 2. Check predictions every 180 seconds (3 mins) once buffer is filled
        if step > 30 and step % 180 == 0:
            prediction_map = {}
            high_risk = False

            for j_id in tls_ids:
                feats = fe.extract_features_at_step(len(fe.history) - 1, j_id)
                if feats:
                    pred = predictor.predict_congestion(feats)
                    prediction_map[j_id] = pred
                    if pred.congestion_probability >= 0.65 or pred.will_congest_5min:
                        high_risk = True

            # 3. Proactive Decision Trigger
            if high_risk:
                print(f"\n[Proactive Trigger t={step_time:.0f}s] High 5-minute congestion probability detected by XGBoost!")
                engine = ScenarioEngine(traci, tls_ids, default_horizon_seconds=horizon)
                
                has_emergency = "veh_emergency" in traci.vehicle.getIDList()
                candidates = generator.generate_candidates(state, prediction_map=prediction_map, has_emergency_vehicle=has_emergency)
                
                results = engine.evaluate_candidates(candidates, horizon_seconds=horizon)
                best_cand, best_score = optimizer.select_best_strategy(results)
                explanation = explain_engine.explain(best_cand, results, prediction_map)

                # Apply selected optimal strategy to reference simulation
                engine.apply_strategy(best_cand)
                proactive_interventions_count += 1

                print(f"  [Recommendation] {explanation.action}")
                print(f"  [Impact]         {explanation.expected_impact} (Confidence: {explanation.confidence})")

                decision_log.append({
                    "step": step_time,
                    "action": explanation.action,
                    "selected_strategy": best_cand.strategy_id,
                    "score": best_score,
                    "confidence": explanation.confidence
                })

        step += 1

    traci.close()

    res_dir = PROJECT_ROOT / "results"
    res_dir.mkdir(exist_ok=True)
    out_file = res_dir / "predictive_vs_reactive.json"

    result_summary = {
        "mode": "Predictive Digital Twin",
        "total_proactive_interventions": proactive_interventions_count,
        "decision_log": decision_log
    }

    with open(out_file, "w") as f:
        json.dump(result_summary, f, indent=4)

    print(f"\n[Finished] Predictive Digital Twin Execution Complete! Total Proactive Interventions: {proactive_interventions_count}")
    print(f"Saved execution log to {out_file}\n")
    return result_summary

if __name__ == "__main__":
    run_predictive_simulation()
