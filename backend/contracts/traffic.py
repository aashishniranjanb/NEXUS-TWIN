"""
Phase 10 Traffic Contracts.
Pydantic schemas for Traffic Request, Ingestion, Prediction, Anomaly, and Fingerprint endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TrafficStateRequest(BaseModel):
    city: str = "Philadelphia"
    intersection_id: int = 463
    hour: int = 17
    weekend: int = 0
    month: int = 10
    entry_heading: str = "NW"
    exit_heading: str = "SE"
    entry_street_name: str = "Market St"
    exit_street_name: str = "15th St"
    latitude: float = 39.9526
    longitude: float = -75.1652

class AnomalyEvaluationRequest(BaseModel):
    city: str = "Philadelphia"
    intersection_id: int = 463
    hour: int = 17
    weekend: int = 0
    entry_heading: str = "NW"
    observed_wait_s: float = 55.0
    observed_dist_m: float = 12.0

class AnomalyEvaluationResponse(BaseModel):
    intersection_id: int
    city: str
    anomaly_detected: bool
    anomaly_score: float = Field(ge=0.0, le=1.0)
    severity: str
    top_contributing_signals: List[str]
    feature_deviations: Dict[str, float]
    method: str

class FingerprintDiagnosticResponse(BaseModel):
    intersection_id: int
    city: str
    classification: str
    confidence: float = Field(ge=0.0, le=1.0)
    severity: str
    anomaly_score: float
    evidence: List[str]
    contributing_signals: List[str]
    historical_comparison: Dict[str, Any]
    limitation_disclaimer: str
