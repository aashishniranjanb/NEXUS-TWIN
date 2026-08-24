"""
Unit Tests for NEXUS-TWIN Phase 4 AI Intelligence & Congestion Prediction Engine.
Verifies FeatureExtractor, CongestionPredictor training & outputs, and Predictive Triggers.
"""

import sys
import unittest
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from intelligence.feature_engineering.feature_engineering import FeatureExtractor
from intelligence.prediction.congestion_predictor import CongestionPredictor, PredictionOutput
from intelligence.strategy.strategy_generator import StrategyGenerator
from intelligence.explainability.explainable_ai import ExplainableAIEngine

class TestPredictionEngine(unittest.TestCase):
    def test_01_feature_extractor(self):
        """Test FeatureExtractor lag windows and dataset generation."""
        fe = FeatureExtractor(lag_steps=2)
        
        # Push mock states
        for i in range(10):
            fe.push_state({
                "step": float(i),
                "active_vehicles": 10 + i,
                "avg_speed_kmh": 35.0,
                "avg_waiting_time_s": 2.0,
                "max_waiting_time_s": 5.0,
                "junctions": {
                    "J1": {"total_queue_m": 10.0 + i * 2, "total_halting": i, "current_phase": 0}
                }
            })

        feats = fe.extract_features_at_step(5, "J1")
        self.assertEqual(feats["junction_id"], "J1")
        self.assertEqual(feats["queue_length_m"], 20.0)
        self.assertEqual(feats["previous_queue_m"], 16.0)
        self.assertEqual(feats["queue_delta"], 4.0)

    def test_02_congestion_predictor_training(self):
        """Test CongestionPredictor training, predictions, and artifact creation."""
        predictor = CongestionPredictor()
        metrics = predictor.train()
        
        self.assertIn("test_accuracy", metrics)
        self.assertGreaterEqual(metrics["test_accuracy"], 0.70)
        self.assertIn("test_f1", metrics)

        # Test single prediction
        sample_features = {
            "active_vehicles": 50,
            "avg_speed_kmh": 25.0,
            "avg_waiting_time_s": 12.0,
            "max_waiting_time_s": 25.0,
            "queue_length_m": 120.0,
            "halting_vehicles": 15,
            "previous_queue_m": 90.0,
            "queue_delta": 30.0,
            "signal_phase": 0,
            "time_of_day_s": 300.0
        }
        pred = predictor.predict_congestion(sample_features)
        self.assertIsInstance(pred, PredictionOutput)
        self.assertGreaterEqual(pred.congestion_probability, 0.0)
        self.assertLessEqual(pred.congestion_probability, 1.0)
        self.assertGreaterEqual(pred.confidence_score, 0.50)

    def test_03_predictive_strategy_generator(self):
        """Test StrategyGenerator with predictive inputs."""
        generator = StrategyGenerator(["J1", "J2", "J3"])
        
        mock_pred_map = {
            "J1": PredictionOutput(
                predicted_queue_5min_m=150.0,
                will_congest_5min=True,
                congestion_probability=0.88,
                confidence_score=0.88
            )
        }

        candidates = generator.generate_candidates(
            current_state={"junctions": {"J1": {"total_queue_m": 50.0}}},
            prediction_map=mock_pred_map
        )
        
        self.assertGreaterEqual(len(candidates), 3)
        self.assertIn("Proactive trigger", candidates[1].description)

if __name__ == "__main__":
    unittest.main()
