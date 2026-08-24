# NEXUS-TWIN Architecture Specification

This document details the canonical architecture for the NEXUS-TWIN project, transitioning from a research-driven structure to a robust, scalable game and digital twin foundation.

## 1. High-Level Architecture
NEXUS-TWIN operates as a real-time, interactive, playable traffic decision game built atop an authoritative SUMO digital twin and AI-driven predictive intelligence. 

The system is organized into the following primary components:
- **Game Client (Unity)**: The interactive 3D visualization and player input layer.
- **Backend Services**: FastAPI-based micro-services handling game state, leaderboards, and orchestrating requests.
- **Intelligence Engine**: ML models (XGBoost) and optimization algorithms that predict congestion and generate counterfactual strategies.
- **Simulation Bridge**: The bridge connecting the abstract AI/Backend logic to the physical SUMO TraCI environment.

## 2. Directory Structure
```
NEXUS-TWIN/
├── game/
│   └── unity/                 # Unity 3D project for the game client
├── backend/
│   ├── api/                   # FastAPI routing layer (e.g. decision_server.py)
│   ├── game_server/           # Game session, scoring, badges (e.g. game_engine.py)
│   ├── agents/                # LangGraph/Multi-Agent orchestration logic
│   ├── orchestration/         # Workflow orchestration
│   └── schemas/               # Pydantic schemas and shared models (e.g. scenario_models.py)
├── simulation/
│   ├── bridge/                # SUMO/TraCI interaction (traffic_state.py, metrics_collector.py)
│   ├── network/               # SUMO .net.xml and .edg.xml files
│   ├── routes/                # SUMO .rou.xml files
│   ├── signals/               # Traffic light logic
│   ├── scenarios/             # predefined scenarios
│   └── configs/               # .sumocfg configurations
├── intelligence/
│   ├── prediction/            # XGBoost Congestion Predictor (congestion_predictor.py)
│   ├── strategy/              # Counterfactual generation & optimization
│   ├── explainability/        # XAI (explainable_ai.py)
│   ├── feature_engineering/   # Data pipeline tools
│   └── safety/                # Guardrails for candidate strategies
├── perception/
│   ├── traffic/               # YOLO/CV pipelines for traffic detection
│   └── vision/                # General computer vision utilities
├── hardware/
│   ├── esp32/                 # Microcontroller code for physical traffic lights
│   ├── mqtt/                  # MQTT broker configs
│   └── prototypes/            # Hardware specs and CAD
├── docs/                      # Canonical documentation
│   ├── game/                  # Main product documentation (PRD, TECH_STACK, DESIGN_GUIDELINES)
│   └── legacy/                # Archived phase-* docs and old web UI
├── experiments/               # Scripts for running baselines and generating data
├── tests/                     # Pytest suite
├── data/                      # Model weights, datasets, generated features
└── assets/                    # Media and diagrams
```

## 3. Data Flow
1. **State Extraction**: `simulation/bridge/traffic_state.py` polls TraCI for the live state.
2. **Prediction & Strategy**: `intelligence/prediction/` assesses the state, and `intelligence/strategy/` formulates counterfactual solutions.
3. **API & Game Engine**: `backend/api/decision_server.py` exposes these options to the client, while `backend/game_server/game_engine.py` manages the score and badges.
4. **Client Visualization**: `game/unity/` renders the state and accepts player decisions.

## 4. Current Status
- The Python backend, ML predictors, and Simulation Bridge are fully operational.
- The repository has been reorganized to isolate these components cleanly from the future Unity client.
- Tests verify that internal imports and cross-component routing are stable.
