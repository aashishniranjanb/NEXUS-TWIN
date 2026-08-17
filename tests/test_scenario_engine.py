"""
Unit & Integration Tests for NEXUS-TWIN Digital Twin Scenario Engine.
Verifies model creation, candidate generation, snapshot/restore repeatability,
strategy evaluation, and optimizer selection per Phase 3 Milestone 2 specs.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from experiments.run_baselines import setup_sumo_env, build_network_and_routes
setup_sumo_env()

import traci
from src.scenario_models import Strategy, ScenarioResult
from src.strategy_generator import StrategyGenerator
from src.scenario_engine import ScenarioEngine
from src.strategy_optimizer import StrategyOptimizer
from src.explainable_ai import ExplainableAIEngine

class TestScenarioEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_network_and_routes()
        cfg_file = str(PROJECT_ROOT / "simulation" / "configs" / "nexus.sumocfg")
        sumo_cmd = ["sumo", "-c", cfg_file, "--start", "--quit-on-end"]
        traci.start(sumo_cmd)
        
        cls.tls_ids = list(traci.trafficlight.getIDList())
        # Step simulation to t=20s to ensure active traffic state
        for _ in range(20):
            traci.simulationStep()

    @classmethod
    def tearDownClass(cls):
        try:
            traci.close()
        except Exception:
            pass

    def test_01_strategy_models(self):
        """Test Strategy and ScenarioResult model initialization."""
        strat = Strategy("test_1", "do_nothing", {}, "Test strategy")
        self.assertEqual(strat.strategy_id, "test_1")
        self.assertEqual(strat.strategy_type, "do_nothing")

        res = ScenarioResult(
            strategy_id="test_1",
            strategy_type="do_nothing",
            parameters={},
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=10.5,
            predicted_queue_m=100.0,
            predicted_throughput=50
        )
        self.assertEqual(res.predicted_delay_s, 10.5)
        self.assertTrue(res.success)

    def test_02_candidate_generation(self):
        """Test StrategyGenerator candidate creation."""
        generator = StrategyGenerator(self.tls_ids)
        dummy_state = {"junctions": {"J1": {"total_queue_m": 50.0}}}
        candidates = generator.generate_candidates(dummy_state)
        
        self.assertGreaterEqual(len(candidates), 3)
        self.assertEqual(candidates[0].strategy_type, "do_nothing")

    def test_03_snapshot_restore_repeatability(self):
        """Test that snapshot and restore returns SUMO to exact state and produces repeatable evaluation."""
        engine = ScenarioEngine(traci, self.tls_ids, default_horizon_seconds=60)
        cand = Strategy("test_do_nothing", "do_nothing", {}, "Repeatability test")

        # Evaluate candidate first time
        res1 = engine.evaluate_strategy(cand, horizon_seconds=60)

        # Evaluate candidate second time starting from restored state
        res2 = engine.evaluate_strategy(cand, horizon_seconds=60)

        # Metrics should be identical or within minimal simulation tolerance
        self.assertAlmostEqual(res1.predicted_delay_s, res2.predicted_delay_s, delta=1.5)
        self.assertAlmostEqual(res1.predicted_queue_m, res2.predicted_queue_m, delta=5.0)

    def test_04_strategy_evaluations(self):
        """Test evaluation of all candidate strategy types."""
        engine = ScenarioEngine(traci, self.tls_ids, default_horizon_seconds=30)
        
        strats = [
            Strategy("s_do_nothing", "do_nothing"),
            Strategy("s_green_extend", "green_extend", {"junction_id": self.tls_ids[0], "extension_seconds": 20}),
            Strategy("s_diversion", "diversion", {"from_edge": "J1_to_J2", "diversion_percent": 30}),
            Strategy("s_dynamic_lane", "dynamic_lane", {"edge_id": "J1_to_J2", "lane_index": 2})
        ]

        results = engine.evaluate_candidates(strats, horizon_seconds=30)
        self.assertEqual(len(results), 4)
        for r in results:
            self.assertTrue(r.success)

    def test_05_optimizer_and_explanation(self):
        """Test StrategyOptimizer and ExplainableAIEngine."""
        engine = ScenarioEngine(traci, self.tls_ids, default_horizon_seconds=30)
        generator = StrategyGenerator(self.tls_ids)
        
        current_state = engine.state_extractor.extract_state(traci)
        candidates = generator.generate_candidates(current_state)
        results = engine.evaluate_candidates(candidates, horizon_seconds=30)

        optimizer = StrategyOptimizer()
        best_candidate, score = optimizer.select_best_strategy(results)
        self.assertIsNotNone(best_candidate)
        self.assertIsNotNone(best_candidate.score)

        explain_engine = ExplainableAIEngine()
        explanation = explain_engine.explain(best_candidate, results)
        self.assertIsNotNone(explanation.action)
        self.assertIsNotNone(explanation.reason)
        self.assertIsNotNone(explanation.expected_impact)
        self.assertIsNotNone(explanation.confidence)

if __name__ == "__main__":
    unittest.main()
