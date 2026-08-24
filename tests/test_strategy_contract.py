"""
Contract Tests for Strategy Generator and Strategy Optimizer in NEXUS-TWIN.
"""

import pytest
from backend.schemas.scenario_models import Strategy, ScenarioResult
from intelligence.strategy.strategy_generator import StrategyGenerator
from intelligence.strategy.strategy_optimizer import StrategyOptimizer

class TestStrategyContract:
    def setup_method(self):
        self.generator = StrategyGenerator(tls_ids=["J1", "J2", "J3"])
        self.optimizer = StrategyOptimizer()

    def test_candidate_generation_coverage(self):
        candidates = self.generator.generate_candidates("J2")
        assert len(candidates) >= 4
        types = [c.strategy_type for c in candidates]
        assert "do_nothing" in types
        assert "green_extend" in types
        assert "diversion" in types
        assert "dynamic_lane" in types

    def test_multi_objective_scoring(self):
        dn = ScenarioResult(
            strategy_id="do_nothing",
            strategy_type="do_nothing",
            parameters={},
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=0.35,
            predicted_queue_m=40.0,
            predicted_throughput=950,
            predicted_emissions=17.0,
            predicted_emergency_delay_s=20.0
        )

        cand = ScenarioResult(
            strategy_id="diversion_j2",
            strategy_type="diversion",
            parameters={"diversion_percent": 30.0},
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=0.20,
            predicted_queue_m=15.0,
            predicted_throughput=1030,
            predicted_emissions=12.0,
            predicted_emergency_delay_s=0.0
        )

        score_dn = self.optimizer.score_candidate(dn, dn)
        score_cand = self.optimizer.score_candidate(cand, dn)

        # Cand should score lower (better) than baseline do_nothing
        assert score_cand < score_dn

        best, best_score = self.optimizer.select_best_strategy([dn, cand])
        assert best.strategy_id == "diversion_j2"
