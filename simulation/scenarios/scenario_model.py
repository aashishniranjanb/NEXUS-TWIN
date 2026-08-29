"""
Scenario Engine Module.
Defines canonical traffic scenarios, environmental assumptions, and disruption injection parameters.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.contracts.simulation import (
    SimulationScenario, ScenarioType
)

class ScenarioCatalog:
    @staticmethod
    def get_scenario(scenario_type: ScenarioType, city: str = "Philadelphia", target_id: int = 0) -> SimulationScenario:
        """Returns fully configured SimulationScenario instance."""
        if scenario_type == ScenarioType.INCIDENT_LIKE_DISRUPTION:
            return SimulationScenario(
                scenario_id="SCENARIO_INCIDENT_DISRUPTION",
                name="Off-Peak Lane Blockage & Bottleneck",
                scenario_type=ScenarioType.INCIDENT_LIKE_DISRUPTION,
                city=city,
                target_intersection_id=target_id,
                horizon_minutes=15,
                inflow_multiplier=1.0,
                capacity_reduction_factor=0.60,
                has_emergency_vehicle=False,
                assumptions=[
                    "60% effective capacity reduction on primary approach lane.",
                    "No immediate route diversion without active signal/VMS intervention.",
                    "Backward queue accumulation modeled at 15 km/h shockwave speed."
                ]
            )
        elif scenario_type == ScenarioType.DEMAND_SURGE:
            return SimulationScenario(
                scenario_id="SCENARIO_DEMAND_SURGE",
                name="Metropolitan Rush-Hour Surge",
                scenario_type=ScenarioType.DEMAND_SURGE,
                city=city,
                target_intersection_id=target_id,
                horizon_minutes=15,
                inflow_multiplier=1.45,
                capacity_reduction_factor=0.0,
                has_emergency_vehicle=False,
                assumptions=[
                    "45% uniform traffic inflow surge across all arterial approach arms.",
                    "Standard cycle times (90s) overwhelmed without dynamic split adjustment."
                ]
            )
        elif scenario_type == ScenarioType.EMERGENCY_CORRIDOR:
            return SimulationScenario(
                scenario_id="SCENARIO_EMERGENCY_CORRIDOR",
                name="Critical Ambulance Corridor Priority",
                scenario_type=ScenarioType.EMERGENCY_CORRIDOR,
                city=city,
                target_intersection_id=target_id,
                horizon_minutes=15,
                inflow_multiplier=1.1,
                capacity_reduction_factor=0.1,
                has_emergency_vehicle=True,
                emergency_origin_node=target_id,
                emergency_destination_node=(target_id + 3),
                assumptions=[
                    "Class-1 Emergency Medical Service (EMS) vehicle transit across corridor.",
                    "Requires green wave preemption without inducing gridlock on cross streets."
                ]
            )
        else: # BASELINE_PEAK
            return SimulationScenario(
                scenario_id="SCENARIO_BASELINE_PEAK",
                name="Standard 5:00 PM Peak Commute Baseline",
                scenario_type=ScenarioType.BASELINE_PEAK,
                city=city,
                target_intersection_id=target_id,
                horizon_minutes=15,
                inflow_multiplier=1.0,
                capacity_reduction_factor=0.0,
                has_emergency_vehicle=False,
                assumptions=[
                    "Normal historical 5:00 PM commuter flow.",
                    "Fixed-time signal coordination."
                ]
            )

if __name__ == "__main__":
    scen = ScenarioCatalog.get_scenario(ScenarioType.INCIDENT_LIKE_DISRUPTION)
    print("Scenario JSON:", scen.model_dump_json(indent=2))
