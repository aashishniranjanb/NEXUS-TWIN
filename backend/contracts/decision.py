"""
Phase 10 Human Decision and Execution Contracts.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class HumanDecisionRequest(BaseModel):
    event_id: str
    action: str  # "APPROVE", "OVERRIDE", "REJECT"
    selected_strategy_id: str
    operator_notes: Optional[str] = "Approved by traffic operations supervisor."
    override_reason: Optional[str] = None

class HumanDecisionResponse(BaseModel):
    event_id: str
    decision_id: str
    action: str
    applied_strategy_id: str
    status: str  # "DISPATCHED_TO_FIELD_SIGNALS", "OVERRIDDEN_MANUALLY", "REJECTED"
    projected_network_gain: str
    timestamp: str
    audit_trail: List[str]
