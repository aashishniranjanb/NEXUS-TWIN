"""
Domino Effect Intelligence Module.
Translates multi-hop network spillover into sequential human-readable and UI-renderable propagation chains.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.contracts.network_intelligence import (
    DominoChain, DominoStep, SpilloverPrediction
)
from intelligence.network.spillover.spillover_model import CongestionSpilloverModel
from intelligence.network.graph_builder import TrafficNetworkGraph

class DominoEffectEngine:
    def __init__(self, network_graph: Optional[TrafficNetworkGraph] = None):
        self.network_graph = network_graph or TrafficNetworkGraph()
        self.spillover_model = CongestionSpilloverModel(self.network_graph)

    def generate_domino_chain(
        self,
        origin_node_id: int,
        source_queue_m: float = 240.0,
        source_congestion_score: float = 0.82
    ) -> DominoChain:
        """Constructs ordered Domino propagation sequence and cumulative corridor impact."""
        spillover_res = self.spillover_model.predict_spillover(
            origin_node_id, source_queue_m, source_congestion_score, max_depth=3
        )
        
        G = self.network_graph.graph
        origin_name = G.nodes.get(origin_node_id, {}).get("name", f"Junction #{origin_node_id}")
        
        seq_names = [f"J{origin_node_id}"]
        steps: List[DominoStep] = []
        
        cum_delay_s = round(float(source_queue_m * 0.8), 1)
        prev_node = origin_node_id
        prev_name = origin_name
        
        for idx, aff in enumerate(spillover_res.affected_intersections[:4]):
            target_id = aff.intersection_id
            target_name = aff.name
            seq_names.append(f"J{target_id}")
            
            # Determine step transit distance
            step_dist = aff.distance_from_source_m
            step_delay = round(float(aff.projected_queue_m * 0.75), 1)
            cum_delay_s += step_delay
            
            if aff.spillover_risk_score > 0.70:
                sev = "CRITICAL"
            elif aff.spillover_risk_score > 0.45:
                sev = "HIGH"
            elif aff.spillover_risk_score > 0.25:
                sev = "MODERATE"
            else:
                sev = "LOW"
                
            steps.append(DominoStep(
                step_index=idx + 1,
                from_node=prev_node,
                from_name=prev_name,
                to_node=target_id,
                to_name=target_name,
                transit_distance_m=step_dist,
                cumulative_delay_s=round(cum_delay_s, 1),
                estimated_time_to_impact_min=aff.estimated_arrival_minutes,
                impact_severity=sev
            ))
            prev_node = target_id
            prev_name = target_name
            
        # Calculate exposure score
        exposure = min(1.0, (source_congestion_score * 0.5) + (len(steps) * 0.12) + (cum_delay_s / 600.0) * 0.38)
        exposure = round(float(exposure), 3)
        
        if exposure > 0.75:
            urgency = "CRITICAL_IMMEDIATE_INTERVENTION"
        elif exposure > 0.50:
            urgency = "HIGH_PRIORITY_DISPATCH"
        elif exposure > 0.30:
            urgency = "MODERATE_MONITOR"
        else:
            urgency = "LOW_STABLE"
            
        corridor_str = " -> ".join(seq_names)
        
        return DominoChain(
            chain_id=f"DOMINO_{origin_node_id}_{self.network_graph.city.upper()}",
            corridor_name=f"{origin_name} Arterial Corridor",
            critical_origin_node=origin_node_id,
            propagation_sequence=seq_names,
            steps=steps,
            network_exposure_score=exposure,
            estimated_total_corridor_delay_s=cum_delay_s,
            intervention_urgency=urgency
        )

if __name__ == "__main__":
    domino = DominoEffectEngine()
    chain = domino.generate_domino_chain(origin_node_id=0)
    print("Domino Chain Output:", chain.model_dump_json(indent=2))
