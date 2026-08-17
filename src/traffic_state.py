"""
TrafficState module for NEXUS-TWIN.
Queries TraCI every simulation step to extract real-time traffic statistics
including queues, waiting times, network speed, and vehicle counts across junctions.
"""

from typing import Dict, List, Any

class TrafficStateExtractor:
    def __init__(self, tls_ids: List[str]):
        self.tls_ids = tls_ids
        self.controlled_lanes: Dict[str, List[str]] = {}

    def initialize(self, traci_module):
        """Discovers lanes controlled by each traffic light signal."""
        for tls_id in self.tls_ids:
            lanes = list(dict.fromkeys(traci_module.trafficlight.getControlledLanes(tls_id)))
            self.controlled_lanes[tls_id] = lanes

    def extract_state(self, traci_module) -> Dict[str, Any]:
        """Extracts complete snapshot of current network state."""
        active_veh_ids = traci_module.vehicle.getIDList()
        num_active = len(active_veh_ids)
        
        # Calculate vehicle speeds & waiting time
        total_waiting_time = 0.0
        total_speed = 0.0
        max_waiting_time = 0.0
        
        for veh_id in active_veh_ids:
            w_time = traci_module.vehicle.getWaitingTime(veh_id)
            spd = traci_module.vehicle.getSpeed(veh_id)
            total_waiting_time += w_time
            total_speed += spd
            if w_time > max_waiting_time:
                max_waiting_time = w_time

        avg_speed = (total_speed / num_active) if num_active > 0 else 0.0
        avg_waiting = (total_waiting_time / num_active) if num_active > 0 else 0.0

        # Per-junction queue and delay breakdown
        tls_stats = {}
        for tls_id in self.tls_ids:
            lanes = self.controlled_lanes.get(tls_id, [])
            junction_halting = 0
            junction_queue_length_m = 0.0
            lane_stats = {}
            
            for lane_id in lanes:
                halting = traci_module.lane.getLastStepHaltingNumber(lane_id)
                occ = traci_module.lane.getLastStepOccupancy(lane_id)
                queue_m = halting * 7.5  # average vehicle footprint + gap
                junction_halting += halting
                junction_queue_length_m += queue_m
                
                lane_stats[lane_id] = {
                    "halting_vehicles": halting,
                    "occupancy": round(occ, 3),
                    "queue_m": round(queue_m, 1)
                }
            
            tls_stats[tls_id] = {
                "total_halting": junction_halting,
                "total_queue_m": round(junction_queue_length_m, 1),
                "lanes": lane_stats,
                "current_phase": traci_module.trafficlight.getPhase(tls_id)
            }

        return {
            "step": traci_module.simulation.getTime(),
            "active_vehicles": num_active,
            "arrived_vehicles": traci_module.simulation.getArrivedNumber(),
            "departed_vehicles": traci_module.simulation.getDepartedNumber(),
            "avg_speed_mps": round(avg_speed, 2),
            "avg_speed_kmh": round(avg_speed * 3.6, 2),
            "total_waiting_time_s": round(total_waiting_time, 1),
            "avg_waiting_time_s": round(avg_waiting, 2),
            "max_waiting_time_s": round(max_waiting_time, 1),
            "junctions": tls_stats
        }
