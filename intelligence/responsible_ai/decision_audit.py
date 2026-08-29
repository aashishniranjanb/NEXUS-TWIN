"""
Decision Audit Log & Decision Trace Persister for Responsible AI.
Maintains auditable JSONL records of all evaluation traces, recommendations,
human actions, and resulting post-intervention outcomes.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from intelligence.responsible_ai.models import DecisionAudit, RecommendationDecision

class DecisionAuditLogger:
    def __init__(self, log_path: str = "results/p4_decision_audit.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_decision(self, rec: RecommendationDecision, candidate_scores: Dict[str, float], human_action: Optional[str] = None, applied_strategy: Optional[str] = None, final_outcome: Optional[Dict[str, Any]] = None) -> DecisionAudit:
        audit = DecisionAudit(
            evaluation_id=rec.evaluation_id,
            scenario_id=rec.scenario_id,
            state_timestamp=rec.state_timestamp,
            candidate_ids=list(candidate_scores.keys()),
            candidate_scores=candidate_scores,
            selected_strategy=rec.strategy_type,
            runner_up=rec.evidence.runner_up_metrics.get("strategy"),
            confidence=rec.confidence.value,
            explanation={"action": rec.action, "reason": rec.reason, "expected_impact": rec.expected_impact},
            human_action=human_action,
            applied_strategy=applied_strategy,
            final_outcome=final_outcome
        )

        with open(self.log_path, "a", encoding="utf-8") as f:
            if hasattr(audit, "model_dump_json"):
                f.write(audit.model_dump_json() + "\n")
            else:
                f.write(audit.json() + "\n")

        return audit
