"""
Digital Twin Scenario Engine for NEXUS-TWIN.
Executes the Snapshot -> Apply Strategy -> Simulate Horizon -> Collect Metrics -> Restore loop
to evaluate candidate interventions in parallel futures before selecting an optimal strategy.
"""

import os
import sys
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.scenario_models import Strategy, ScenarioResult
from src.traffic_state import TrafficStateExtractor
from src.metrics_collector import MetricsCollector

class ScenarioEngine:
    def __init__(self, traci_module, tls_ids: List[str], default_horizon_seconds: int = 180):
        self.traci = traci_module
        self.tls_ids = tls_ids
        self.default_horizon_seconds = default_horizon_seconds
        self.state_extractor = TrafficStateExtractor(tls_ids)
        self.state_extractor.initialize(traci_module)

    def snapshot_state(self, snapshot_path: str):
        """Snapshots the exact current SUMO simulation state to disk/memory."""
        self.traci.simulation.saveState(snapshot_path)

    def restore_state(self, snapshot_path: str):
        """Restores the exact SUMO simulation state from a snapshot."""
        self.traci.simulation.loadState(snapshot_path)

    def apply_strategy(self, strategy: Strategy):
        """Applies a candidate intervention via TraCI APIs."""
        stype = strategy.strategy_type
        params = strategy.parameters

        if stype == "do_nothing":
            # Control candidate: continue current control unchanged
            return

        elif stype == "green_extend":
            # Parameters: junction_id, extension_seconds
            junction_id = params.get("junction_id", self.tls_ids[0])
            ext_seconds = params.get("extension_seconds", 20)
            
            # Identify current phase
            curr_phase = self.traci.trafficlight.getPhase(junction_id)
            # If current phase is green (Phase 0 or Phase 2), set phase duration extension
            if curr_phase % 2 == 0:
                # Set phase duration to extend green phase
                self.traci.trafficlight.setPhaseDuration(junction_id, float(ext_seconds))

        elif stype == "diversion":
            # Parameters: from_edge, alternate_edges, diversion_percent
            from_edge = params.get("from_edge", "J1_to_J2")
            alt_edges = params.get("alternate_edges", ["J1_to_E1", "E1_to_E2", "E2_to_J2", "J2_to_J3", "J3_to_S"])
            diversion_pct = params.get("diversion_percent", 30)
            
            # Find vehicles targeting from_edge or heading along default route
            active_vehs = self.traci.vehicle.getIDList()
            eligible_vehs = []
            for veh_id in active_vehs:
                try:
                    route = self.traci.vehicle.getRoute(veh_id)
                    if from_edge in route:
                        eligible_vehs.append(veh_id)
                except Exception:
                    pass

            # Reroute diversion_pct of eligible vehicles
            num_to_reroute = int(len(eligible_vehs) * (diversion_pct / 100.0))
            for veh_id in eligible_vehs[:num_to_reroute]:
                try:
                    curr_road = self.traci.vehicle.getRoadID(veh_id)
                    if curr_road and not curr_road.startswith(":"):
                        if curr_road in alt_edges:
                            idx = alt_edges.index(curr_road)
                            new_route = alt_edges[idx:]
                            self.traci.vehicle.setRoute(veh_id, new_route)
                        elif curr_road == "N_to_J1":
                            new_route = ["N_to_J1"] + alt_edges
                            self.traci.vehicle.setRoute(veh_id, new_route)
                except Exception:
                    pass

        elif stype == "dynamic_lane":
            # Parameters: edge_id, lane_index
            edge_id = params.get("edge_id", "J1_to_J2")
            lane_idx = params.get("lane_index", 2)
            lane_id = f"{edge_id}_{lane_idx}"
            
            try:
                # Open dynamic shoulder lane (lane 2) to all standard vehicle classes
                self.traci.lane.setAllowed(lane_id, ["passenger", "bus", "truck", "delivery", "emergency"])
            except Exception:
                pass

        elif stype == "emergency_priority":
            # Parameters: vehicle_id, corridor_edges
            emergency_id = params.get("vehicle_id", "veh_emergency")
            corridor_edges = params.get("corridor_edges", ["N_to_J1", "J1_to_J2", "J2_to_J3", "J3_to_S"])

            # Force green light at all corridor junctions if emergency vehicle is approaching
            for tls_id in self.tls_ids:
                try:
                    # Phase 0 is North-South Green Phase
                    self.traci.trafficlight.setPhase(tls_id, 0)
                    self.traci.trafficlight.setPhaseDuration(tls_id, 120.0)
                except Exception:
                    pass

            if emergency_id in self.traci.vehicle.getIDList():
                try:
                    self.traci.vehicle.setSpeed(emergency_id, 20.0)  # Priority speed
                except Exception:
                    pass

    def simulate_horizon(self, horizon_seconds: int) -> Dict[str, Any]:
        """Simulates forward horizon_seconds and collects network-wide metrics."""
        start_time = self.traci.simulation.getTime()
        end_target = start_time + horizon_seconds

        metrics = MetricsCollector(controller_name="scenario_eval")
        
        total_co2_mg = 0.0
        emergency_start_time = None
        emergency_end_time = None

        veh_depart_times = {}

        while self.traci.simulation.getTime() < end_target and self.traci.simulation.getMinExpectedNumber() > 0:
            self.traci.simulationStep()
            step_time = self.traci.simulation.getTime()

            # Record vehicle departures & arrivals for travel time
            for veh_id in self.traci.simulation.getDepartedIDList():
                veh_depart_times[veh_id] = step_time
                if veh_id == "veh_emergency":
                    emergency_start_time = step_time

            for veh_id in self.traci.simulation.getArrivedIDList():
                if veh_id in veh_depart_times:
                    metrics.record_completed_trip(step_time - veh_depart_times[veh_id])
                if veh_id == "veh_emergency":
                    emergency_end_time = step_time

            # Extract snapshot state & measure CO2 emissions
            state = self.state_extractor.extract_state(self.traci)
            metrics.record_step(state)

            # Sum active vehicle CO2 emissions
            for veh_id in self.traci.vehicle.getIDList():
                try:
                    total_co2_mg += self.traci.vehicle.getCO2Emission(veh_id)
                except Exception:
                    pass

        summary = metrics.compute_summary()
        
        # Calculate emergency vehicle delay if present
        emergency_delay_s = None
        if emergency_start_time is not None:
            if emergency_end_time is not None:
                emergency_delay_s = round(emergency_end_time - emergency_start_time, 1)
            else:
                # Still running: calculate accumulated delay so far
                emergency_delay_s = round(self.traci.simulation.getTime() - emergency_start_time, 1)

        # Per-junction queue breakdown from last state
        last_step = metrics.step_history[-1] if metrics.step_history else {}
        per_junction = {}
        if "junctions" in last_step:
            for tls_id, data in last_step["junctions"].items():
                per_junction[tls_id] = {
                    "total_halting": data["total_halting"],
                    "queue_m": data["total_queue_m"]
                }

        return {
            "start_time": start_time,
            "end_time": self.traci.simulation.getTime(),
            "predicted_delay_s": summary.get("avg_waiting_time_s", 0.0),
            "predicted_queue_m": summary.get("mean_queue_length_m", 0.0),
            "predicted_throughput": summary.get("throughput_vehicles", 0),
            "predicted_emissions_kg": round(total_co2_mg / 1e6, 3),  # mg to kg
            "predicted_emergency_delay_s": emergency_delay_s,
            "avg_speed_kmh": summary.get("avg_speed_kmh", 0.0),
            "per_junction": per_junction
        }

    def evaluate_strategy(self, strategy: Strategy, horizon_seconds: Optional[int] = None) -> ScenarioResult:
        """
        Evaluates a single strategy candidate by taking snapshot, applying strategy,
        simulating horizon, and restoring exact state.
        """
        if horizon_seconds is None:
            horizon_seconds = self.default_horizon_seconds

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            snap_file = tmp.name

        try:
            # 1. Snapshot Twin state
            self.snapshot_state(snap_file)
            start_time = self.traci.simulation.getTime()

            # 2. Apply candidate action
            self.apply_strategy(strategy)

            # 3 & 4. Simulate horizon and collect metrics
            res = self.simulate_horizon(horizon_seconds)

            return ScenarioResult(
                strategy_id=strategy.strategy_id,
                strategy_type=strategy.strategy_type,
                parameters=strategy.parameters,
                simulation_start_time=start_time,
                simulation_end_time=res["end_time"],
                horizon_seconds=float(horizon_seconds),
                predicted_delay_s=res["predicted_delay_s"],
                predicted_queue_m=res["predicted_queue_m"],
                predicted_throughput=res["predicted_throughput"],
                predicted_emissions=res["predicted_emissions_kg"],
                predicted_emergency_delay_s=res["predicted_emergency_delay_s"],
                per_junction_metrics=res["per_junction"],
                network_metrics={
                    "avg_speed_kmh": res["avg_speed_kmh"],
                    "predicted_emissions_kg": res["predicted_emissions_kg"]
                },
                success=True
            )
        except Exception as e:
            return ScenarioResult(
                strategy_id=strategy.strategy_id,
                strategy_type=strategy.strategy_type,
                parameters=strategy.parameters,
                simulation_start_time=0.0,
                simulation_end_time=0.0,
                horizon_seconds=float(horizon_seconds),
                predicted_delay_s=999.0,
                predicted_queue_m=999.0,
                predicted_throughput=0,
                success=False,
                error_message=str(e)
            )
        finally:
            # 5. Restore Twin to pre-candidate snapshot
            if os.path.exists(snap_file):
                try:
                    self.restore_state(snap_file)
                finally:
                    try:
                        os.remove(snap_file)
                    except Exception:
                        pass

    def evaluate_candidates(self, candidates: List[Strategy], horizon_seconds: Optional[int] = None) -> List[ScenarioResult]:
        """Evaluates multiple candidate strategies sequentially from identical snapshot states."""
        results = []
        for strategy in candidates:
            res = self.evaluate_strategy(strategy, horizon_seconds=horizon_seconds)
            results.append(res)
        return results
