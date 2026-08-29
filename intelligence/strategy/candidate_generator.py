"""
Candidate Intervention Strategy Generator Module.
Generates candidate traffic management strategies (Green Extension, Dynamic Diversion, Emergency Priority, Hybrid)
with structured parameters and explicit operational trade-offs.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.contracts.simulation import (
    InterventionStrategy, StrategyType, SimulationScenario
)

class StrategyGenerator:
    @staticmethod
    def generate_candidates(scenario: SimulationScenario) -> List[InterventionStrategy]:
        """Generates candidate intervention strategies for the given scenario."""
        target_id = scenario.target_intersection_id
        candidates: List[InterventionStrategy] = []
        
        # 1. Baseline: No Action
        candidates.append(InterventionStrategy(
            strategy_id="STRAT_NO_ACTION",
            strategy_type=StrategyType.NO_ACTION,
            name="No Action (Baseline Operation)",
            target_junctions=[target_id],
            parameters={},
            description="Maintain standard fixed-time signal timing without dynamic intervention.",
            expected_trade_offs="Zero implementation effort, but allows queue spillover and delay accumulation."
        ))
        
        # 2. Strategy A: Extend Green
        candidates.append(InterventionStrategy(
            strategy_id="STRAT_EXTEND_GREEN",
            strategy_type=StrategyType.EXTEND_GREEN,
            name="Dynamic Green Extension (+20s)",
            target_junctions=[target_id],
            parameters={
                "green_extension_seconds": 20,
                "cycle_length_seconds": 110,
                "priority_phase": "major_arterial_through"
            },
            description="Extend green phase by 20s on critical approach to accelerate bottleneck discharge.",
            expected_trade_offs="Reduces primary queue rapidly; minor +12% delay penalty on minor cross-streets."
        ))
        
        # 3. Strategy B: Divert Traffic
        candidates.append(InterventionStrategy(
            strategy_id="STRAT_DIVERT_TRAFFIC",
            strategy_type=StrategyType.DIVERT_TRAFFIC,
            name="Upstream Dynamic Diversion (25%)",
            target_junctions=[max(0, target_id - 1), target_id],
            parameters={
                "diversion_rate_pct": 25.0,
                "vms_sign_nodes": [max(0, target_id - 1)],
                "secondary_route": "Parallel Arterial 2nd St"
            },
            description="Activate Variable Message Signs 500m upstream to reroute 25% of inflow to parallel corridors.",
            expected_trade_offs="Eliminates bottleneck shockwave; increases travel distance on secondary network by 400m."
        ))
        
        # 4. Strategy C: Emergency Priority (if applicable or general)
        if scenario.has_emergency_vehicle or scenario.scenario_type.value == "EMERGENCY_CORRIDOR":
            candidates.append(InterventionStrategy(
                strategy_id="STRAT_EMERGENCY_PRIORITY",
                strategy_type=StrategyType.EMERGENCY_PRIORITY,
                name="Emergency Corridor Green Wave",
                target_junctions=[target_id, target_id + 1, target_id + 2],
                parameters={
                    "preemption_lead_time_s": 15,
                    "hold_all_red_cross_s": 25,
                    "corridor_length_nodes": 3
                },
                description="Synchronized green wave preemption along ambulance path with cross-street red hold.",
                expected_trade_offs="Reduces emergency transit time by >55%; temporarily pauses cross-arterial traffic."
            ))
            
        # 5. Strategy D: Hybrid Adaptive
        candidates.append(InterventionStrategy(
            strategy_id="STRAT_HYBRID_ADAPTIVE",
            strategy_type=StrategyType.HYBRID_ADAPTIVE,
            name="Hybrid Adaptive Coordination",
            target_junctions=[max(0, target_id - 1), target_id, target_id + 1],
            parameters={
                "green_extension_seconds": 15,
                "diversion_rate_pct": 18.0,
                "cycle_offset_seconds": 8
            },
            description="Combines 15s green extension at bottleneck with 18% upstream metered diversion and synchronized offsets.",
            expected_trade_offs="Optimal balance: high queue reduction (-42%) with minimal cross-street penalty."
        ))
        
        return candidates

if __name__ == "__main__":
    from simulation.scenarios.scenario_model import ScenarioCatalog, ScenarioType
    scen = ScenarioCatalog.get_scenario(ScenarioType.INCIDENT_LIKE_DISRUPTION)
    strats = StrategyGenerator.generate_candidates(scen)
    print(f"Generated {len(strats)} candidate strategies for {scen.name}:")
    for s in strats:
        print(f" - [{s.strategy_type.value}] {s.name}")
