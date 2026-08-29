"""
Shared Stable Contracts for Downstream Consumers (Backend, AI Agents, Frontend).
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CongestionSeverity(str, Enum):
    NORMAL = "NORMAL"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class FingerprintClass(str, Enum):
    NORMAL = "NORMAL"
    RECURRING_CONGESTION = "RECURRING_CONGESTION"
    INCIDENT_LIKE = "INCIDENT_LIKE"
    DEMAND_SURGE = "DEMAND_SURGE"
    SIGNAL_RELATED = "SIGNAL_RELATED"

class TrafficPredictionContract(BaseModel):
    intersection_id: int
    target: str
    predicted_stopped_time_s: float
    confidence: float
    model_version: str

class TrafficStateContract(BaseModel):
    intersection_id: int
    city: str
    hour: int
    weekend: int
    entry_heading: str
    exit_heading: str
    turn_type: str
    predicted_stopped_time_s: float
    historical_baseline_p50_s: float
    historical_baseline_p80_s: float
    congestion_score: float
    severity: CongestionSeverity
    estimated_queue_m: float
    confidence: float
    evidence: List[str]
    is_peak_period: bool
    model_version: str

class AnomalyResultContract(BaseModel):
    intersection_id: int
    anomaly_detected: bool
    anomaly_score: float
    severity: str
    method: str
    top_contributing_signals: List[str]
    feature_deviations: Dict[str, float]

class TrafficFingerprintContract(BaseModel):
    intersection_id: int
    city: str
    classification: FingerprintClass
    confidence: float
    severity: str
    anomaly_score: float
    evidence: List[str]
    contributing_signals: List[str]
    historical_comparison: Dict[str, Any]
    limitation_disclaimer: str
