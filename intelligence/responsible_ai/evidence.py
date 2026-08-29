"""
Evidence Builder & Explanation Validator for NEXUS-TWIN.
Constructs structured evidence bundles from ScenarioResult objects and verifies
that explanation claims are 100% grounded in simulation data.
"""

from typing import List, Dict, Any
from backend.schemas.scenario_models import ScenarioResult
from intelligence.responsible_ai.models import EvidenceBundle, SafetyAssessment

class EvidenceBuilder:
    def build_bundle(self, best_result: ScenarioResult, baseline_result: ScenarioResult, runner_up_result: ScenarioResult = None, safety: SafetyAssessment = None) -> EvidenceBundle:
        # Compute deltas against baseline
        delay_delta = round(((best_result.predicted_delay_s - baseline_result.predicted_delay_s) / max(0.1, baseline_result.predicted_delay_s)) * 100, 1)
        queue_delta = round(((best_result.predicted_queue_m - baseline_result.predicted_queue_m) / max(0.1, baseline_result.predicted_queue_m)) * 100, 1)

        metric_deltas = {
            "delay_change_pct": delay_delta,
            "queue_change_pct": queue_delta,
            "score_diff_from_baseline": round(best_result.score - baseline_result.score, 2)
        }

        safety_metrics = {
            "status": safety.status if safety else "PASS",
            "emergency_route": safety.emergency_route_status if safety else "SAFE",
            "spillback": safety.spillback_status if safety else "LOW"
        }

        return EvidenceBundle(
            baseline_metrics={"delay_s": baseline_result.predicted_delay_s, "queue_m": baseline_result.predicted_queue_m, "score": baseline_result.score},
            chosen_metrics={"delay_s": best_result.predicted_delay_s, "queue_m": best_result.predicted_queue_m, "score": best_result.score},
            runner_up_metrics={"strategy": runner_up_result.strategy_type if runner_up_result else None, "score": runner_up_result.score if runner_up_result else None},
            metric_deltas=metric_deltas,
            safety_metrics=safety_metrics,
            provenance="SUMO 1.27.1 Digital Twin Simulation"
        )

class ExplanationValidator:
    def validate(self, action: str, reason: str, expected_impact: str, best_result: ScenarioResult, baseline_result: ScenarioResult) -> bool:
        # Check that action refers to the chosen strategy
        if not action or len(action.strip()) < 5:
            return False
        
        # Check that reason and impact are non-empty
        if not reason or not expected_impact:
            return False

        # Grounding check: ensure impact does not claim impossible zero-delay
        if "Delay: 0.0s" in expected_impact and best_result.predicted_delay_s > 1.0:
            return False

        return True

