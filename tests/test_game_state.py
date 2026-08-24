"""
Tests for Game State Machine and Session Lifecycle in NEXUS-TWIN.
"""

import pytest
from backend.game_server.game_engine import GameEngine, GameState, CongestionEvent
from backend.schemas.scenario_models import Strategy

class TestGameStateTransitions:
    def setup_method(self):
        self.engine = GameEngine()

    def test_session_init_and_state(self):
        state = self.engine.start_session("CommanderAlpha", "free_play", "hard")
        assert state.player_name == "CommanderAlpha"
        assert state.difficulty == "hard"
        assert state.session_active is True
        assert state.total_points == 0
        assert state.current_streak == 0

    def test_move_evaluation_and_streak(self):
        self.engine.start_session("CommanderAlpha", "free_play", "normal")
        strat = Strategy("strat_div", "diversion", {"diversion_percent": 30.0})
        traffic = {
            "network_metrics": {"avg_waiting_time_s": 0.28, "mean_queue_length_m": 35.0},
            "junctions": {
                "J1": {"total_queue_m": 20},
                "J2": {"total_queue_m": 45},
                "J3": {"total_queue_m": 15}
            }
        }

        res = self.engine.evaluate_player_move(strat, traffic)
        assert res.points_total > 0
        assert self.engine.state.current_streak >= 1
        assert self.engine.state.decisions_made == 1

    def test_end_session_summary(self):
        self.engine.start_session("CommanderBeta", "challenge", "normal", "challenge_01")
        summary = self.engine.end_session()
        assert summary["player_name"] == "CommanderBeta"
        assert self.engine.state.session_active is False
        assert "total_points" in summary
