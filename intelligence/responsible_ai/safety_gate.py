"""
Hard Safety Gate & Constraint Validator for NEXUS-TWIN.
Evaluates candidates against emergency corridor clearance, prohibited spillback,
signal timing constraints, and route reachability.
"""

from typing import List, Dict, Any, Tuple
from backend.schemas.scenario_models import Strategy, ScenarioResult
from intelligence.responsible_ai.models import SafetyAssessment

class SafetyGate:
    def __init__(self, max_green_extension_sec: float = 60.0, max_spillback_m: float = 80.0):
        self.max_green_extension_sec = max_green_extension_sec
        self.max_spillback_m = max_spillback_m

    def assess_candidate(self, strategy: Strategy, result: ScenarioResult, baseline_result: ScenarioResult, is_emergency_active: bool = False) -> SafetyAssessment:
        assessment = SafetyAssessment()
        failures = []
        warnings = []

        # 1. Parameter & Strategy Validity Check
        if strategy.strategy_type == "green_extend":
            ext = strategy.parameters.get("extension_seconds", 0)
            if ext > self.max_green_extension_sec:
                failures.append(f"Green extension ({ext}s) exceeds safe maximum ({self.max_green_extension_sec}s).")
                assessment.signal_safety = False

        # 2. Emergency Route Protection
        if is_emergency_active:
            # If candidate causes severe emergency vehicle delay increase relative to baseline
            if result.predicted_emergency_delay_s > baseline_result.predicted_emergency_delay_s + 15.0:
                failures.append("Severe emergency corridor delay degradation detected.")
                assessment.emergency_route_status = "COMPROMISED"
            elif result.predicted_emergency_delay_s > baseline_result.predicted_emergency_delay_s:
                warnings.append("Minor emergency corridor delay increase.")
                assessment.emergency_route_status = "WARNING"
            else:
                assessment.emergency_route_status = "SAFE"

        # 3. Downstream Spillback & Blocked Junction Detection
        for j_id, j_metrics in result.per_junction_metrics.items():
            base_q = baseline_result.per_junction_metrics.get(j_id, {}).get("queue_length_m", 0.0)
            cand_q = j_metrics.get("queue_length_m", 0.0)
            
            # If queue at non-target junction exploded
            if cand_q > base_q + self.max_spillback_m:
                failures.append(f"Excessive queue spillback transferred to junction {j_id} (+{cand_q - base_q:.1f}m).")
                assessment.blocked_junctions.append(j_id)
                assessment.spillback_status = "CRITICAL"
            elif cand_q > base_q + 25.0:
                warnings.append(f"Moderate queue buildup at junction {j_id}.")
                if assessment.spillback_status != "CRITICAL":
                    assessment.spillback_status = "MODERATE"

        # 4. Final Status Synthesis
        assessment.hard_constraint_failures = failures
        assessment.warnings = warnings

        if failures:
            assessment.status = "FAIL"
        elif warnings:
            assessment.status = "WARN"
        else:
            assessment.status = "PASS"

        return assessment

    def filter_safe_candidates(self, candidates: List[Strategy], results: List[ScenarioResult], is_emergency_active: bool = False) -> Tuple[List[ScenarioResult], Dict[str, SafetyAssessment]]:
        assessments = {}
        safe_results = []
        
        # Locate baseline do_nothing result
        baseline = next((r for r in results if r.strategy_type == "do_nothing"), results[0])
        cand_map = {c.strategy_id: c for c in candidates}

        for res in results:
            cand = cand_map.get(res.strategy_id, Strategy(res.strategy_id, res.strategy_type))
            assess = self.assess_candidate(cand, res, baseline, is_emergency_active)
            assessments[res.strategy_id] = assess
            
            if assess.status != "FAIL" and res.success:
                safe_results.append(res)

        return safe_results, assessments
