"""
Training Data Generator Script for NEXUS-TWIN Congestion Predictor.
Runs multi-scenario SUMO traffic simulations to extract labeled feature dataset across 3 independent runs.
Outputs data/traffic_features.csv per 32_TRAFFIC_FEATURE_ENGINEERING.md specs.
"""

import os
import sys
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from experiments.run_baselines import setup_sumo_env, build_network_and_routes
setup_sumo_env()

import traci
from simulation.routes.generate_routes import generate_route_file
from src.traffic_state import TrafficStateExtractor
from src.feature_engineering import FeatureExtractor

def generate_dataset_from_runs(num_runs: int = 3, run_duration: int = 1500):
    build_network_and_routes()

    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    out_csv = data_dir / "traffic_features.csv"

    all_dfs = []

    for run_i in range(num_runs):
        print(f"\n[DataGen] Running simulation dataset run [{run_i + 1}/{num_runs}]...")
        # Vary vehicle density & seed per run to ensure independent runs
        num_vehs = 700 + (run_i * 300)
        rou_file = PROJECT_ROOT / "simulation" / "routes" / "nexus.rou.xml"
        generate_route_file(filepath=str(rou_file), num_vehicles=num_vehs, duration=run_duration)

        cfg_file = str(PROJECT_ROOT / "simulation" / "configs" / "nexus.sumocfg")
        sumo_cmd = ["sumo", "-c", cfg_file, "--start", "--quit-on-end", "--seed", str(42 + run_i * 100)]

        traci.start(sumo_cmd)
        tls_ids = list(traci.trafficlight.getIDList())
        state_extractor = TrafficStateExtractor(tls_ids)
        state_extractor.initialize(traci)

        fe = FeatureExtractor(lag_steps=5)

        step = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            state = state_extractor.extract_state(traci)
            fe.push_state(state)
            step += 1

        traci.close()

        run_df = fe.build_dataset_from_history(horizon_steps=300)  # 5-min horizon
        if not run_df.empty:
            run_df["run_id"] = run_i
            all_dfs.append(run_df)
            print(f"  [OK] Extracted {len(run_df)} feature samples from Run {run_i + 1}")

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_csv(out_csv, index=False)
        print(f"\n[DataGen] Successfully generated {len(final_df)} training samples across {num_runs} independent runs!")
        print(f"Saved to: {out_csv}")
        return final_df
    else:
        print("[DataGen] Error: No features extracted.")
        return pd.DataFrame()

if __name__ == "__main__":
    generate_dataset_from_runs(num_runs=3, run_duration=1500)
