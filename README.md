# NEXUS-TWIN: AI-Powered Digital Twin for Urban Traffic Optimization

NEXUS-TWIN is a digital twin architecture for real-time traffic signal optimization and scenario simulation powered by SUMO and TraCI.

## Project Structure

```
NEXUS-TWIN/
├── game/                 # Unity 3D project for the game client
├── backend/              # FastAPI routing layer and game server logic
├── simulation/           # SUMO simulation files & bridge logic
├── intelligence/         # Prediction, strategy, and explainability engines
├── perception/           # Edge-AI / YOLO traffic detection pipelines
├── hardware/             # Physical device integrations (ESP32)
├── experiments/          # Baseline comparison and benchmarking scripts
├── tests/                # Automated testing suite
├── docs/                 # Documentation (PRD, Guidelines, Architecture)
├── data/                 # Raw & processed traffic data
├── results/              # Simulation output metrics & baseline reports
└── assets/               # Visual assets and posters
```

## Quick Start: Running Baselines

```bash
# Run baseline comparison (Fixed-time vs. Reactive adaptive signal control)
python experiments/run_baselines.py
```
