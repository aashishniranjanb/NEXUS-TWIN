"""
Phase 10 AI Recommendation and Critic Contracts.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.contracts.simulation import StrategyEvaluationResult, SimulationScenario
from backend.contracts.network_intelligence import DominoChain

class CriticEvaluationResult(BaseModel):
    approved: bool
    status: str  # APPROVED, CONDITIONAL_APPROVAL, REJECTED
    confidence: float = Field(ge=0.0, le=1.0)
    safety_score: float = Field(ge=0.0, le=100.0)
    risk_level: str
    verified_evidence_checks: List[str]
    identified_hazards: List[str]
    reasoning: str

class AIExplanation(BaseModel):
    summary: str
    observed_context: str
    predicted_impact: str
    simulated_alternatives: List[str]
    why_recommended: str
    trade_off_analysis: str
    confidence_statement: str

class AIRecommendationResponse(BaseModel):
    event_id: str
    timestamp: str
    intersection_id: int
    city: str
    traffic_fingerprint: str
    predicted_delay_s: float
    current_queue_m: float
    domino_threat_chain: List[str]
    scenario: SimulationScenario
    recommended_strategy: StrategyEvaluationResult
    alternative_strategies: List[StrategyEvaluationResult]
    critic_evaluation: CriticEvaluationResult
    explanation: AIExplanation
    human_approval_required: bool = True
