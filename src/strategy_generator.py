"""
Strategy Generator module for NEXUS-TWIN.
Generates context-aware candidate strategies based on current network state,
XGBoost congestion predictions, incidents, and active emergency vehicles
per 34_STRATEGY_GENERATION.md specifications.
"""

from typing import List, Dict, Any, Optional
from src.scenario_models import Strategy
from prediction.congestion_predictor import PredictionOutput

class StrategyGenerator:
    def __init__(self, tls_ids: List[str]):
        self.tls_ids = tls_ids

    def generate_candidates(
        self, 
        current_state: Dict[str, Any], 
        prediction_map: Dict[str, PredictionOutput] = None,
        active_incidents: List[Dict[str, Any]] = None,
        has_emergency_vehicle: bool = False
    ) -> List[Strategy]:
        """
        Generates 3-4 context-aware candidate Strategy objects including a 'do_nothing' baseline.
        """
        candidates: List[Strategy] = []

        # 1. Mandatory Control Candidate: Do Nothing
        candidates.append(
            Strategy(
                strategy_id="cand_do_nothing",
                strategy_type="do_nothing",
                parameters={},
                description="Continue current traffic signal and routing control without intervention."
            )
        )

        # Identify target junction from current queue or predictive forecast
        target_junction = self.tls_ids[0]
        max_risk_score = -1.0
        proactive_reason = ""

        if prediction_map:
            for j_id, pred in prediction_map.items():
                if pred.congestion_probability > max_risk_score:
                    max_risk_score = pred.congestion_probability
                    target_junction = j_id
                    if pred.will_congest_5min:
                        proactive_reason = f" (Proactive trigger: XGBoost predicts {pred.predicted_queue_5min_m}m queue in 5 min, prob={pred.congestion_probability*100:.1f}%)"

        if max_risk_score < 0 and "junctions" in current_state:
            for j_id, j_data in current_state["junctions"].items():
                if j_data.get("total_queue_m", 0.0) > max_risk_score:
                    max_risk_score = j_data["total_queue_m"]
                    target_junction = j_id

        # 2. Strategy A: Green Extension
        candidates.append(
            Strategy(
                strategy_id="cand_green_extend_20s",
                strategy_type="green_extend",
                parameters={
                    "junction_id": target_junction,
                    "extension_seconds": 20
                },
                description=f"Extend green signal phase by +20 seconds at {target_junction}{proactive_reason}."
            )
        )

        # 3. Strategy B: Diversion
        candidates.append(
            Strategy(
                strategy_id="cand_diversion_30pct",
                strategy_type="diversion",
                parameters={
                    "from_edge": "J1_to_J2",
                    "alternate_edges": ["J1_to_E1", "E1_to_E2", "E2_to_J2", "J2_to_J3", "J3_to_S"],
                    "diversion_percent": 30
                },
                description="Divert 30% of main corridor flow to East parallel bypass arterial."
            )
        )

        # 4. Strategy C: Dynamic Lane (or Emergency Priority if emergency vehicle present)
        if has_emergency_vehicle:
            candidates.append(
                Strategy(
                    strategy_id="cand_emergency_priority",
                    strategy_type="emergency_priority",
                    parameters={
                        "vehicle_id": "veh_emergency",
                        "corridor_edges": ["N_to_J1", "J1_to_J2", "J2_to_J3", "J3_to_S"]
                    },
                    description="Create continuous priority corridor clearing for approaching emergency vehicle."
                )
            )
        else:
            candidates.append(
                Strategy(
                    strategy_id="cand_dynamic_lane",
                    strategy_type="dynamic_lane",
                    parameters={
                        "edge_id": "J1_to_J2",
                        "lane_index": 2
                    },
                    description="Open dynamic shoulder lane 2 on main corridor edge J1_to_J2."
                )
            )

        return candidates
