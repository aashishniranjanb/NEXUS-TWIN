"""
Strategy Optimizer module for NEXUS-TWIN.
Computes multi-objective scores for candidate ScenarioResults based on network delay,
queue length, spillback penalties, emissions, and emergency delays per 35_STRATEGY_OPTIMIZATION.md.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from src.scenario_models import ScenarioResult

class StrategyOptimizer:
    def __init__(self, weights_config_path: str = None, spillback_weight: float = None):
        if weights_config_path is None:
            weights_config_path = str(Path(__file__).resolve().parent.parent / "configs" / "optimization_weights.json")

        self.weights = self.load_weights(weights_config_path)
        if spillback_weight is not None:
            self.weights["spillback"] = float(spillback_weight)

    def load_weights(self, filepath: str) -> Dict[str, float]:
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            return {
                "delay": 1.0,
                "queue": 1.0,
                "spillback": 1.5,
                "emissions": 0.5,
                "emergency": 3.0
            }

    def compute_spillback_penalty(self, candidate: ScenarioResult, do_nothing: ScenarioResult) -> float:
        """
        Calculates network spillback penalty by detecting queue displacement.
        Penalizes cases where a strategy reduces queue at one junction but causes queue spillback at adjacent junctions.
        """
        if not do_nothing or not candidate.per_junction_metrics or not do_nothing.per_junction_metrics:
            return 0.0

        penalty = 0.0
        for j_id, j_metrics in candidate.per_junction_metrics.items():
            base_q = do_nothing.per_junction_metrics.get(j_id, {}).get("queue_m", 0.0)
            cand_q = j_metrics.get("queue_m", 0.0)
            diff = cand_q - base_q
            # If queue increased at this junction compared to baseline do_nothing, penalize
            if diff > 0:
                penalty += diff

        return round(penalty, 2)

    def score_candidate(self, candidate: ScenarioResult, do_nothing: ScenarioResult = None) -> float:
        """Calculates multi-objective score for a candidate scenario (lowest score wins)."""
        w = self.weights
        
        delay_score = w["delay"] * candidate.predicted_delay_s
        queue_score = w["queue"] * candidate.predicted_queue_m
        
        spillback_p = self.compute_spillback_penalty(candidate, do_nothing) if do_nothing else 0.0
        spillback_score = w["spillback"] * spillback_p
        
        emissions_val = candidate.predicted_emissions if candidate.predicted_emissions is not None else 0.0
        emissions_score = w["emissions"] * emissions_val
        
        emergency_val = candidate.predicted_emergency_delay_s if candidate.predicted_emergency_delay_s is not None else 0.0
        emergency_score = w["emergency"] * emergency_val

        total_score = round(delay_score + queue_score + spillback_score + emissions_score + emergency_score, 2)
        candidate.score = total_score
        return total_score

    def select_best_strategy(self, candidates: List[ScenarioResult]) -> Tuple[ScenarioResult, float]:
        """
        Evaluates all candidate ScenarioResults and selects the candidate with lowest network score.
        If do_nothing performs best, do_nothing wins.
        """
        # Find do_nothing candidate as baseline reference for spillback computation
        do_nothing_cand = None
        for c in candidates:
            if c.strategy_type == "do_nothing":
                do_nothing_cand = c
                break

        # Score all candidates
        for c in candidates:
            self.score_candidate(c, do_nothing_cand)

        # Select candidate with lowest score
        valid_candidates = [c for c in candidates if c.success]
        if not valid_candidates:
            raise RuntimeError("No successful scenario evaluations to select from.")

        best_candidate = min(valid_candidates, key=lambda c: c.score)
        return best_candidate, best_candidate.score
