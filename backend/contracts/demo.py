"""
Unified Demo and Integration Contracts for Phase 11.
Provides a single stable schema for the Frontend / Command Center without exposing internal ML details.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DemoAnalysisRequest(BaseModel):
    city: str = Field(default="Philadelphia", description="Target metropolitan area (Philadelphia, Boston, Atlanta, Chicago)")
    intersection_id: int = Field(default=0, description="Epicenter junction ID")
    scenario: str = Field(default="INCIDENT_LIKE_DISRUPTION", description="Scenario type: BASELINE_PEAK, INCIDENT_LIKE_DISRUPTION, DEMAND_SURGE, EMERGENCY_CORRIDOR")
    emergency_mode: bool = Field(default=False, description="Whether to activate emergency corridor preemption")
    hour: int = Field(default=17, description="Clock hour (0-23)")
    weekend: int = Field(default=0, description="0 for weekday, 1 for weekend")
    seed: int = Field(default=42, description="Deterministic simulation seed")

class DemoTrafficStateSection(BaseModel):
    intersection_id: int
    city: str
    name: str
    latitude: float
    longitude: float
    turn_type: str
    predicted_stopped_time_s: float
    historical_baseline_median_s: float
    historical_baseline_p80_s: float
    congestion_score: float
    severity: str
    estimated_queue_m: float
    evidence: List[str]

class DemoPredictionSection(BaseModel):
    target: str = "TotalTimeStopped_p50"
    predicted_value_s: float
    prediction_type: str = "Contextual Stopping Delay Expectation"
    model: str = "XGBoost Regressor v1.0 (Histogram Method)"
    confidence: float

class DemoAnomalySection(BaseModel):
    anomaly_score: float
    anomaly_detected: bool
    severity: str
    top_contributing_signals: List[str]
    feature_deviations: Dict[str, float]
    method: str

class DemoFingerprintSection(BaseModel):
    classification: str
    confidence: float
    severity: str
    evidence: List[str]
    contributing_signals: List[str]
    historical_comparison: Dict[str, Any]
    limitation_disclaimer: str

class DemoNetworkSection(BaseModel):
    total_nodes: int
    total_edges: int
    affected_nodes_count: int
    overall_spillover_risk: float
    domino_sequence: List[str]
    domino_steps: List[Dict[str, Any]]
    network_exposure_index: float
    containment_status: str
    nodes_summary: List[Dict[str, Any]]
    edges_summary: List[Dict[str, Any]]

class DemoStrategyItem(BaseModel):
    strategy_id: str
    strategy_type: str
    name: str
    rank: int
    delay_reduction_pct: float
    queue_reduction_pct: float
    throughput_gain_pct: float
    emergency_speedup_pct: Optional[float] = None
    composite_score: float
    description: str
    trade_offs: str
    evidence: List[str]

class DemoRecommendationSection(BaseModel):
    strategy_id: str
    strategy_type: str
    name: str
    rank: int
    delay_reduction_pct: float
    queue_reduction_pct: float
    throughput_gain_pct: float
    emergency_speedup_pct: Optional[float] = None
    composite_score: float
    reason: str
    evidence: List[str]
    trade_offs: str

class DemoResponsibleAISection(BaseModel):
    safety_status: str  # APPROVED, CONDITIONAL_APPROVAL, REJECTED
    critic_score: float
    risk_level: str
    verified_evidence_checks: List[str]
    identified_hazards: List[str]
    human_override_required: bool = True
    reasoning: str

class DemoExplainabilitySection(BaseModel):
    action: str
    why: str
    evidence: List[str]
    trade_off_analysis: str
    confidence_statement: str
    limitations: str

class DemoMetadataSection(BaseModel):
    pipeline_version: str = "1.0.0"
    dataset: str = "BigQuery-Geotab Empirical Telematics (856k rows)"
    timestamp: str
    seed: int
    execution_time_ms: float

class DemoAnalysisResponse(BaseModel):
    traffic_state: DemoTrafficStateSection
    prediction: DemoPredictionSection
    anomaly: DemoAnomalySection
    fingerprint: DemoFingerprintSection
    network: DemoNetworkSection
    strategies: List[DemoStrategyItem]
    recommendation: DemoRecommendationSection
    responsible_ai: DemoResponsibleAISection
    explainability: DemoExplainabilitySection
    metadata: DemoMetadataSection
