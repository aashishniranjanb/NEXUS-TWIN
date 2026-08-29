"""
Responsible AI Data Models for NEXUS-TWIN.
Defines schemas for SafetyAssessment, ConfidenceAssessment, EvidenceBundle,
RecommendationDecision, and DecisionAudit.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time
import uuid

class SafetyAssessment(BaseModel):
    status: str = "PASS"  # PASS, WARN, FAIL, NOT_APPLICABLE
    emergency_route_status: str = "SAFE"  # SAFE, WARNING, COMPROMISED
    spillback_status: str = "LOW"  # LOW, MODERATE, CRITICAL
    blocked_junctions: List[str] = Field(default_factory=list)
    signal_safety: bool = True
    route_validity: bool = True
    hard_constraint_failures: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class ConfidenceAssessment(BaseModel):
    value: float = 0.85
    label: str = "HIGH CONFIDENCE"  # LOW CONFIDENCE, MODERATE CONFIDENCE, HIGH CONFIDENCE
    prediction_confidence: float = 0.85
    score_margin: float = 0.15
    simulation_consistency: float = 0.90
    data_quality: float = 1.0
    reason: str = "Clear score margin separation and consistent counterfactual simulation outcomes."

class EvidenceBundle(BaseModel):
    baseline_metrics: Dict[str, Any] = Field(default_factory=dict)
    chosen_metrics: Dict[str, Any] = Field(default_factory=dict)
    runner_up_metrics: Dict[str, Any] = Field(default_factory=dict)
    metric_deltas: Dict[str, Any] = Field(default_factory=dict)
    safety_metrics: Dict[str, Any] = Field(default_factory=dict)
    provenance: str = "SUMO 1.27.1 Digital Twin Simulation"

class RecommendationDecision(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: f"eval_{uuid.uuid4().hex[:8]}")
    scenario_id: str = "default_corridor"
    strategy_id: str
    strategy_type: str
    status: str = "READY_FOR_HUMAN_REVIEW"
    action: str
    reason: str
    expected_impact: str
    confidence: ConfidenceAssessment
    safety: SafetyAssessment
    evidence: EvidenceBundle
    human_approval_required: bool = True
    state_timestamp: float = Field(default_factory=time.time)
    created_at: float = Field(default_factory=time.time)

class DecisionAudit(BaseModel):
    audit_id: str = Field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:8]}")
    evaluation_id: str
    timestamp: float = Field(default_factory=time.time)
    scenario_id: str
    state_timestamp: float
    candidate_ids: List[str]
    candidate_scores: Dict[str, float]
    selected_strategy: str
    runner_up: Optional[str] = None
    confidence: float
    explanation: Dict[str, str]
    human_action: Optional[str] = None  # APPROVE, REJECT, TRY_ANOTHER
    applied_strategy: Optional[str] = None
    final_outcome: Optional[Dict[str, Any]] = None
