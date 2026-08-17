"""
Decision Server REST API for NEXUS-TWIN.
Provides HTTP API endpoints serving real-time traffic state, candidate scenario evaluations,
dynamic confidence scores, XAI explanations, emergency preemption overrides, and decision history per Phase 6 specifications.
"""

import json
import time
import math
import http.server
import socketserver
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.scenario_models import Strategy, ScenarioResult
from src.strategy_generator import StrategyGenerator
from src.strategy_optimizer import StrategyOptimizer
from src.explainable_ai import ExplainableAIEngine

# Simulated / Live state provider for Web UI demo
class SystemStateManager:
    def __init__(self):
        self.start_time = time.time()
        self.tls_ids = ["J1", "J2", "J3"]
        self.generator = StrategyGenerator(self.tls_ids)
        self.optimizer = StrategyOptimizer()
        self.xai_engine = ExplainableAIEngine()
        self.history: List[Dict[str, Any]] = []

    def get_live_state(self) -> Dict[str, Any]:
        """Generates realistic live traffic state telemetry for J1, J2, J3."""
        elapsed = time.time() - self.start_time
        phase_j1 = int((elapsed // 30) % 4)
        phase_j2 = int((elapsed // 25) % 4)
        phase_j3 = int((elapsed // 35) % 4)

        base_q1 = 25.0 + 15.0 * math.sin(elapsed / 10.0)
        base_q2 = 35.0 + 20.0 * math.sin(elapsed / 12.0 + 1.0)
        base_q3 = 18.0 + 10.0 * math.sin(elapsed / 8.0 + 2.0)

        return {
            "timestamp": round(elapsed, 1),
            "network_metrics": {
                "active_vehicles": int(120 + 30 * math.sin(elapsed / 15.0)),
                "avg_waiting_time_s": round(0.24 + 0.05 * math.sin(elapsed / 20.0), 2),
                "avg_speed_kmh": round(39.5 + 1.2 * math.cos(elapsed / 18.0), 1),
                "mean_queue_length_m": round((base_q1 + base_q2 + base_q3) / 3.0, 1),
                "total_throughput": int(450 + elapsed * 0.5)
            },
            "junctions": {
                "J1": {
                    "phase": phase_j1,
                    "phase_name": "N-S Green" if phase_j1 % 2 == 0 else "E-W Green",
                    "total_queue_m": round(max(5.0, base_q1), 1),
                    "avg_waiting_time_s": round(0.22 + 0.04 * math.sin(elapsed / 10.0), 2),
                    "vehicle_count": int(15 + 5 * math.sin(elapsed / 7.0))
                },
                "J2": {
                    "phase": phase_j2,
                    "phase_name": "E-W Green" if phase_j2 % 2 == 0 else "N-S Green",
                    "total_queue_m": round(max(8.0, base_q2), 1),
                    "avg_waiting_time_s": round(0.28 + 0.06 * math.sin(elapsed / 11.0), 2),
                    "vehicle_count": int(22 + 8 * math.sin(elapsed / 9.0))
                },
                "J3": {
                    "phase": phase_j3,
                    "phase_name": "N-S Green" if phase_j3 % 2 == 0 else "E-W Green",
                    "total_queue_m": round(max(4.0, base_q3), 1),
                    "avg_waiting_time_s": round(0.19 + 0.03 * math.sin(elapsed / 8.0), 2),
                    "vehicle_count": int(12 + 4 * math.sin(elapsed / 6.0))
                }
            }
        }

    def evaluate_whatif(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates what-if candidate strategies and computes dynamic confidence + XAI."""
        horizon = int(payload.get("horizon_seconds", 180))
        custom_junction = payload.get("junction_id", "J2")
        custom_type = payload.get("strategy_type", "green_extend")
        ext_seconds = float(payload.get("extension_seconds", 20.0))

        state = self.get_live_state()

        # Build candidate set
        cands = [
            Strategy("do_nothing", "do_nothing", {}, "Do Nothing (Baseline)"),
            Strategy("green_extend_j2", "green_extend", {"junction_id": custom_junction, "extension_seconds": ext_seconds}, f"Green Extend {ext_seconds}s at {custom_junction}"),
            Strategy("diversion_j2", "diversion", {"from_edge": "J1_to_J2", "diversion_percent": 25.0}, "Route Diversion via E1/E2"),
            Strategy("dynamic_lane_j2", "dynamic_lane", {"junction_id": custom_junction, "reassigned_lane": 1}, f"Dynamic Lane Reassignment at {custom_junction}")
        ]

        # Generate simulated evaluation results
        now = time.time()
        results: List[ScenarioResult] = []

        # Baseline Do Nothing
        res_dn = ScenarioResult(
            strategy_id="do_nothing",
            strategy_type="do_nothing",
            parameters={},
            simulation_start_time=0.0,
            simulation_end_time=float(horizon),
            horizon_seconds=float(horizon),
            predicted_delay_s=0.25,
            predicted_queue_m=state["network_metrics"]["mean_queue_length_m"],
            predicted_throughput=1001,
            predicted_emissions=14.2
        )
        results.append(res_dn)

        # Selected Custom Candidate
        res_custom = ScenarioResult(
            strategy_id=f"{custom_type}_{custom_junction}",
            strategy_type=custom_type,
            parameters={"junction_id": custom_junction, "extension_seconds": ext_seconds},
            simulation_start_time=0.0,
            simulation_end_time=float(horizon),
            horizon_seconds=float(horizon),
            predicted_delay_s=max(0.15, res_dn.predicted_delay_s - 0.04),
            predicted_queue_m=max(15.0, res_dn.predicted_queue_m - 4.5),
            predicted_throughput=1008,
            predicted_emissions=13.1
        )
        results.append(res_custom)

        # Diversion Candidate
        res_div = ScenarioResult(
            strategy_id="diversion_j2",
            strategy_type="diversion",
            parameters={"from_edge": "J1_to_J2", "diversion_percent": 25.0},
            simulation_start_time=0.0,
            simulation_end_time=float(horizon),
            horizon_seconds=float(horizon),
            predicted_delay_s=0.23,
            predicted_queue_m=res_dn.predicted_queue_m - 2.1,
            predicted_throughput=1005,
            predicted_emissions=13.8
        )
        results.append(res_div)

        # Dynamic Lane Candidate
        res_lane = ScenarioResult(
            strategy_id="dynamic_lane_j2",
            strategy_type="dynamic_lane",
            parameters={"junction_id": custom_junction, "reassigned_lane": 1},
            simulation_start_time=0.0,
            simulation_end_time=float(horizon),
            horizon_seconds=float(horizon),
            predicted_delay_s=0.26,
            predicted_queue_m=res_dn.predicted_queue_m + 1.2,
            predicted_throughput=998,
            predicted_emissions=14.5
        )
        results.append(res_lane)

        # Score candidates
        scored_results: List[ScenarioResult] = []
        for r in results:
            score = self.optimizer.score_candidate(r, res_dn)
            r.score = score
            scored_results.append(r)

        best_strategy, best_score = self.optimizer.select_best_strategy(scored_results)

        # Generate XAI Explanation with dynamic confidence calibration
        explanation = self.xai_engine.explain(best_strategy, scored_results)

        # Format output
        response_data = {
            "timestamp": now,
            "horizon_seconds": horizon,
            "recommended_strategy": best_strategy.to_dict(),
            "recommended_score": round(best_score, 3),
            "explanation": explanation.to_dict(),
            "candidates": [r.to_dict() for r in scored_results]
        }

        # Save to history
        self.history.append(response_data)
        if len(self.history) > 50:
            self.history.pop(0)

        return response_data

    def trigger_emergency_preemption(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Triggers emergency vehicle priority preemption for a specified corridor."""
        corridor = payload.get("corridor", "J1-J2-J3")
        vehicle_id = payload.get("vehicle_id", "AMBULANCE_01")
        junction_id = payload.get("junction_id", "J2")

        res_emergency = ScenarioResult(
            strategy_id="emergency_priority_override",
            strategy_type="emergency_priority",
            parameters={"vehicle_id": vehicle_id, "corridor": corridor, "junction_id": junction_id},
            simulation_start_time=0.0,
            simulation_end_time=60.0,
            horizon_seconds=60.0,
            predicted_delay_s=0.05,
            predicted_queue_m=12.0,
            predicted_throughput=1020,
            predicted_emergency_delay_s=0.0
        )

        return {
            "status": "PREEMPTION_ACTIVE",
            "vehicle_id": vehicle_id,
            "corridor": corridor,
            "target_junction": junction_id,
            "preemption_phase": "GREEN_CORRIDOR",
            "estimated_clearance_time_s": 14.5,
            "result": res_emergency.to_dict(),
            "explanation": {
                "action": f"DISPATCH EMERGENCY PREEMPTION: Clear Corridor {corridor} at {junction_id}",
                "reason": f"Emergency vehicle {vehicle_id} detected. Signals forced to green along Corridor {corridor}.",
                "expected_impact": "Emergency travel delay reduced to 0.0s; normal queues cleared.",
                "confidence": "98% (Emergency Preemption Override Override)"
            }
        }

state_manager = SystemStateManager()

class DecisionRequestHandler(http.server.BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            data = {
                "status": "ONLINE",
                "system": "NEXUS-TWIN Digital Twin Decision Engine",
                "version": "1.0.0",
                "simulation": "SUMO v1.27.1",
                "network": "3-Junction Corridor (J1/J2/J3)",
                "predictor_accuracy": "81.03%"
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))

        elif path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            state = state_manager.get_live_state()
            self.wfile.write(json.dumps(state).encode("utf-8"))

        elif path == "/api/history":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(state_manager.history).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            payload = {}

        if path == "/api/evaluate":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            res = state_manager.evaluate_whatif(payload)
            self.wfile.write(json.dumps(res).encode("utf-8"))

        elif path == "/api/emergency":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            res = state_manager.trigger_emergency_preemption(payload)
            self.wfile.write(json.dumps(res).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

def run_server(port: int = 8000):
    server_address = ("", port)
    httpd = socketserver.TCPServer(server_address, DecisionRequestHandler)
    print(f"==================================================")
    print(f"  NEXUS-TWIN Decision Server Running on Port {port} ")
    print(f"  API URL: http://localhost:{port}/api/status      ")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    port_arg = 8000
    if len(sys.argv) > 1:
        port_arg = int(sys.argv[1])
    run_server(port_arg)
