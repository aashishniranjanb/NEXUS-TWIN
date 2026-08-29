"""
Pydantic Schemas for Traffic Intelligence State and Summaries.
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

class TrafficState(BaseModel):
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
    congestion_score: float = Field(ge=0.0, le=1.0)
    severity: CongestionSeverity
    estimated_queue_m: float
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[str]
    is_peak_period: bool
    model_version: str

class IntersectionRankItem(BaseModel):
    intersection_id: int
    city: str
    congestion_score: float
    severity: CongestionSeverity
    predicted_stopped_time_s: float
    queue_m: float

class IntersectionRankingResponse(BaseModel):
    city: str
    hour: int
    ranked_intersections: List[IntersectionRankItem]
