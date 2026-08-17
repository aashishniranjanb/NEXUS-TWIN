"""
Experiments Pipeline: Run and compare Baseline 1 (Fixed-time) vs Baseline 2 (Reactive Adaptive).
NEXUS-TWIN Phase 3 Initial MVP Evaluation Script.
"""

import os
import sys
import json
import csv
import subprocess
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Ensure SUMO_HOME and PATH are set for Windows eclipse-sumo installation
def setup_sumo_env():
    if "SUMO_HOME" not in os.environ:
        possible_sumo_home = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "Python" / "Python314" / "site-packages" / "sumo"
        if possible_sumo_home.exists():
            os.environ["SUMO_HOME"] = str(possible_sumo_home)
            bin_dir = str(possible_sumo_home / "bin")
            scripts_dir = str(possible_sumo_home.parent.parent / "Scripts")
            os.environ["PATH"] = bin_dir + ";" + scripts_dir + ";" + os.environ.get("PATH", "")

setup_sumo_env()

from simulation.routes.generate_routes import generate_route_file
from src.traffic_state import TrafficStateExtractor
from src.metrics_collector import MetricsCollector
from simulation.signals.fixed_time import FixedTimeController
from simulation.signals.reactive import ReactiveAdaptiveController

def build_network_and_routes():
    """Generates nexus.net.xml via netconvert and nexus.rou.xml via route generator."""
    net_dir = PROJECT_ROOT / "simulation" / "network"
    rou_dir = PROJECT_ROOT / "simulation" / "routes"
    
    rou_file = rou_dir / "nexus.rou.xml"
    if not rou_file.exists():
        print("[Setup] Generating 1000 vehicles demand (nexus.rou.xml)...")
        generate_route_file(filepath=str(rou_file), num_vehicles=1000, duration=1800)

    # Netconvert check
    net_file = net_dir / "nexus.net.xml"
    netccfg_file = net_dir / "nexus.netccfg"
    
    if not net_file.exists():
        print("[Setup] Building SUMO network (nexus.net.xml) via netconvert...")
        cmd = ["netconvert", "-c", str(netccfg_file), "-o", str(net_file)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[Error] netconvert failed:\n{res.stderr}")
            sys.exit(1)
        print("[Setup] Network compiled successfully!")

def run_simulation(controller_type: str, gui: bool = False):
    import traci
    
    cfg_file = str(PROJECT_ROOT / "simulation" / "configs" / "nexus.sumocfg")
    sumo_cmd = ["sumo-gui" if gui else "sumo", "-c", cfg_file, "--start", "--quit-on-end"]

    print(f"\n==================================================")
    print(f"   Starting Simulation: {controller_type.upper()} BASELINE")
    print(f"==================================================")

    traci.start(sumo_cmd)
    
    tls_ids = list(traci.trafficlight.getIDList())
    state_extractor = TrafficStateExtractor(tls_ids)
    state_extractor.initialize(traci)
    
    metrics = MetricsCollector(controller_type)

    if controller_type == "fixed_time":
        controller = FixedTimeController(tls_ids, green_duration=30, yellow_duration=4)
    elif controller_type == "reactive":
        controller = ReactiveAdaptiveController(tls_ids, min_green=15, max_green=50, yellow_duration=4, queue_threshold=4)
        controller.initialize(traci)
    else:
        raise ValueError(f"Unknown controller type: {controller_type}")

    # Track vehicle depart & arrive times for exact trip durations
    veh_depart_times = {}

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step_time = traci.simulation.getTime()
        
        # Controller step
        controller.step(traci, step_time)

        # Track departed vehicles
        for veh_id in traci.simulation.getDepartedIDList():
            veh_depart_times[veh_id] = step_time

        # Track arrived vehicles
        arrived_ids = traci.simulation.getArrivedIDList()
        for veh_id in arrived_ids:
            if veh_id in veh_depart_times:
                travel_time = step_time - veh_depart_times[veh_id]
                metrics.record_completed_trip(travel_time)

        # Extract snapshot state
        state = state_extractor.extract_state(traci)
        metrics.record_step(state)
        
        step += 1

    traci.close()
    
    summary = metrics.compute_summary()
    print(f"[Finished] {controller_type.upper()} Complete! Throughput: {summary.get('throughput_vehicles')} vehicles | Avg Wait: {summary.get('avg_waiting_time_s')}s | Mean Queue: {summary.get('mean_queue_length_m')}m")
    return summary

def main():
    build_network_and_routes()

    use_gui = "--gui" in sys.argv

    # Run Fixed Baseline
    fixed_results = run_simulation("fixed_time", gui=use_gui)

    # Run Reactive Adaptive Baseline
    reactive_results = run_simulation("reactive", gui=use_gui)

    # Output Directory Setup
    res_dir = PROJECT_ROOT / "results"
    res_dir.mkdir(exist_ok=True)

    json_out = res_dir / "baseline_comparison.json"
    csv_out = res_dir / "baseline_comparison.csv"

    comparison_data = {
        "fixed_baseline": fixed_results,
        "reactive_baseline": reactive_results,
        "improvements": {
            "waiting_time_reduction_pct": round(
                ((fixed_results['avg_waiting_time_s'] - reactive_results['avg_waiting_time_s']) / fixed_results['avg_waiting_time_s']) * 100, 2
            ) if fixed_results['avg_waiting_time_s'] > 0 else 0,
            "queue_reduction_pct": round(
                ((fixed_results['mean_queue_length_m'] - reactive_results['mean_queue_length_m']) / fixed_results['mean_queue_length_m']) * 100, 2
            ) if fixed_results['mean_queue_length_m'] > 0 else 0,
            "speed_increase_pct": round(
                ((reactive_results['avg_speed_kmh'] - fixed_results['avg_speed_kmh']) / fixed_results['avg_speed_kmh']) * 100, 2
            ) if fixed_results['avg_speed_kmh'] > 0 else 0
        }
    }

    with open(json_out, "w") as f:
        json.dump(comparison_data, f, indent=4)

    # Write CSV Summary
    fieldnames = ["metric", "fixed_baseline", "reactive_baseline", "diff_pct"]
    with open(csv_out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerow({
            "metric": "Avg Waiting Time (s)",
            "fixed_baseline": fixed_results["avg_waiting_time_s"],
            "reactive_baseline": reactive_results["avg_waiting_time_s"],
            "diff_pct": f"-{comparison_data['improvements']['waiting_time_reduction_pct']}%"
        })
        writer.writerow({
            "metric": "Avg Travel Time (s)",
            "fixed_baseline": fixed_results["avg_travel_time_s"],
            "reactive_baseline": reactive_results["avg_travel_time_s"],
            "diff_pct": "N/A"
        })
        writer.writerow({
            "metric": "Mean Queue Length (m)",
            "fixed_baseline": fixed_results["mean_queue_length_m"],
            "reactive_baseline": reactive_results["mean_queue_length_m"],
            "diff_pct": f"-{comparison_data['improvements']['queue_reduction_pct']}%"
        })
        writer.writerow({
            "metric": "Avg Speed (km/h)",
            "fixed_baseline": fixed_results["avg_speed_kmh"],
            "reactive_baseline": reactive_results["avg_speed_kmh"],
            "diff_pct": f"+{comparison_data['improvements']['speed_increase_pct']}%"
        })
        writer.writerow({
            "metric": "Vehicle Throughput",
            "fixed_baseline": fixed_results["throughput_vehicles"],
            "reactive_baseline": reactive_results["throughput_vehicles"],
            "diff_pct": "100%"
        })

    print("\n" + "="*70)
    print("                NEXUS-TWIN BASELINE COMPARISON RESULTS             ")
    print("="*70)
    print(f"{'Metric':<30} | {'Fixed Baseline':<16} | {'Reactive Baseline':<18} | {'Improvement':<12}")
    print("-" * 70)
    print(f"{'Avg Waiting Time (s)':<30} | {fixed_results['avg_waiting_time_s']:<16} | {reactive_results['avg_waiting_time_s']:<18} | -{comparison_data['improvements']['waiting_time_reduction_pct']}%")
    print(f"{'Mean Queue Length (m)':<30} | {fixed_results['mean_queue_length_m']:<16} | {reactive_results['mean_queue_length_m']:<18} | -{comparison_data['improvements']['queue_reduction_pct']}%")
    print(f"{'Avg Network Speed (km/h)':<30} | {fixed_results['avg_speed_kmh']:<16} | {reactive_results['avg_speed_kmh']:<18} | +{comparison_data['improvements']['speed_increase_pct']}%")
    print(f"{'Vehicle Throughput':<30} | {fixed_results['throughput_vehicles']:<16} | {reactive_results['throughput_vehicles']:<18} | 100%")
    print("="*70)
    print(f"[Saved] Baseline report written to {json_out} and {csv_out}\n")

if __name__ == "__main__":
    main()
