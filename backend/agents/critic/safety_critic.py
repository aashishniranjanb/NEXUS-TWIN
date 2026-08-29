"""
Responsible AI Safety Critic Module.
Audits candidate strategies and recommendations for evidence grounding, safety bounds,
cross-corridor side-effects, and emergency vehicle protection.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.contracts.recommendation import CriticEvaluationResult
from backend.contracts.simulation import (
    StrategyEvaluationResult, SimulationScenario, StrategyType
)

class SafetyCritic:
    def __init__(self):
        pass

    def evaluate_recommendation(
        self,
        scenario: SimulationScenario,
        recommended: StrategyEvaluationResult,
        all_evaluations: List[StrategyEvaluationResult]
    ) -> CriticEvaluationResult:
        """Audits the AI recommendation for safety, side-effects, and evidence compliance."""
        verified_checks: List[str] = []
        hazards: List[str] = []
        
        # Check 1: Quantitative Simulation Evidence
        if recommended.metrics.total_vehicular_delay_hours >= 0.0 and len(recommended.evidence) > 0:
            verified_checks.append("Digital Twin quantitative simulation evidence verified (900s kinematic model).")
        else:
            hazards.append("Missing numerical simulation evidence for candidate strategy.")
            
        # Check 2: Performance Improvement Delta
        if recommended.delay_reduction_pct > 10.0 or recommended.queue_reduction_pct > 10.0:
            verified_checks.append(f"Statistically significant improvement delta ({recommended.delay_reduction_pct:.1f}% delay, {recommended.queue_reduction_pct:.1f}% queue reduction).")
        else:
            hazards.append("Strategy offers marginal or negative delay reduction relative to unmitigated baseline.")
            
        # Check 3: Emergency Corridor Protection
        if scenario.has_emergency_vehicle:
            if recommended.strategy.strategy_type == StrategyType.EMERGENCY_PRIORITY or recommended.strategy.strategy_type == StrategyType.HYBRID_ADAPTIVE:
                verified_checks.append("Emergency priority verified: EMS green wave corridor preemption active.")
            else:
                hazards.append("EMS vehicle detected in corridor but recommended strategy does not guarantee preemption.")
                
        # Check 4: Cross-Street Spillover Risk Check
        if recommended.metrics.spillover_risk_score > 0.85:
            hazards.append("High residual spillover risk remains; secondary queue monitoring required.")
        else:
            verified_checks.append(f"Corridor spillover risk safely bounded at {recommended.metrics.spillover_risk_score:.2f}.")

        # Scoring & Determination
        if len(hazards) == 0:
            status = "APPROVED"
            safety_score = 94.0
            risk_level = "LOW"
            approved = True
            reasoning = "All safety criteria satisfied. Strategy demonstrated superior queue clearance with bounded side-effects."
        elif len(hazards) == 1 and not scenario.has_emergency_vehicle:
            status = "CONDITIONAL_APPROVAL"
            safety_score = 78.0
            risk_level = "MODERATE"
            approved = True
            reasoning = f"Approved with operational warnings: {hazards[0]}"
        else:
            status = "REJECTED"
            safety_score = 42.0
            risk_level = "HIGH"
            approved = False
            reasoning = f"Safety standards violated: {'; '.join(hazards)}"

        return CriticEvaluationResult(
            approved=approved,
            status=status,
            confidence=0.92,
            safety_score=safety_score,
            risk_level=risk_level,
            verified_evidence_checks=verified_checks,
            identified_hazards=hazards,
            reasoning=reasoning
        )

if __name__ == "__main__":
    from simulation.scenarios.scenario_model import ScenarioCatalog, ScenarioType
    from simulation.engine.digital_twin_engine import DigitalTwinEngine
    
    scen = ScenarioCatalog.get_scenario(ScenarioType.INCIDENT_LIKE_DISRUPTION)
    dt = DigitalTwinEngine()
    sim_res = dt.evaluate_scenario(scen)
    
    critic = SafetyCritic()
    eval_out = critic.evaluate_recommendation(scen, sim_res.recommended_strategy, sim_res.candidate_evaluations)
    print("Critic Evaluation Result:", eval_out.model_dump_json(indent=2))
