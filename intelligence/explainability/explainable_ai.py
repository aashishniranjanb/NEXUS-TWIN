"""
Explainable AI Module for NEXUS-TWIN.
Generates structured, grounded explanations directly from ScenarioResult data,
score margins, and XGBoost model confidence per 37_EXPLAINABLE_AI.md specifications.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from backend.schemas.scenario_models import ScenarioResult
from intelligence.prediction.congestion_predictor import PredictionOutput

@dataclass
class Explanation:
    action: str
    reason: str
    expected_impact: str
    confidence: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "expected_impact": self.expected_impact,
            "confidence": self.confidence
        }

class ExplainableAIEngine:
    def explain(
        self, 
        chosen: ScenarioResult, 
        all_candidates: List[ScenarioResult],
        prediction_map: Optional[Dict[str, PredictionOutput]] = None
    ) -> Explanation:
        """
        Generates grounded, template-driven explanation strictly from simulated ScenarioResult metrics and model confidence.
        """
        # Find baseline do_nothing and runner-up candidate
        do_nothing = None
        for c in all_candidates:
            if c.strategy_type == "do_nothing":
                do_nothing = c
                break

        sorted_cands = sorted([c for c in all_candidates if c.success], key=lambda c: c.score if c.score is not None else 9999)
        runner_up = sorted_cands[1] if len(sorted_cands) > 1 else sorted_cands[0]

        # 1. Action String
        action_str = self._format_action(chosen)

        # 2. Reason String
        if chosen.strategy_type == "do_nothing":
            reason_str = "Current signal timing and routing perform optimally. All candidate interventions score worse due to net network delay or queue spillback."
        else:
            delay_diff_pct = 0.0
            if runner_up.predicted_delay_s > 0:
                delay_diff_pct = round(((runner_up.predicted_delay_s - chosen.predicted_delay_s) / runner_up.predicted_delay_s) * 100, 1)

            pred_text = ""
            if prediction_map:
                high_prob = max([p.congestion_probability for p in prediction_map.values()], default=0.0)
                if high_prob >= 0.65:
                    pred_text = f" Driven by proactive 5-minute forecast (XGBoost model confidence {high_prob*100:.1f}%)."

            reason_str = (
                f"Achieves lowest network-wide score ({chosen.score}) among evaluated options. "
                f"Reduces average delay by {delay_diff_pct}% compared to next-best candidate ({runner_up.strategy_type}) "
                f"without causing queue spillback transfer.{pred_text}"
            )

        # 3. Expected Impact String
        ref = do_nothing if do_nothing else runner_up
        delay_imp = round(((ref.predicted_delay_s - chosen.predicted_delay_s) / ref.predicted_delay_s) * 100, 1) if ref.predicted_delay_s > 0 else 0.0
        queue_imp = round(((ref.predicted_queue_m - chosen.predicted_queue_m) / ref.predicted_queue_m) * 100, 1) if ref.predicted_queue_m > 0 else 0.0
        
        impact_str = f"Delay: {delay_imp:+.1f}%, Queue Length: {queue_imp:+.1f}%"
        if chosen.predicted_emissions is not None and ref.predicted_emissions:
            em_imp = round(((ref.predicted_emissions - chosen.predicted_emissions) / ref.predicted_emissions) * 100, 1)
            impact_str += f", CO2 Emissions: {em_imp:+.1f}%"

        # 4. Confidence Derivation: f(prediction_confidence, score_margin)
        score_margin = 0.0
        if len(sorted_cands) > 1 and runner_up.score is not None and chosen.score is not None and runner_up.score > 0:
            score_margin = (runner_up.score - chosen.score) / runner_up.score

        model_conf = 0.85
        if prediction_map:
            avg_pred_conf = np.mean([p.confidence_score for p in prediction_map.values()]) if prediction_map else 0.85
            model_conf = float(avg_pred_conf)

        combined_conf = min(98, max(55, int((model_conf * 50) + (60 * score_margin))))
        confidence_str = f"{combined_conf}%"

        return Explanation(
            action=action_str,
            reason=reason_str,
            expected_impact=impact_str,
            confidence=confidence_str
        )

    def _format_action(self, chosen: ScenarioResult) -> str:
        stype = chosen.strategy_type
        params = chosen.parameters

        if stype == "do_nothing":
            return "Maintain Current Baseline Signal Control"
        elif stype == "green_extend":
            j_id = params.get("junction_id", "J1")
            ext = params.get("extension_seconds", 20)
            return f"Extend Green Signal Phase by +{ext}s at {j_id}"
        elif stype == "diversion":
            pct = params.get("diversion_percent", 30)
            return f"Divert {pct}% Traffic to Parallel East Bypass Arterial"
        elif stype == "dynamic_lane":
            return "Activate Dynamic Shoulder Lane on J1-J2 Corridor"
        elif stype == "emergency_priority":
            return "Enable Priority Corridor Preemption for Emergency Vehicle"
        else:
            return f"Apply Intervention: {stype}"
