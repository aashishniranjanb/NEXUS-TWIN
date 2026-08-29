"""
Recommendation Policy & Decision Pipeline for Responsible AI.
Orchestrates Safety Gate, Multi-Objective Optimizer, Confidence Engine,
Evidence Builder, and Explanation Generation into a unified human-review decision object.
"""

from typing import List, Dict, Any, Optional
from backend.schemas.scenario_models import Strategy, ScenarioResult
from intelligence.strategy.strategy_optimizer import StrategyOptimizer
from intelligence.explainability.explainable_ai import ExplainableAIEngine
from intelligence.responsible_ai.models import RecommendationDecision, SafetyAssessment
from intelligence.responsible_ai.safety_gate import SafetyGate
from intelligence.responsible_ai.confidence import ConfidenceEngine
from intelligence.responsible_ai.evidence import EvidenceBuilder, ExplanationValidator

class RecommendationPolicy:
    def __init__(self, optimizer: StrategyOptimizer = None, xai_engine: ExplainableAIEngine = None):
        self.optimizer = optimizer or StrategyOptimizer()
        self.xai_engine = xai_engine or ExplainableAIEngine()
        self.safety_gate = SafetyGate()
        self.confidence_engine = ConfidenceEngine()
        self.evidence_builder = EvidenceBuilder()
        self.explanation_validator = ExplanationValidator()

    def evaluate_and_recommend(self, candidates: List[Strategy], results: List[ScenarioResult], is_emergency_active: bool = False, prediction_confidence: float = 0.85) -> RecommendationDecision:
        # 1. Safety Gate Evaluation
        safe_results, assessments = self.safety_gate.filter_safe_candidates(candidates, results, is_emergency_active)

        # Baseline result
        baseline = next((r for r in results if r.strategy_type == "do_nothing"), results[0])

        # 2. No Safe Candidates Handling
        if not safe_results:
            assess_fail = assessments.get(results[0].strategy_id, SafetyAssessment(status="FAIL"))
            return RecommendationDecision(
                strategy_id=baseline.strategy_id,
                strategy_type="do_nothing",
                status="NO_SAFE_INTERVENTION",
                action="Maintain Baseline Operations (Manual Operator Review Required)",
                reason="All proposed candidate interventions violated safety constraints (excessive spillback or emergency route interference).",
                expected_impact=f"Baseline delay {baseline.predicted_delay_s:.1f}s maintained.",
                confidence=self.confidence_engine.evaluate_confidence(baseline, prediction_confidence=0.30),
                safety=assess_fail,
                evidence=self.evidence_builder.build_bundle(baseline, baseline, safety=assess_fail),
                human_approval_required=True
            )

        # 3. Select Best from Safe Candidates using Optimizer
        best_cand, best_score = self.optimizer.select_best_strategy(safe_results)

        # Identify runner up
        sorted_res = sorted(safe_results, key=lambda r: r.score)
        runner_up = sorted_res[1] if len(sorted_res) > 1 else None

        # 4. Generate Grounded Explanation
        exp_res = self.xai_engine.explain(best_cand, safe_results)
        action_val = exp_res.action if hasattr(exp_res, "action") else exp_res["action"]
        reason_val = exp_res.reason if hasattr(exp_res, "reason") else exp_res["reason"]
        impact_val = exp_res.expected_impact if hasattr(exp_res, "expected_impact") else exp_res["expected_impact"]

        # 5. Build Assessments & Evidence
        best_assess = assessments.get(best_cand.strategy_id, SafetyAssessment())
        conf_assess = self.confidence_engine.evaluate_confidence(best_cand, runner_up, prediction_confidence=prediction_confidence)
        evidence_bundle = self.evidence_builder.build_bundle(best_cand, baseline, runner_up, safety=best_assess)

        # 6. Validate Explanation Grounding
        is_grounded = self.explanation_validator.validate(action_val, reason_val, impact_val, best_cand, baseline)
        if not is_grounded:
            reason_val = f"Strategy {best_cand.strategy_type} minimizes network-wide loss (score {best_cand.score:.1f})."

        return RecommendationDecision(
            strategy_id=best_cand.strategy_id,
            strategy_type=best_cand.strategy_type,
            status="READY_FOR_HUMAN_REVIEW",
            action=action_val,
            reason=reason_val,
            expected_impact=impact_val,
            confidence=conf_assess,
            safety=best_assess,
            evidence=evidence_bundle,
            human_approval_required=True
        )
