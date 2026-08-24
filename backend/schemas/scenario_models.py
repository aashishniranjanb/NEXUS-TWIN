"""
Scenario Data Models for NEXUS-TWIN Digital Twin Engine.
Defines typed representations for candidate strategies and simulation evaluation results.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class Strategy:
    strategy_id: str
    strategy_type: str  # "do_nothing", "green_extend", "diversion", "dynamic_lane", "emergency_priority"
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "strategy_type": self.strategy_type,
            "parameters": self.parameters,
            "description": self.description
        }

@dataclass
class ScenarioResult:
    strategy_id: str
    strategy_type: str
    parameters: Dict[str, Any]
    simulation_start_time: float
    simulation_end_time: float
    horizon_seconds: float
    predicted_delay_s: float
    predicted_queue_m: float
    predicted_throughput: int
    predicted_emissions: Optional[float] = None
    predicted_emergency_delay_s: Optional[float] = None
    per_junction_metrics: Dict[str, Any] = field(default_factory=dict)
    network_metrics: Dict[str, Any] = field(default_factory=dict)
    score: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "strategy_type": self.strategy_type,
            "parameters": self.parameters,
            "simulation_start_time": self.simulation_start_time,
            "simulation_end_time": self.simulation_end_time,
            "horizon_seconds": self.horizon_seconds,
            "predicted_delay_s": self.predicted_delay_s,
            "predicted_queue_m": self.predicted_queue_m,
            "predicted_throughput": self.predicted_throughput,
            "predicted_emissions": self.predicted_emissions,
            "predicted_emergency_delay_s": self.predicted_emergency_delay_s,
            "per_junction_metrics": self.per_junction_metrics,
            "network_metrics": self.network_metrics,
            "score": self.score,
            "success": self.success,
            "error_message": self.error_message
        }
