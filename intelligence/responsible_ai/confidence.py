"""
Responsible AI Confidence Engine for NEXUS-TWIN.
Computes calibrated recommendation confidence based on model prediction uncertainty,
score separation margin between candidates, simulation stability, and telemetry data quality.
"""

from typing import List
from backend.schemas.scenario_models import ScenarioResult
from intelligence.responsible_ai.models import ConfidenceAssessment

class ConfidenceEngine:
    def evaluate_confidence(self, best_result: ScenarioResult, runner_up_result: ScenarioResult = None, prediction_confidence: float = 0.85, data_quality: float = 1.0) -> ConfidenceAssessment:
        # 1. Score Margin Calculation
        if runner_up_result and runner_up_result.score > 0:
            score_diff = abs(runner_up_result.score - best_result.score)
            score_margin = min(1.0, score_diff / runner_up_result.score)
        else:
            score_margin = 0.5

        # 2. Simulation Consistency
        sim_consistency = 0.95 if best_result.success else 0.30

        # 3. Blended Recommendation Confidence
        raw_val = (prediction_confidence * 0.40) + (score_margin * 0.30) + (sim_consistency * 0.20) + (data_quality * 0.10)
        conf_val = round(max(0.10, min(0.99, raw_val)), 2)

        # 4. Confidence Banding
        if conf_val >= 0.75:
            label = "HIGH CONFIDENCE"
            reason = f"Strong winner separation (score margin {score_margin*100:.1f}%) and stable simulation telemetry."
        elif conf_val >= 0.50:
            label = "MODERATE CONFIDENCE"
            reason = f"Moderate score separation over runner-up ({runner_up_result.strategy_type if runner_up_result else 'baseline'})."
        else:
            label = "LOW CONFIDENCE"
            reason = "Narrow score margin or elevated telemetry uncertainty. Human review strongly advised."

        return ConfidenceAssessment(
            value=conf_val,
            label=label,
            prediction_confidence=prediction_confidence,
            score_margin=round(score_margin, 3),
            simulation_consistency=sim_consistency,
            data_quality=data_quality,
            reason=reason
        )
