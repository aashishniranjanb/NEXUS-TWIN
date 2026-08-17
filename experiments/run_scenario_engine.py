"""
CLI Demonstration & Execution Script for Digital Twin Scenario Engine.
Evaluates candidate traffic strategies in parallel futures, scores network outcomes,
selects the optimal intervention, and generates grounded explanations per Phase 3 Milestone 2 specs.
"""

import os
import sys
import time
import json
import csv
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from experiments.run_baselines import setup_sumo_env, build_network_and_routes
setup_sumo_env()

import traci
from src.traffic_state import TrafficStateExtractor
from src.strategy_generator import StrategyGenerator
from src.scenario_engine import ScenarioEngine
from src.strategy_optimizer import StrategyOptimizer
from src.explainable_ai import ExplainableAIEngine

def main():
    parser = argparse.ArgumentParser(description="NexusTwin Digital Twin Scenario Engine")
    parser.add_argument("--gui", action="store_true", help="Run SUMO with GUI")
    parser.add_argument("--horizon", type=int, default=180, help="Scenario simulation horizon in seconds (default: 180)")
    parser.add_argument("--warmup", type=int, default=300, help="Simulation steps before decision point (default: 300)")
    args = parser.parse_args()

    build_network_and_routes()

    cfg_file = str(PROJECT_ROOT / "simulation" / "configs" / "nexus.sumocfg")
    sumo_cmd = ["sumo-gui" if args.gui else "sumo", "-c", cfg_file, "--start", "--quit-on-end"]

    print("\n==================================================")
    print("   NEXUS-TWIN DIGITAL TWIN SCENARIO EVALUATION   ")
    print("==================================================")

    traci.start(sumo_cmd)
    
    tls_ids = list(traci.trafficlight.getIDList())
    extractor = TrafficStateExtractor(tls_ids)
    extractor.initialize(traci)

    # 1. Warmup simulation up to decision point (e.g. t=300s)
    print(f"\n[1/5] Simulating reference traffic to decision point (t={args.warmup}s)...")
    for _ in range(args.warmup):
        traci.simulationStep()

    # 2. Extract current synchronized state
    current_state = extractor.extract_state(traci)
    has_emergency = "veh_emergency" in traci.vehicle.getIDList()

    print("\n--------------------------------------------------")
    print("CURRENT SYNCHRONIZED TWIN STATE (t=300s)")
    print("--------------------------------------------------")
    print(f"Active Vehicles: {current_state['active_vehicles']}")
    print(f"Average Speed:   {current_state['avg_speed_kmh']} km/h")
    print(f"Average Waiting: {current_state['avg_waiting_time_s']} s")
    print(f"Emergency Veh:   {'ACTIVE' if has_emergency else 'NONE'}")
    for j_id, j_data in current_state["junctions"].items():
        print(f"  Junction {j_id}: Queue = {j_data['total_queue_m']} m ({j_data['total_halting']} vehicles)")

    # 3. Generate candidate strategies
    generator = StrategyGenerator(tls_ids)
    candidates = generator.generate_candidates(current_state, has_emergency_vehicle=has_emergency)

    print(f"\n[2/5] Generated {len(candidates)} Candidate Strategies for Evaluation:")
    for i, cand in enumerate(candidates, 1):
        print(f"  Candidate [{i}]: {cand.strategy_id:<25} ({cand.strategy_type}) -> {cand.description}")

    # 4. Scenario Engine Evaluation
    engine = ScenarioEngine(traci, tls_ids, default_horizon_seconds=args.horizon)
    
    print(f"\n[3/5] Simulating {len(candidates)} Parallel Futures (Horizon: {args.horizon}s)...")
    
    t_start = time.time()
    results = engine.evaluate_candidates(candidates, horizon_seconds=args.horizon)
    t_end = time.time()
    total_eval_time = round(t_end - t_start, 3)

    print(f"  [OK] All candidate futures simulated and state restored in {total_eval_time}s wall-clock time!")

    # 5. Optimize & Select Best Strategy
    optimizer = StrategyOptimizer()
    best_candidate, best_score = optimizer.select_best_strategy(results)

    # 6. Generate Grounded Explanation
    explain_engine = ExplainableAIEngine()
    explanation = explain_engine.explain(best_candidate, results)

    # Display Results Table
    print("\n--------------------------------------------------------------------------------------")
    print("                       SCENARIO FUTURE EVALUATION RESULTS                             ")
    print("--------------------------------------------------------------------------------------")
    print(f"{'Strategy ID':<25} | {'Delay (s)':<10} | {'Queue (m)':<10} | {'Speed (km/h)':<12} | {'Score':<8}")
    print("-" * 86)
    for r in results:
        is_best = " (SELECTED)" if r.strategy_id == best_candidate.strategy_id else ""
        print(f"{r.strategy_id:<25} | {r.predicted_delay_s:<10} | {r.predicted_queue_m:<10} | {r.network_metrics.get('avg_speed_kmh', 0.0):<12} | {r.score:<8}{is_best}")
    print("--------------------------------------------------------------------------------------")

    print("\n==================================================")
    print("             NEXUS-TWIN RECOMMENDATION            ")
    print("==================================================")
    print(f"ACTION:          {explanation.action}")
    print(f"REASON:          {explanation.reason}")
    print(f"EXPECTED IMPACT: {explanation.expected_impact}")
    print(f"CONFIDENCE:      {explanation.confidence}")
    print("==================================================\n")

    # 7. Save Machine-Readable Output Files
    res_dir = PROJECT_ROOT / "results"
    res_dir.mkdir(exist_ok=True)

    json_results_file = res_dir / "scenario_results.json"
    csv_results_file = res_dir / "scenario_results.csv"
    summary_file = res_dir / "scenario_summary.json"
    perf_file = res_dir / "scenario_performance.json"

    # Export scenario_results.json
    with open(json_results_file, "w") as f:
        json.dump([r.to_dict() for r in results], f, indent=4)

    # Export scenario_results.csv
    fieldnames = ["strategy_id", "strategy_type", "predicted_delay_s", "predicted_queue_m", "predicted_throughput", "predicted_emissions_kg", "predicted_emergency_delay_s", "score", "success"]
    with open(csv_results_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "strategy_id": r.strategy_id,
                "strategy_type": r.strategy_type,
                "predicted_delay_s": r.predicted_delay_s,
                "predicted_queue_m": r.predicted_queue_m,
                "predicted_throughput": r.predicted_throughput,
                "predicted_emissions_kg": r.predicted_emissions,
                "predicted_emergency_delay_s": r.predicted_emergency_delay_s,
                "score": r.score,
                "success": r.success
            })

    # Export scenario_summary.json
    summary_data = {
        "decision_point_step": args.warmup,
        "selected_strategy": best_candidate.strategy_id,
        "selected_score": best_score,
        "explanation": explanation.to_dict(),
        "candidates_evaluated": len(results)
    }
    with open(summary_file, "w") as f:
        json.dump(summary_data, f, indent=4)

    # Export scenario_performance.json
    perf_data = {
        "candidate_count": len(results),
        "horizon_seconds": args.horizon,
        "total_wall_clock_seconds": total_eval_time,
        "avg_seconds_per_candidate": round(total_eval_time / len(results), 3)
    }
    with open(perf_file, "w") as f:
        json.dump(perf_data, f, indent=4)

    print(f"[Saved] Scenario evaluation outputs saved to:")
    print(f"  - {json_results_file}")
    print(f"  - {csv_results_file}")
    print(f"  - {summary_file}")
    print(f"  - {perf_file}\n")

    traci.close()

if __name__ == "__main__":
    main()
