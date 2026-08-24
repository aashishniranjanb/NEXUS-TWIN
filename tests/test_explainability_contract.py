"""
Contract Tests for Explainability Module (XAI) in NEXUS-TWIN.
Verifies ExplainableAIEngine outputs, grounding in ScenarioResults, confidence calculation, and schema adherence.
"""

import pytest
from backend.schemas.scenario_models import Strategy, ScenarioResult
from intelligence.explainability.explainable_ai import ExplainableAIEngine, Explanation
from intelligence.prediction.congestion_predictor import PredictionOutput

class TestExplainabilityContract:
    def setup_method(self):
        self.xai = ExplainableAIEngine()

    def test_explanation_contract_diversion(self):
        chosen = ScenarioResult(
            strategy_id="diversion_j2",
            strategy_type="diversion",
            parameters={"from_edge": "J1_to_J2", "diversion_percent": 35.0},
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=0.20,
            predicted_queue_m=12.0,
            predicted_throughput=1020,
            predicted_emissions=12.0,
            predicted_emergency_delay_s=0.0,
            score=15.5
        )

        baseline = ScenarioResult(
            strategy_id="do_nothing",
            strategy_type="do_nothing",
            parameters={},
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=0.38,
            predicted_queue_m=45.0,
            predicted_throughput=980,
            predicted_emissions=18.0,
            predicted_emergency_delay_s=25.0,
            score=65.0
        )

        all_candidates = [chosen, baseline]
        explanation = self.xai.explain(chosen, all_candidates)

        assert isinstance(explanation, Explanation)
        assert isinstance(explanation.action, str) and len(explanation.action) > 0
        assert isinstance(explanation.reason, str) and len(explanation.reason) > 0
        assert isinstance(explanation.expected_impact, str)
        assert "%" in explanation.confidence

        data = explanation.to_dict()
        assert "action" in data
        assert "reason" in data
        assert "expected_impact" in data
        assert "confidence" in data

    def test_explanation_do_nothing(self):
        dn = ScenarioResult(
            strategy_id="do_nothing",
            strategy_type="do_nothing",
            parameters={},
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=0.20,
            predicted_queue_m=10.0,
            predicted_throughput=1050,
            score=10.0
        )
        explanation = self.xai.explain(dn, [dn])
        assert "Baseline" in explanation.action or "Maintain" in explanation.action
        assert "optimally" in explanation.reason or "score" in explanation.reason
