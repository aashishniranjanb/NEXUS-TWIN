"""
Unit Tests for Responsible AI Package.
Tests SafetyGate, ConfidenceEngine, EvidenceBuilder, RecommendationPolicy, and DecisionAuditLogger.
"""

import unittest
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.schemas.scenario_models import Strategy, ScenarioResult
from intelligence.responsible_ai.models import SafetyAssessment
from intelligence.responsible_ai.safety_gate import SafetyGate
from intelligence.responsible_ai.confidence import ConfidenceEngine
from intelligence.responsible_ai.evidence import EvidenceBuilder, ExplanationValidator
from intelligence.responsible_ai.recommendation_policy import RecommendationPolicy
from intelligence.responsible_ai.decision_audit import DecisionAuditLogger

class TestResponsibleAI(unittest.TestCase):
    def setUp(self):
        self.baseline = ScenarioResult(
            strategy_id="cand_do_nothing",
            strategy_type="do_nothing",
            parameters={},
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=10.0,
            predicted_queue_m=100.0,
            predicted_throughput=50,
            predicted_emergency_delay_s=0.0,
            score=45.0,
            per_junction_metrics={"J1": {"queue_length_m": 40.0}, "J2": {"queue_length_m": 60.0}}
        )
        self.cand_safe = ScenarioResult(
            strategy_id="cand_dynamic_lane",
            strategy_type="dynamic_lane",
            parameters={},
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=6.0,
            predicted_queue_m=65.0,
            predicted_throughput=62,
            predicted_emergency_delay_s=0.0,
            score=22.0,
            per_junction_metrics={"J1": {"queue_length_m": 30.0}, "J2": {"queue_length_m": 35.0}}
        )
        self.cand_spillback_trap = ScenarioResult(
            strategy_id="cand_bad_diversion",
            strategy_type="diversion",
            parameters={},
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=4.0,
            predicted_queue_m=160.0,
            predicted_throughput=40,
            predicted_emergency_delay_s=0.0,
            score=20.0,
            per_junction_metrics={"J1": {"queue_length_m": 10.0}, "J2": {"queue_length_m": 150.0}} # massive downstream spillback
        )

    def test_01_safety_gate_rejects_spillback(self):
        gate = SafetyGate(max_spillback_m=80.0)
        assess = gate.assess_candidate(Strategy("cand_bad_diversion", "diversion"), self.cand_spillback_trap, self.baseline)
        self.assertEqual(assess.status, "FAIL")
        self.assertEqual(assess.spillback_status, "CRITICAL")
        self.assertIn("J2", assess.blocked_junctions)

    def test_02_confidence_engine_narrow_margin(self):
        engine = ConfidenceEngine()
        # Candidate with tight score margin
        runner_up = ScenarioResult(
            strategy_id="cand_runner_up",
            strategy_type="green_extend",
            parameters={},
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=6.2,
            predicted_queue_m=66.0,
            predicted_throughput=61,
            score=22.2
        )
        conf = engine.evaluate_confidence(self.cand_safe, runner_up, prediction_confidence=0.80)
        self.assertLess(conf.score_margin, 0.05)
        self.assertEqual(conf.label, "MODERATE CONFIDENCE")

    def test_03_recommendation_policy_end_to_end(self):
        policy = RecommendationPolicy()
        candidates = [
            Strategy("cand_do_nothing", "do_nothing"),
            Strategy("cand_dynamic_lane", "dynamic_lane"),
            Strategy("cand_bad_diversion", "diversion")
        ]
        results = [self.baseline, self.cand_safe, self.cand_spillback_trap]
        
        decision = policy.evaluate_and_recommend(candidates, results, is_emergency_active=False)
        self.assertEqual(decision.strategy_type, "dynamic_lane")
        self.assertTrue(decision.human_approval_required)
        self.assertEqual(decision.status, "READY_FOR_HUMAN_REVIEW")

    def test_04_decision_audit_persistence(self):
        log_file = PROJECT_ROOT / "results" / "test_decision_audit.jsonl"
        if log_file.exists():
            os.remove(log_file)

        policy = RecommendationPolicy()
        candidates = [Strategy("cand_do_nothing", "do_nothing"), Strategy("cand_dynamic_lane", "dynamic_lane")]
        results = [self.baseline, self.cand_safe]
        
        decision = policy.evaluate_and_recommend(candidates, results)
        logger = DecisionAuditLogger(str(log_file))
        audit = logger.log_decision(decision, {"cand_do_nothing": 45.0, "cand_dynamic_lane": 22.0}, human_action="APPROVE", applied_strategy="dynamic_lane")
        
        self.assertTrue(log_file.exists())
        self.assertEqual(audit.human_action, "APPROVE")

        if log_file.exists():
            os.remove(log_file)

if __name__ == "__main__":
    unittest.main()
