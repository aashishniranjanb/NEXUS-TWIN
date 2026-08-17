# 21 — Simulation Setup

## Purpose
Concrete, repeatable steps to get SUMO + Python + TraCI running, so any team member (or a judge reproducing the build) can go from a clean machine to a running simulation. This is the practical companion to `19_SIMULATION_ARCHITECTURE.md`.

## Prerequisites

| Requirement | Notes |
|---|---|
| SUMO (Simulation of Urban MObility) | Install separately from the OS package manager or official installer — not a pip package |
| Python 3.10+ | For TraCI client, FastAPI backend, ML libraries |
| `SUMO_HOME` environment variable | Must be set for TraCI's Python bindings to be importable |
| pip packages | `traci` (bundled with SUMO's `tools/`), `fastapi`, `uvicorn`, `pandas`, `numpy`, `scikit-learn`, `xgboost`, `ultralytics` (YOLO), `paho-mqtt`, `streamlit`, `plotly` |

## Installation Steps (Reference)

```bash
# 1. Install SUMO (Ubuntu example)
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools sumo-doc

# 2. Set SUMO_HOME (add to shell profile)
export SUMO_HOME=/usr/share/sumo

# 3. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install Python dependencies
pip install fastapi uvicorn pandas numpy scikit-learn xgboost \
            ultralytics paho-mqtt streamlit plotly
```

macOS/Windows installers are available from the official SUMO downloads page — the team should pre-install on all laptops **before** the event to avoid depending on venue network access (per `11_TECH_STACK.md` dependency notes).

## Verifying the Install

```bash
sumo --version
sumo-gui   # should open the SUMO GUI window
python3 -c "import traci; print('traci OK')"
```

## Project Commands (once scaffolded)

```bash
# Run the reference SUMO simulation headless
sumo -c simulation/network/nexustwin.sumocfg

# Run with GUI for visual debugging
sumo-gui -c simulation/network/nexustwin.sumocfg

# Run the FastAPI backend (wraps TraCI control loop)
uvicorn src.main:app --reload --port 8000

# Run the dashboard
streamlit run dashboard/app.py
```

## Directory Expectations (created in this phase)

```text
simulation/
├── network/       # .net.xml, .sumocfg
├── routes/        # demand / .rou.xml
├── signals/       # traffic light program definitions
└── scenarios/     # scenario-specific configs (rush hour, accident, etc.)
```

## Pre-Event Checklist
- [ ] SUMO installed and verified on every team laptop.
- [ ] `SUMO_HOME` set and persisted (not just for the current shell session).
- [ ] Python virtual environment created and dependencies installed offline-cached where possible.
- [ ] YOLO model weights pre-downloaded (see `31_COMPUTER_VISION.md`).
- [ ] A minimal `.sumocfg` + `.net.xml` smoke-tested to confirm the toolchain works end-to-end before Round 2 begins.

This checklist feeds into `60_FINAL_CHECKLIST.md`.
