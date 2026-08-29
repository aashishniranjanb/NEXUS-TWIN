"""
API Request and Response Schemas for NEXUS-TWIN.
Defines typed Pydantic models matching shared_config/ids.yaml and DATA_CONTRACT.md.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# --- Traffic & Incident Requests ---

class IncidentTriggerRequest(BaseModel):
    junction_id: str = Field("J2", description="Target junction identifier (J1, J2, J3)")
    incident_type: str = Field("accident", description="accident, closure, surge, weather, emergency")
    severity: str = Field("high", description="low, medium, high, critical")
    location_x: Optional[float] = 2.5
    location_z: Optional[float] = 0.0

class StrategyEvaluateRequest(BaseModel):
    horizon_seconds: int = Field(180, description="Evaluation forecast horizon in seconds")
    junction_id: str = Field("J2", description="Target junction identifier")
    strategy_type: str = Field("green_extend", description="green_extend, diversion, dynamic_lane, emergency_priority, do_nothing")
    extension_seconds: Optional[float] = Field(20.0, description="Seconds to extend green light")
    diversion_percent: Optional[float] = Field(25.0, description="Percentage of traffic diverted")

class StrategyApplyRequest(BaseModel):
    strategy_id: str = Field("green_extend_J2", description="Strategy identifier")
    strategy_type: str = Field("green_extend", description="Strategy type")
    junction_id: str = Field("J2", description="Target junction")
    parameters: Dict[str, Any] = Field(default_factory=dict)

class EmergencyPreemptionRequest(BaseModel):
    corridor: str = Field("J1-J2-J3", description="Target emergency corridor")
    vehicle_id: str = Field("AMBULANCE_01", description="Emergency vehicle ID")
    junction_id: str = Field("J2", description="Target junction")

# --- Telemetry & WebSocket Models ---

class VehicleTelemetry(BaseModel):
    id: str
    type: str = "car"
    x: float
    y: float = 0.0
    z: float
    speed_mps: float
    angle_deg: float
    lane_id: str

class SignalTelemetry(BaseModel):
    junction_id: str
    phase_index: int
    phase_state: str
    remaining_duration_s: float

class WebSocketTrafficMessage(BaseModel):
    type: str # "vehicle_state" | "signal_state" | "incident_event"
    step: Optional[int] = 0
    vehicles: Optional[List[VehicleTelemetry]] = None
    signals: Optional[List[SignalTelemetry]] = None
    event_type: Optional[str] = None
    junction_id: Optional[str] = None

# --- Unified Multi-Agent Intelligence Schemas ---

class SituationState(BaseModel):
    junction_id: str
    active_vehicles: int
    avg_speed_kmh: float
    avg_waiting_time_s: float
    queue_length_m: float

class PredictionOutputModel(BaseModel):
    will_congest_5min: bool
    congestion_probability: float
    predicted_queue_5min_m: float
    confidence_score: float

class FingerprintState(BaseModel):
    pattern_type: str
    dataset_similarity_score: float
    factors: Dict[str, float]

class RecommendationOutput(BaseModel):
    strategy: str
    confidence: float
    explanation: str
    action_plan: str

class CandidateFuture(BaseModel):
    strategy_type: str
    delay_change_pct: float
    queue_change_pct: float
    emergency_eta_change_sec: float
    emissions_change_pct: float
    is_best: bool
    score: float

class MultiAgentDecisionResponse(BaseModel):
    timestamp: float
    situation: SituationState
    prediction: PredictionOutputModel
    fingerprint: FingerprintState
    recommendation: RecommendationOutput
    candidates: List[CandidateFuture]

