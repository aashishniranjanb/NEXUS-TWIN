"""
Automatic Figure Generator Script for NEXUS-TWIN Phase 5.
Reads empirical experiment JSON output files from results/ and generates publication-grade
matplotlib figures saved to results/figures/ per Phase 5 requirements.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

# Set clean professional plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.labelsize'] = 11

def generate_fig1_baselines():
    h1_file = RESULTS_DIR / "phase5_h1_baselines.json"
    if not h1_file.exists():
        print(f"[Warning] {h1_file} not found. Skipping Fig 1.")
        return

    with open(h1_file, "r") as f:
        data = json.load(f)

    methods = ["Fixed Time", "Reactive Adaptive", "NexusTwin"]
    keys = ["fixed", "reactive", "nexustwin"]

    delays = [data[k]["avg_waiting_time_s"] for k in keys]
    queues = [data[k]["mean_queue_length_m"] for k in keys]
    speeds = [data[k]["avg_speed_kmh"] for k in keys]

    x = np.arange(len(methods))
    width = 0.25

    fig, ax1 = plt.subplots(figsize=(9, 5))

    rects1 = ax1.bar(x - width, delays, width, label='Avg Waiting Time (s)', color='#e74c3c')
    rects2 = ax1.bar(x, queues, width, label='Mean Queue Length (m)', color='#3498db')

    ax2 = ax1.twinx()
    rects3 = ax2.bar(x + width, speeds, width, label='Avg Speed (km/h)', color='#2ecc71', alpha=0.85)

    ax1.set_ylabel('Time (s) / Queue (m)')
    ax2.set_ylabel('Speed (km/h)')
    ax1.set_title('Figure 1: Baseline Method Performance Comparison (H1 Evaluation)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods)
    
    # Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig1_baseline_comparison.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [OK] Saved Figure 1: {out_path}")

def generate_fig2_predictive():
    h2_file = RESULTS_DIR / "phase5_h2_predictive.json"
    if not h2_file.exists():
        return

    with open(h2_file, "r") as f:
        data = json.load(f)

    modes = ["Reactive Scenario Engine", "Predictive Digital Twin"]
    keys = ["reactive_only", "predictive_twin"]

    delays = [data[k]["avg_waiting_time_s"] for k in keys]
    queues = [data[k]["mean_queue_length_m"] for k in keys]
    interventions = [data[k]["interventions_count"] for k in keys]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    x = np.arange(len(modes))
    ax1.bar(x - 0.2, delays, 0.4, label='Avg Waiting Time (s)', color='#9b59b6')
    ax1.bar(x + 0.2, queues, 0.4, label='Mean Queue Length (m)', color='#1abc9c')
    ax1.set_xticks(x)
    ax1.set_xticklabels(["Reactive", "Predictive"])
    ax1.set_ylabel('Metric Value')
    ax1.set_title('Delay & Queue Comparison')
    ax1.legend()

    ax2.bar(modes, interventions, color='#f39c12', width=0.4)
    ax2.set_ylabel('Proactive Interventions Triggered')
    ax2.set_title('Trigger Frequency Comparison (H2)')

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig2_predictive_vs_reactive.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [OK] Saved Figure 2: {out_path}")

def generate_fig3_spillback():
    h3_file = RESULTS_DIR / "phase5_h3_network_spillback.json"
    if not h3_file.exists():
        return

    with open(h3_file, "r") as f:
        data = json.load(f)

    modes = ["Local (Weight = 0.0)", "Network (Weight = 1.5)"]
    keys = ["local_optimization", "network_optimization"]

    spillbacks = [data[k]["spillback_events_count"] for k in keys]
    delays = [data[k]["avg_waiting_time_s"] for k in keys]

    fig, ax1 = plt.subplots(figsize=(7, 4.5))

    ax1.bar(modes, spillbacks, color='#e67e22', width=0.4, label='Spillback Penalty Events')
    ax1.set_ylabel('Spillback Penalty Count', color='#e67e22')
    ax1.set_title('Figure 3: Local vs Network-Level Optimization (H3 Evaluation)')

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig3_spillback_ablation.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [OK] Saved Figure 3: {out_path}")

def generate_fig4_latency():
    lat_file = RESULTS_DIR / "phase5_latency.json"
    if not lat_file.exists():
        return

    with open(lat_file, "r") as f:
        data = json.load(f)

    counts = [v["num_candidates"] for v in data.values()]
    times = [v["wall_clock_seconds"] for v in data.values()]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(counts, times, marker='o', linewidth=2.5, markersize=8, color='#2980b9')
    ax.set_xlabel('Candidate Strategies Evaluated (180s Horizon)')
    ax.set_ylabel('Wall-Clock Simulation Latency (seconds)')
    ax.set_title('Figure 4: Engine Scalability & Wall-Clock Latency Analysis')
    ax.set_xticks(counts)

    for c, t in zip(counts, times):
        ax.annotate(f"{t:.2f}s", (c, t), textcoords="offset points", xytext=(0,10), ha='center')

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig4_latency_analysis.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [OK] Saved Figure 4: {out_path}")

def generate_all_figures():
    print("\n==================================================")
    print("      GENERATING PHASE 5 PUBLICATION FIGURES      ")
    print("==================================================")
    generate_fig1_baselines()
    generate_fig2_predictive()
    generate_fig3_spillback()
    generate_fig4_latency()
    print("==================================================\n")

if __name__ == "__main__":
    generate_all_figures()
