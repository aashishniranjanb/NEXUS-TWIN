"""
Feature Engineering Module for NEXUS-TWIN.
Transforms step-by-step TrafficState history into lag features and predictive dataset targets
per 32_TRAFFIC_FEATURE_ENGINEERING.md specifications.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any

class FeatureExtractor:
    def __init__(self, lag_steps: int = 5):
        self.lag_steps = lag_steps
        self.history: List[Dict[str, Any]] = []

    def push_state(self, state: Dict[str, Any]):
        """Pushes a step snapshot of state into rolling buffer."""
        self.history.append(state)

    def extract_features_at_step(self, step_idx: int, junction_id: str) -> Dict[str, Any]:
        """Extracts engineered features for a specific junction at step_idx."""
        if step_idx < 0 or step_idx >= len(self.history):
            return {}

        curr = self.history[step_idx]
        j_data = curr.get("junctions", {}).get(junction_id, {})
        
        curr_q = j_data.get("total_queue_m", 0.0)
        curr_halting = j_data.get("total_halting", 0)

        # Lag features
        prev_idx = max(0, step_idx - self.lag_steps)
        prev = self.history[prev_idx]
        prev_j_data = prev.get("junctions", {}).get(junction_id, {})
        prev_q = prev_j_data.get("total_queue_m", 0.0)

        queue_delta = curr_q - prev_q

        return {
            "step": curr.get("step", 0.0),
            "junction_id": junction_id,
            "active_vehicles": curr.get("active_vehicles", 0),
            "avg_speed_kmh": curr.get("avg_speed_kmh", 0.0),
            "avg_waiting_time_s": curr.get("avg_waiting_time_s", 0.0),
            "max_waiting_time_s": curr.get("max_waiting_time_s", 0.0),
            "queue_length_m": curr_q,
            "halting_vehicles": curr_halting,
            "previous_queue_m": prev_q,
            "queue_delta": round(queue_delta, 1),
            "signal_phase": j_data.get("current_phase", 0),
            "time_of_day_s": curr.get("step", 0.0)
        }

    def build_dataset_from_history(self, horizon_steps: int = 300) -> pd.DataFrame:
        """
        Builds a full tabular dataset with 5-minute future target labels from simulation history.
        horizon_steps = 300 (which corresponds to 5 minutes of 1s steps).
        """
        rows = []
        if len(self.history) <= horizon_steps:
            return pd.DataFrame()

        # Gather all junction IDs present in history
        junction_ids = set()
        for s in self.history:
            if "junctions" in s:
                junction_ids.update(s["junctions"].keys())

        for step_idx in range(self.lag_steps, len(self.history) - horizon_steps):
            future_step = self.history[step_idx + horizon_steps]

            for j_id in junction_ids:
                feats = self.extract_features_at_step(step_idx, j_id)
                if not feats:
                    continue

                # Target labels at step + horizon
                fut_j_data = future_step.get("junctions", {}).get(j_id, {})
                fut_q = fut_j_data.get("total_queue_m", 0.0)
                fut_halting = fut_j_data.get("total_halting", 0)

                # Binary classification target: will_congest_5min (1 if queue > 40m or halting >= 5, else 0)
                will_congest = 1 if (fut_q >= 37.5 or fut_halting >= 5) else 0

                feats["future_queue_5min_m"] = fut_q
                feats["will_congest_5min"] = will_congest
                rows.append(feats)

        return pd.DataFrame(rows)
