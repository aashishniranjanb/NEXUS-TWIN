"""
Phase 8 Network Intelligence Contracts.
Pydantic schemas for Network Graph, Node/Edge states, Spillover Predictions, Domino Chains, and Network Metrics.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class NodeTrafficState(BaseModel):
    intersection_id: int
    name: str
    latitude: float
    longitude: float
    congestion_score: float = Field(ge=0.0, le=1.0)
    severity: str
    predicted_stopped_time_s: float
    queue_m: float
    turn_type: str = "Straight"
    is_bottleneck: bool = False

class EdgeTrafficState(BaseModel):
    edge_id: str
    source: int
    target: int
    street_name: str
    heading: str
    distance_m: float
    speed_limit_kmh: float = 50.0
    free_flow_time_s: float
    current_travel_time_s: float
    congestion_ratio: float = Field(ge=1.0)
    capacity_veh_per_hr: int = 1200
    current_flow_veh_per_hr: int = 600

class GraphSnapshot(BaseModel):
    city: str
    total_nodes: int
    total_edges: int
    nodes: List[NodeTrafficState]
    edges: List[EdgeTrafficState]

class AffectedIntersection(BaseModel):
    intersection_id: int
    name: str
    distance_from_source_m: float
    spillover_risk_score: float = Field(ge=0.0, le=1.0)
    propagation_level: int = Field(ge=1)
    estimated_arrival_minutes: float
    projected_queue_m: float
    evidence: str

class SpilloverPrediction(BaseModel):
    source_intersection: int
    source_name: str
    city: str
    current_queue_m: float
    affected_intersections: List[AffectedIntersection]
    max_propagation_depth: int
    overall_corridor_risk: float = Field(ge=0.0, le=1.0)
    evidence: List[str]
    method: str = "Kinematic Shockwave & Graph Distance Propagation"
    confidence: float = Field(ge=0.0, le=1.0)
    limitations: str

class DominoStep(BaseModel):
    step_index: int
    from_node: int
    from_name: str
    to_node: int
    to_name: str
    transit_distance_m: float
    cumulative_delay_s: float
    estimated_time_to_impact_min: float
    impact_severity: str

class DominoChain(BaseModel):
    chain_id: str
    corridor_name: str
    critical_origin_node: int
    propagation_sequence: List[str]  # e.g. ["J2", "J1", "J4"]
    steps: List[DominoStep]
    network_exposure_score: float = Field(ge=0.0, le=1.0)
    estimated_total_corridor_delay_s: float
    intervention_urgency: str

class NetworkMetrics(BaseModel):
    total_intersections: int
    congested_intersections_count: int
    active_corridor_chokepoints: List[int]
    average_network_congestion_score: float
    network_exposure_index: float
    highest_risk_propagation_corridor: str
    spillover_containment_status: str

class NetworkIntelligenceResponse(BaseModel):
    city: str
    timestamp: str
    graph_snapshot: GraphSnapshot
    spillover: SpilloverPrediction
    domino_chain: DominoChain
    network_metrics: NetworkMetrics
    evidence: List[str]
    model_metadata: Dict[str, Any]
