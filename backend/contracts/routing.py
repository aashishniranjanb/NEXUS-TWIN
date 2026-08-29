"""
Pydantic contracts for AI Dynamic Route & Spillover Optimizer.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RouteOptimizationRequest(BaseModel):
    origin: int = Field(..., description="Origin intersection ID")
    destination: int = Field(..., description="Destination intersection ID")
    mode: str = Field(default="normal", description="Routing mode: normal or emergency")
    city: str = Field(default="Philadelphia", description="Target metropolitan area")
    hour: int = Field(default=17, description="Clock hour")
    weekend: int = Field(default=0, description="0 for weekday, 1 for weekend")

class DemoRouteInfo(BaseModel):
    nodes: List[int]
    edges: List[Dict[str, Any]]
    predicted_eta_s: float
    congestion_risk: float
    spillover_risk: float

class RouteComparison(BaseModel):
    baseline_eta_s: float
    optimized_eta_s: float
    eta_improvement_pct: float

class RouteReasoning(BaseModel):
    why: str
    evidence: List[str]
    tradeoffs: List[str]

class RouteOptimizationResponse(BaseModel):
    origin: int
    destination: int
    mode: str
    recommended_route: DemoRouteInfo
    alternatives: List[DemoRouteInfo]
    comparison: RouteComparison
    reasoning: RouteReasoning
    metadata: Dict[str, Any]
