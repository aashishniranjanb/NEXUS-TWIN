import os
import shutil
import re

directories = [
    "game/unity",
    "backend/api", "backend/game_server", "backend/agents", "backend/orchestration", "backend/schemas",
    "simulation/network", "simulation/routes", "simulation/signals", "simulation/scenarios", "simulation/bridge", "simulation/configs",
    "intelligence/prediction", "intelligence/feature_engineering", "intelligence/strategy", "intelligence/explainability", "intelligence/safety",
    "perception/traffic", "perception/vision",
    "hardware/esp32", "hardware/mqtt", "hardware/prototypes"
]

for d in directories:
    os.makedirs(d, exist_ok=True)

moves = {
    "src/traffic_state.py": "simulation/bridge/traffic_state.py",
    "src/scenario_engine.py": "simulation/bridge/scenario_engine.py",
    "src/scenario_models.py": "backend/schemas/scenario_models.py",
    "src/decision_server.py": "backend/api/decision_server.py",
    "src/game_engine.py": "backend/game_server/game_engine.py",
    "src/metrics_collector.py": "simulation/bridge/metrics_collector.py",
    "src/strategy_generator.py": "intelligence/strategy/strategy_generator.py",
    "src/strategy_optimizer.py": "intelligence/strategy/strategy_optimizer.py",
    "src/explainable_ai.py": "intelligence/explainability/explainable_ai.py",
    "src/feature_engineering.py": "intelligence/feature_engineering/feature_engineering.py",
    "prediction/congestion_predictor.py": "intelligence/prediction/congestion_predictor.py",
    "src/__init__.py": None,
    "prediction/__init__.py": None
}

import_replacements = {
    r"src\.scenario_models": "backend.schemas.scenario_models",
    r"src\.traffic_state": "simulation.bridge.traffic_state",
    r"src\.metrics_collector": "simulation.bridge.metrics_collector",
    r"src\.strategy_optimizer": "intelligence.strategy.strategy_optimizer",
    r"src\.strategy_generator": "intelligence.strategy.strategy_generator",
    r"src\.explainable_ai": "intelligence.explainability.explainable_ai",
    r"src\.game_engine": "backend.game_server.game_engine",
    r"src\.scenario_engine": "simulation.bridge.scenario_engine",
    r"prediction\.congestion_predictor": "intelligence.intelligence.prediction.congestion_predictor",
    r"src\.feature_engineering": "intelligence.feature_engineering.feature_engineering",
}

# Recursively find all python files
py_files = []
for root, _, files in os.walk("."):
    if ".git" in root or "graphify-out" in root or "__pycache__" in root:
        continue
    for f in files:
        if f.endswith(".py"):
            py_files.append(os.path.join(root, f))

# Update imports in all files BEFORE moving (so we don't miss any)
for pf in py_files:
    if not os.path.exists(pf): continue
    with open(pf, "r", encoding="utf-8") as file:
        content = file.read()
    
    new_content = content
    for old, new in import_replacements.items():
        # Match 'from src.module' or 'import src.module'
        new_content = re.sub(old, new, new_content)
    
    if new_content != content:
        with open(pf, "w", encoding="utf-8") as file:
            file.write(new_content)

# Move the files
for src_f, dst_f in moves.items():
    if os.path.exists(src_f):
        if dst_f is not None:
            shutil.move(src_f, dst_f)
            print(f"Moved {src_f} to {dst_f}")
        else:
            os.remove(src_f)
            print(f"Removed {src_f}")
    else:
        print(f"Skipped {src_f}, not found.")

# Create __init__.py files in new packages
packages = ["backend", "backend/api", "backend/game_server", "backend/schemas", 
            "simulation", "simulation/bridge", "intelligence", 
            "intelligence/strategy", "intelligence/explainability", "intelligence/prediction", "intelligence/feature_engineering"]

for p in packages:
    init_path = os.path.join(p, "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, 'a').close()
