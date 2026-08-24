"""
MetricsCollector module for NEXUS-TWIN.
Accumulates step-by-step state logs and exports summary metrics tables.
"""

import json
from typing import Dict, List, Any

class MetricsCollector:
    def __init__(self, controller_name: str):
        self.controller_name = controller_name
        self.step_history: List[Dict[str, Any]] = []
        self.completed_trip_times: List[float] = []

    def record_step(self, state: Dict[str, Any]):
        self.step_history.append(state)

    def record_completed_trip(self, travel_time: float):
        self.completed_trip_times.append(travel_time)

    def compute_summary(self) -> Dict[str, Any]:
        """Computes aggregate summary stats for evaluation."""
        if not self.step_history:
            return {}

        total_steps = len(self.step_history)
        avg_waiting = sum(s["avg_waiting_time_s"] for s in self.step_history) / total_steps
        avg_speed_kmh = sum(s["avg_speed_kmh"] for s in self.step_history) / total_steps
        
        # Calculate mean & max network-wide queue length (sum of junction halting count * 7.5m)
        total_queues_m = []
        for s in self.step_history:
            step_q = sum(j["total_queue_m"] for j in s["junctions"].values())
            total_queues_m.append(step_q)
            
        mean_queue_m = sum(total_queues_m) / total_steps if total_queues_m else 0.0
        max_queue_m = max(total_queues_m) if total_queues_m else 0.0
        
        total_throughput = len(self.completed_trip_times)

        avg_travel_time = (
            sum(self.completed_trip_times) / len(self.completed_trip_times)
            if self.completed_trip_times else 0.0
        )

        return {
            "controller": self.controller_name,
            "total_sim_steps": total_steps,
            "throughput_vehicles": total_throughput,
            "avg_waiting_time_s": round(avg_waiting, 2),
            "avg_travel_time_s": round(avg_travel_time, 2),
            "mean_queue_length_m": round(mean_queue_m, 2),
            "max_queue_length_m": round(max_queue_m, 2),
            "avg_speed_kmh": round(avg_speed_kmh, 2)
        }

    def save_results(self, filepath: str):
        summary = self.compute_summary()
        with open(filepath, "w") as f:
            json.dump(summary, f, indent=4)
        return summary
