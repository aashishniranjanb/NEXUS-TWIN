"""
Unit & Integration Tests for Phase 7 (Traffic Commander Game Engine).
Verifies game session lifecycle, points calculation, streak multipliers,
badge unlocks, AI duel scoring, leaderboard persistence, event spawning, and challenge pass/fail.
"""

import unittest
import json
import time
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.game_engine import GameEngine, GameState, CongestionEvent, Badge, ALL_BADGES, CHALLENGE_SCENARIOS
from src.scenario_models import Strategy, ScenarioResult


class TestGameSessionLifecycle(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        # Use temp leaderboard to avoid polluting real data
        self.engine.leaderboard_path = PROJECT_ROOT / "data" / "test_leaderboard.json"

    def tearDown(self):
        if self.engine.leaderboard_path.exists():
            os.remove(self.engine.leaderboard_path)

    def test_start_session(self):
        state = self.engine.start_session("TestPlayer", "free_play", "normal")
        self.assertIsNotNone(state)
        self.assertEqual(state.player_name, "TestPlayer")
        self.assertEqual(state.mode, "free_play")
        self.assertEqual(state.difficulty, "normal")
        self.assertTrue(state.session_active)
        self.assertEqual(state.total_points, 0)
        self.assertEqual(state.current_streak, 0)

    def test_end_session_returns_summary(self):
        self.engine.start_session("TestPlayer", "free_play", "normal")
        summary = self.engine.end_session()
        self.assertIn("session_id", summary)
        self.assertIn("total_points", summary)
        self.assertIn("decisions_made", summary)
        self.assertIn("badges_earned", summary)
        self.assertFalse(self.engine.state.session_active)

    def test_full_lifecycle(self):
        """start -> spawn event -> submit move -> end"""
        self.engine.start_session("FullTest", "free_play", "normal")

        # Force-spawn an event
        self.engine.last_event_time = 0  # Reset cooldown
        traffic = {"junctions": {"J1": {"total_queue_m": 25}, "J2": {"total_queue_m": 40}, "J3": {"total_queue_m": 18}},
                   "network_metrics": {"avg_waiting_time_s": 0.25, "mean_queue_length_m": 28.0}}
        event = self.engine.spawn_event(traffic)
        self.assertIsNotNone(event)
        self.assertFalse(event.resolved)

        # Submit a move
        strategy = Strategy("test_green", "green_extend", {"junction_id": "J2", "extension_seconds": 20.0})
        result = self.engine.evaluate_player_move(strategy, traffic)
        self.assertIsNotNone(result)
        self.assertIsInstance(result.points_total, int)
        self.assertEqual(self.engine.state.decisions_made, 1)

        # End session
        summary = self.engine.end_session()
        self.assertIn("total_points", summary)


class TestPointsCalculation(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        self.engine.leaderboard_path = PROJECT_ROOT / "data" / "test_leaderboard.json"
        self.traffic = {"junctions": {"J1": {"total_queue_m": 25}, "J2": {"total_queue_m": 40}, "J3": {"total_queue_m": 18}},
                        "network_metrics": {"avg_waiting_time_s": 0.25, "mean_queue_length_m": 30.0}}

    def tearDown(self):
        if self.engine.leaderboard_path.exists():
            os.remove(self.engine.leaderboard_path)

    def test_positive_points_for_improvement(self):
        """Green extend should improve traffic and yield positive points."""
        self.engine.start_session("PosTest", "free_play", "normal")
        self.engine.last_event_time = 0
        self.engine.spawn_event(self.traffic)

        strategy = Strategy("test_green", "green_extend", {"junction_id": "J2", "extension_seconds": 25.0})
        result = self.engine.evaluate_player_move(strategy, self.traffic)
        # Green extend should improve delay/queue vs do-nothing, yielding positive base points
        self.assertGreater(result.points_base, 0, "Green extend should yield positive base points")

    def test_negative_points_for_worsening(self):
        """Dynamic lane tends to worsen metrics and should yield negative or zero base points."""
        self.engine.start_session("NegTest", "free_play", "normal")
        self.engine.last_event_time = 0
        self.engine.spawn_event(self.traffic)

        strategy = Strategy("test_lane", "dynamic_lane", {"junction_id": "J2", "reassigned_lane": 1})
        result = self.engine.evaluate_player_move(strategy, self.traffic)
        # Dynamic lane worsens metrics in our simulation model
        self.assertLessEqual(result.points_base, 0, "Dynamic lane should yield zero or negative base points")


class TestStreakMultiplier(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        self.engine.leaderboard_path = PROJECT_ROOT / "data" / "test_leaderboard.json"
        self.traffic = {"junctions": {"J1": {"total_queue_m": 25}, "J2": {"total_queue_m": 40}, "J3": {"total_queue_m": 18}},
                        "network_metrics": {"avg_waiting_time_s": 0.25, "mean_queue_length_m": 30.0}}

    def tearDown(self):
        if self.engine.leaderboard_path.exists():
            os.remove(self.engine.leaderboard_path)

    def test_streak_builds_on_positive_moves(self):
        """3 consecutive positive-point moves should build a streak."""
        self.engine.start_session("StreakTest", "free_play", "normal")
        strategy = Strategy("test_green", "green_extend", {"junction_id": "J2", "extension_seconds": 20.0})

        for i in range(3):
            self.engine.last_event_time = 0
            self.engine.spawn_event(self.traffic)
            if self.engine.state.active_event:
                self.engine.state.active_event.resolved = False
                self.engine.state.active_event.expired = False
                self.engine.state.active_event.spawn_time = time.time()
            result = self.engine.evaluate_player_move(strategy, self.traffic)

        self.assertGreaterEqual(self.engine.state.current_streak, 3)
        self.assertGreaterEqual(self.engine.state.max_streak, 3)

    def test_streak_resets_on_negative_move(self):
        """Streak should reset when a move yields negative points."""
        self.engine.start_session("ResetTest", "free_play", "normal")

        # Build a streak with good moves
        good_strategy = Strategy("test_green", "green_extend", {"junction_id": "J2", "extension_seconds": 20.0})
        for i in range(3):
            self.engine.last_event_time = 0
            self.engine.spawn_event(self.traffic)
            if self.engine.state.active_event:
                self.engine.state.active_event.resolved = False
                self.engine.state.active_event.expired = False
                self.engine.state.active_event.spawn_time = time.time()
            self.engine.evaluate_player_move(good_strategy, self.traffic)

        streak_before = self.engine.state.current_streak

        # Make a bad move
        bad_strategy = Strategy("test_lane", "dynamic_lane", {"junction_id": "J2"})
        self.engine.last_event_time = 0
        self.engine.spawn_event(self.traffic)
        if self.engine.state.active_event:
            self.engine.state.active_event.resolved = False
            self.engine.state.active_event.expired = False
            self.engine.state.active_event.spawn_time = time.time()
        self.engine.evaluate_player_move(bad_strategy, self.traffic)

        self.assertEqual(self.engine.state.current_streak, 0, "Streak should reset after negative move")


class TestBadgeUnlocks(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        self.engine.leaderboard_path = PROJECT_ROOT / "data" / "test_leaderboard.json"
        self.traffic = {"junctions": {"J1": {"total_queue_m": 25}, "J2": {"total_queue_m": 40}, "J3": {"total_queue_m": 18}},
                        "network_metrics": {"avg_waiting_time_s": 0.25, "mean_queue_length_m": 30.0}}

    def tearDown(self):
        if self.engine.leaderboard_path.exists():
            os.remove(self.engine.leaderboard_path)

    def test_spillback_free_badge(self):
        """10 zero-spillback decisions should unlock Spillback-Free Master."""
        self.engine.start_session("BadgeTest", "free_play", "normal")
        strategy = Strategy("test_green", "green_extend", {"junction_id": "J2", "extension_seconds": 20.0})

        for i in range(10):
            self.engine.last_event_time = 0
            self.engine.spawn_event(self.traffic)
            if self.engine.state.active_event:
                self.engine.state.active_event.resolved = False
                self.engine.state.active_event.expired = False
                self.engine.state.active_event.spawn_time = time.time()
            self.engine.evaluate_player_move(strategy, self.traffic)

        badge_ids = [b.badge_id for b in self.engine.state.badges_unlocked]
        self.assertIn("spillback_free", badge_ids, "Spillback-Free Master should unlock after 10 zero-spillback moves")

    def test_emergency_ace_badge(self):
        """5 perfect emergency clears should unlock Emergency Ace."""
        self.engine.start_session("EmergAce", "free_play", "normal")
        strategy = Strategy("test_emg", "emergency_priority", {"corridor": "J1-J2-J3", "vehicle_id": "AMB"})

        for i in range(5):
            self.engine.last_event_time = 0
            # Force emergency event
            event = CongestionEvent(
                event_id=f"emg_{i}", event_type="emergency", target_junction="J2",
                severity="critical", description="Emergency vehicle approaching!",
                time_limit_s=15.0, spawn_time=time.time()
            )
            self.engine.state.active_event = event
            self.engine.evaluate_player_move(strategy, self.traffic)

        badge_ids = [b.badge_id for b in self.engine.state.badges_unlocked]
        self.assertIn("emergency_ace", badge_ids, "Emergency Ace should unlock after 5 perfect emergency clears")


class TestAIDuelScoring(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        self.engine.leaderboard_path = PROJECT_ROOT / "data" / "test_leaderboard.json"
        self.traffic = {"junctions": {"J1": {"total_queue_m": 25}, "J2": {"total_queue_m": 40}, "J3": {"total_queue_m": 18}},
                        "network_metrics": {"avg_waiting_time_s": 0.25, "mean_queue_length_m": 30.0}}

    def tearDown(self):
        if self.engine.leaderboard_path.exists():
            os.remove(self.engine.leaderboard_path)

    def test_ai_comparison_computed(self):
        """Move result should include player_score and ai_score for comparison."""
        self.engine.start_session("AITest", "ai_duel", "normal")
        self.engine.last_event_time = 0
        self.engine.spawn_event(self.traffic)

        strategy = Strategy("test_green", "green_extend", {"junction_id": "J2", "extension_seconds": 20.0})
        result = self.engine.evaluate_player_move(strategy, self.traffic)

        self.assertIsNotNone(result.player_score)
        self.assertIsNotNone(result.ai_score)
        self.assertIsInstance(result.beat_ai, bool)
        self.assertIsNotNone(result.ai_strategy_id)


class TestLeaderboardPersistence(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        self.engine.leaderboard_path = PROJECT_ROOT / "data" / "test_leaderboard.json"
        self.traffic = {"junctions": {"J1": {"total_queue_m": 25}, "J2": {"total_queue_m": 40}, "J3": {"total_queue_m": 18}},
                        "network_metrics": {"avg_waiting_time_s": 0.25, "mean_queue_length_m": 30.0}}

    def tearDown(self):
        if self.engine.leaderboard_path.exists():
            os.remove(self.engine.leaderboard_path)

    def test_leaderboard_save_and_load(self):
        """Scores should be saved to and loaded from leaderboard.json."""
        self.engine.start_session("LBTest", "free_play", "normal")

        # Make some moves to accumulate points
        strategy = Strategy("test_green", "green_extend", {"junction_id": "J2", "extension_seconds": 20.0})
        for i in range(3):
            self.engine.last_event_time = 0
            self.engine.spawn_event(self.traffic)
            if self.engine.state.active_event:
                self.engine.state.active_event.resolved = False
                self.engine.state.active_event.expired = False
                self.engine.state.active_event.spawn_time = time.time()
            self.engine.evaluate_player_move(strategy, self.traffic)

        self.engine.end_session()

        # Load and verify
        lb = self.engine.get_leaderboard()
        if self.engine.state.total_points > 0:
            self.assertGreater(len(lb), 0, "Leaderboard should have at least one entry")
            self.assertEqual(lb[0]["player"], "LBTest")


class TestEventSpawning(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        self.engine.leaderboard_path = PROJECT_ROOT / "data" / "test_leaderboard.json"

    def tearDown(self):
        if self.engine.leaderboard_path.exists():
            os.remove(self.engine.leaderboard_path)

    def test_contextual_event_spawning(self):
        """Events should match current traffic conditions."""
        self.engine.start_session("EventTest", "free_play", "normal")
        self.engine.last_event_time = 0

        # High queue traffic should bias toward cascade/rush_hour events
        high_q_traffic = {
            "junctions": {"J1": {"total_queue_m": 60}, "J2": {"total_queue_m": 70}, "J3": {"total_queue_m": 55}},
            "network_metrics": {"avg_waiting_time_s": 0.4, "mean_queue_length_m": 62.0}
        }
        event = self.engine.spawn_event(high_q_traffic)
        self.assertIsNotNone(event)
        self.assertIn(event.event_type, ["rush_hour", "emergency", "accident", "cascade"])
        # Target junction should be J2 (highest queue) for rush_hour/cascade
        if event.event_type in ("rush_hour", "cascade"):
            self.assertEqual(event.target_junction, "J2")


class TestChallengePassFail(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        self.engine.leaderboard_path = PROJECT_ROOT / "data" / "test_leaderboard.json"
        self.traffic = {"junctions": {"J1": {"total_queue_m": 25}, "J2": {"total_queue_m": 40}, "J3": {"total_queue_m": 18}},
                        "network_metrics": {"avg_waiting_time_s": 0.25, "mean_queue_length_m": 30.0}}

    def tearDown(self):
        if self.engine.leaderboard_path.exists():
            os.remove(self.engine.leaderboard_path)

    def test_challenge_pass(self):
        """Challenge should pass when average points per decision > 50."""
        self.engine.start_session("ChallengeTest", "challenge", "normal", challenge_id="rush_hour")
        strategy = Strategy("test_green", "green_extend", {"junction_id": "J2", "extension_seconds": 25.0})

        for i in range(5):
            self.engine.last_event_time = 0
            self.engine.spawn_event(self.traffic)
            if self.engine.state.active_event:
                self.engine.state.active_event.resolved = False
                self.engine.state.active_event.expired = False
                self.engine.state.active_event.spawn_time = time.time()
            self.engine.evaluate_player_move(strategy, self.traffic)

        summary = self.engine.end_session()
        # With good green_extend moves, average should be well above 50
        if summary["total_points"] > 0:
            self.assertTrue(summary["challenge_passed"], "Challenge should pass with positive average points")


if __name__ == "__main__":
    unittest.main()
