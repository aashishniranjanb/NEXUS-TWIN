# NEXUS-TWIN: AI-Powered Digital Twin for Urban Traffic Optimization

NEXUS-TWIN is a digital twin architecture for real-time traffic signal optimization and scenario simulation powered by SUMO and TraCI.

## Project Structure

```
NEXUS-TWIN/
├── docs/                 # Documentation and architecture specs
├── simulation/           # SUMO simulation files & signal controllers
│   ├── network/          # Network XML definitions (nexus.net.xml, etc.)
│   ├── routes/           # Vehicle demand & route definitions (nexus.rou.xml)
│   ├── signals/          # Fixed-time & Reactive adaptive traffic signal controllers
│   ├── scenarios/        # Scenario simulation configs (future interventions)
│   └── configs/          # SUMO config files (nexus.sumocfg)
├── src/                  # Core Digital Twin engine modules
│   ├── traffic_state.py  # Real-time TraCI state extractor
│   └── metrics.py        # Delay, queue length, waiting time, throughput logger
├── perception/           # Edge-AI / YOLO traffic detection pipelines
├── prediction/           # Traffic forecasting models (e.g., XGBoost)
├── optimization/         # Scenario simulation & strategy scoring engine
├── dashboard/            # Analytical visual interface
├── game/                 # Interactive simulation UI
├── experiments/          # Baseline comparison and benchmarking scripts
├── data/                 # Raw & processed traffic data
├── results/              # Simulation output metrics & baseline reports
└── assets/               # Visual assets and posters
```

## Quick Start: Running Baselines

```bash
# Run baseline comparison (Fixed-time vs. Reactive adaptive signal control)
python experiments/run_baselines.py
```
