"""
Phase 9 Digital Twin & Scenario Simulation Contracts.
Pydantic schemas for Scenarios, Interventions, Simulation Metrics, and Strategy Comparisons.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ScenarioType(str, Enum):
    BASELINE_PEAK = "BASELINE_PEAK"
    INCIDENT_LIKE_DISRUPTION = "INCIDENT_LIKE_DISRUPTION"
    DEMAND_SURGE = "DEMAND_SURGE"
    EMERGENCY_CORRIDOR = "EMERGENCY_CORRIDOR"
    SIGNAL_MALFUNCTION = "SIGNAL_MALFUNCTION"

class StrategyType(str, Enum):
    NO_ACTION = "NO_ACTION"
    EXTEND_GREEN = "EXTEND_GREEN"
    DIVERT_TRAFFIC = "DIVERT_TRAFFIC"
    EMERGENCY_PRIORITY = "EMERGENCY_PRIORITY"
    HYBRID_ADAPTIVE = "HYBRID_ADAPTIVE"

class SimulationScenario(BaseModel):
    scenario_id: str
    name: str
    scenario_type: ScenarioType
    city: str
    target_intersection_id: int
    horizon_minutes: int = 15
    inflow_multiplier: float = 1.0
    capacity_reduction_factor: float = 0.0
    has_emergency_vehicle: bool = False
    emergency_origin_node: Optional[int] = None
    emergency_destination_node: Optional[int] = None
    assumptions: List[str]

class InterventionStrategy(BaseModel):
    strategy_id: str
    strategy_type: StrategyType
    name: str
    target_junctions: List[int]
    parameters: Dict[str, Any]
    description: str
    expected_trade_offs: str

class SimulationMetrics(BaseModel):
    total_vehicular_delay_hours: float
    average_stopped_time_s: float
    max_queue_m: float
    corridor_throughput_veh_per_hr: int
    emergency_travel_time_s: Optional[float] = None
    spillover_risk_score: float = Field(ge=0.0, le=1.0)
    composite_network_score: float = Field(ge=0.0, le=100.0)

class StrategyEvaluationResult(BaseModel):
    strategy: InterventionStrategy
    metrics: SimulationMetrics
    delay_reduction_pct: float
    queue_reduction_pct: float
    throughput_gain_pct: float
    emergency_speedup_pct: Optional[float] = None
    rank: int = 1
    safety_approved: bool = True
    evidence: List[str]

class DigitalTwinSimulationResponse(BaseModel):
    scenario: SimulationScenario
    baseline_result: StrategyEvaluationResult
    candidate_evaluations: List[StrategyEvaluationResult]
    recommended_strategy: StrategyEvaluationResult
    summary_evidence: List[str]
    simulation_engine: str = "Deterministic Kinematic Digital Twin Engine v1.0"
    reproducible_seed: int = 42
