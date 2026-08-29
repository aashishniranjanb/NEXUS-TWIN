"""
Digital Twin Kinematic Simulation Engine.
Executes deterministic physical traffic flow simulations across network corridors to evaluate candidate strategies.
"""

import json
import os
import sys
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.contracts.simulation import (
    SimulationScenario, InterventionStrategy, StrategyType,
    SimulationMetrics, StrategyEvaluationResult, DigitalTwinSimulationResponse
)
from intelligence.strategy.candidate_generator import StrategyGenerator
from simulation.scenarios.scenario_model import ScenarioCatalog, ScenarioType

class DigitalTwinEngine:
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed

    def simulate_strategy(
        self,
        scenario: SimulationScenario,
        strategy: InterventionStrategy
    ) -> SimulationMetrics:
        """
        Runs a deterministic 15-minute (900s) macroscopic simulation of traffic kinematics under the specified strategy.
        """
        # Base flow parameters
        inflow_rate = 950.0 * scenario.inflow_multiplier  # veh/hr
        base_capacity = 1200.0 * (1.0 - scenario.capacity_reduction_factor)  # veh/hr
        cycle_len = 90.0  # seconds
        base_green = 45.0  # seconds
        
        # Apply Strategy Adjustments
        eff_green = base_green
        eff_inflow = inflow_rate
        emergency_transit_s: Optional[float] = None
        
        if strategy.strategy_type == StrategyType.EXTEND_GREEN:
            ext_s = float(strategy.parameters.get("green_extension_seconds", 20))
            eff_green += ext_s
            cycle_len = float(strategy.parameters.get("cycle_length_seconds", 110))
            
        elif strategy.strategy_type == StrategyType.DIVERT_TRAFFIC:
            div_pct = float(strategy.parameters.get("diversion_rate_pct", 25.0)) / 100.0
            eff_inflow *= (1.0 - div_pct)
            
        elif strategy.strategy_type == StrategyType.EMERGENCY_PRIORITY:
            eff_green += 30.0
            cycle_len = 120.0
            
        elif strategy.strategy_type == StrategyType.HYBRID_ADAPTIVE:
            ext_s = float(strategy.parameters.get("green_extension_seconds", 15))
            div_pct = float(strategy.parameters.get("diversion_rate_pct", 18.0)) / 100.0
            eff_green += ext_s
            eff_inflow *= (1.0 - div_pct)
            
        # Effective discharge capacity (saturation flow 1800 veh/hr during green)
        sat_flow = 1800.0
        eff_capacity = min(base_capacity * 1.3, sat_flow * (eff_green / cycle_len))
        
        # Queue accumulation & Delay integration over 15 minutes (900s)
        # Webster's delay model + deterministic overflow queue
        volume_to_capacity = min(1.8, eff_inflow / max(100.0, eff_capacity))
        
        # Uniform delay term
        c = cycle_len
        g_c = eff_green / c
        d1 = 0.5 * c * ((1.0 - g_c)**2) / (1.0 - min(0.99, g_c * volume_to_capacity))
        
        # Incremental overflow delay term
        if volume_to_capacity > 0.95:
            d2 = 900.0 / 4.0 * ((volume_to_capacity - 1.0) + math.sqrt((volume_to_capacity - 1.0)**2 + (12.0 * (volume_to_capacity - 0.95) / (eff_capacity * 0.25))))
        else:
            d2 = 0.0
            
        avg_wait_s = max(4.0, min(140.0, d1 + d2))
        
        # Max queue in meters (~7.5m per queued vehicle)
        excess_veh = max(0.0, (eff_inflow - eff_capacity) * (15.0 / 60.0))
        queue_veh = max(3.0, (eff_inflow * (c - eff_green) / 3600.0) + excess_veh)
        max_q_m = round(float(queue_veh * 7.5), 1)
        
        # Total vehicle-hours of delay across corridor
        tot_delay_hrs = round(float((eff_inflow * avg_wait_s * (15.0 / 60.0)) / 3600.0), 2)
        throughput = int(min(eff_inflow, eff_capacity * 0.95))
        
        # Spillover risk
        spillover_risk = round(float(min(1.0, max(0.05, (max_q_m / 250.0) * volume_to_capacity))), 3)
        
        # Emergency travel time calculation
        if scenario.has_emergency_vehicle or scenario.scenario_type.value == "EMERGENCY_CORRIDOR":
            corridor_dist_m = 1200.0
            if strategy.strategy_type == StrategyType.EMERGENCY_PRIORITY:
                emergency_transit_s = round(float((corridor_dist_m / (65.0 / 3.6)) + 10.0), 1) # ~76s
            elif strategy.strategy_type == StrategyType.HYBRID_ADAPTIVE:
                emergency_transit_s = round(float((corridor_dist_m / (50.0 / 3.6)) + 25.0), 1) # ~111s
            elif strategy.strategy_type == StrategyType.DIVERT_TRAFFIC:
                emergency_transit_s = round(float((corridor_dist_m / (45.0 / 3.6)) + 40.0), 1) # ~136s
            elif strategy.strategy_type == StrategyType.EXTEND_GREEN:
                emergency_transit_s = round(float((corridor_dist_m / (40.0 / 3.6)) + 50.0), 1) # ~158s
            else: # NO_ACTION
                emergency_transit_s = round(float((corridor_dist_m / (25.0 / 3.6)) + avg_wait_s * 1.5), 1) # ~240s
                
        # Composite Network Score (0-100, higher is better)
        delay_penalty = min(50.0, avg_wait_s * 0.6)
        queue_penalty = min(30.0, (max_q_m / 300.0) * 30.0)
        throughput_bonus = min(20.0, (throughput / 1000.0) * 20.0)
        composite_score = round(float(max(10.0, min(99.0, 100.0 - delay_penalty - queue_penalty + throughput_bonus))), 1)

        return SimulationMetrics(
            total_vehicular_delay_hours=tot_delay_hrs,
            average_stopped_time_s=round(avg_wait_s, 1),
            max_queue_m=max_q_m,
            corridor_throughput_veh_per_hr=throughput,
            emergency_travel_time_s=emergency_transit_s,
            spillover_risk_score=spillover_risk,
            composite_network_score=composite_score
        )

    def evaluate_scenario(self, scenario: SimulationScenario) -> DigitalTwinSimulationResponse:
        """Runs baseline and all candidate strategies, compares outcomes, and ranks strategies."""
        candidates = StrategyGenerator.generate_candidates(scenario)
        
        # 1. Simulate Baseline (No Action)
        no_action_strat = next((s for s in candidates if s.strategy_type == StrategyType.NO_ACTION), candidates[0])
        baseline_metrics = self.simulate_strategy(scenario, no_action_strat)
        
        baseline_result = StrategyEvaluationResult(
            strategy=no_action_strat,
            metrics=baseline_metrics,
            delay_reduction_pct=0.0,
            queue_reduction_pct=0.0,
            throughput_gain_pct=0.0,
            emergency_speedup_pct=0.0 if baseline_metrics.emergency_travel_time_s else None,
            rank=len(candidates),
            safety_approved=True,
            evidence=[f"Baseline operation results in {baseline_metrics.average_stopped_time_s:.1f}s delay and {baseline_metrics.max_queue_m:.1f}m queue."]
        )
        
        evaluations: List[StrategyEvaluationResult] = []
        
        # 2. Simulate Each Candidate Strategy
        for strat in candidates:
            m = self.simulate_strategy(scenario, strat)
            
            # Deltas vs Baseline
            delay_red = round(float(((baseline_metrics.average_stopped_time_s - m.average_stopped_time_s) / max(1.0, baseline_metrics.average_stopped_time_s)) * 100.0), 1)
            queue_red = round(float(((baseline_metrics.max_queue_m - m.max_queue_m) / max(1.0, baseline_metrics.max_queue_m)) * 100.0), 1)
            thru_gain = round(float(((m.corridor_throughput_veh_per_hr - baseline_metrics.corridor_throughput_veh_per_hr) / max(1.0, baseline_metrics.corridor_throughput_veh_per_hr)) * 100.0), 1)
            
            em_speedup = None
            if baseline_metrics.emergency_travel_time_s and m.emergency_travel_time_s:
                em_speedup = round(float(((baseline_metrics.emergency_travel_time_s - m.emergency_travel_time_s) / baseline_metrics.emergency_travel_time_s) * 100.0), 1)
                
            evidence = [
                f"Reduces average stopping delay by {delay_red:.1f}% ({baseline_metrics.average_stopped_time_s:.1f}s -> {m.average_stopped_time_s:.1f}s).",
                f"Cuts maximum vehicle queue accumulation by {queue_red:.1f}% ({baseline_metrics.max_queue_m:.1f}m -> {m.max_queue_m:.1f}m).",
                f"Corridor throughput improves by {thru_gain:.1f}% ({baseline_metrics.corridor_throughput_veh_per_hr} -> {m.corridor_throughput_veh_per_hr} veh/hr)."
            ]
            if em_speedup is not None:
                evidence.append(f"Emergency transit accelerated by {em_speedup:.1f}% ({baseline_metrics.emergency_travel_time_s:.0f}s -> {m.emergency_travel_time_s:.0f}s).")

            evaluations.append(StrategyEvaluationResult(
                strategy=strat,
                metrics=m,
                delay_reduction_pct=delay_red,
                queue_reduction_pct=queue_red,
                throughput_gain_pct=thru_gain,
                emergency_speedup_pct=em_speedup,
                rank=1,
                safety_approved=True,
                evidence=evidence
            ))
            
        # Rank strategies by Composite Network Score (or emergency priority if active)
        if scenario.has_emergency_vehicle:
            sorted_evals = sorted(evaluations, key=lambda x: (x.emergency_speedup_pct or 0.0, x.metrics.composite_network_score), reverse=True)
        else:
            sorted_evals = sorted(evaluations, key=lambda x: x.metrics.composite_network_score, reverse=True)
            
        for rank_idx, ev in enumerate(sorted_evals, 1):
            ev.rank = rank_idx
            
        recommended = sorted_evals[0]
        
        summary_evidence = [
            f"Evaluated {len(evaluations)} alternative strategies across a 15-minute Digital Twin simulation horizon.",
            f"Recommended strategy: [{recommended.strategy.name}] achieving {recommended.delay_reduction_pct:.1f}% delay reduction and {recommended.queue_reduction_pct:.1f}% queue reduction.",
            f"Composite Network Score improves from {baseline_metrics.composite_network_score:.1f} to {recommended.metrics.composite_network_score:.1f} / 100."
        ]

        return DigitalTwinSimulationResponse(
            scenario=scenario,
            baseline_result=baseline_result,
            candidate_evaluations=sorted_evals,
            recommended_strategy=recommended,
            summary_evidence=summary_evidence,
            simulation_engine="Deterministic Kinematic Digital Twin Engine v1.0",
            reproducible_seed=self.random_seed
        )

if __name__ == "__main__":
    dt = DigitalTwinEngine()
    scen = ScenarioCatalog.get_scenario(ScenarioType.INCIDENT_LIKE_DISRUPTION)
    res = dt.evaluate_scenario(scen)
    print(f"\n[Digital Twin Evaluation for {scen.name}]:")
    print(f"Recommended Strategy: {res.recommended_strategy.strategy.name} (Rank #{res.recommended_strategy.rank})")
    print(f"Delay Delta: {res.recommended_strategy.delay_reduction_pct}% | Queue Delta: {res.recommended_strategy.queue_reduction_pct}%")
    print("Summary Evidence:", json.dumps(res.summary_evidence, indent=2))
