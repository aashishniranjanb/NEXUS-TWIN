"""
Game Engine for NEXUS-TWIN Traffic Commander.
Manages game sessions, congestion event spawning, player move evaluation,
points/streak/multiplier calculation, badge unlocking, and leaderboard persistence.
"""

import json
import time
import math
import random
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from backend.schemas.scenario_models import Strategy, ScenarioResult
from intelligence.strategy.strategy_optimizer import StrategyOptimizer


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class Badge:
    badge_id: str
    name: str
    icon: str
    description: str
    tier: str  # "bronze", "silver", "gold", "platinum"
    unlocked: bool = False
    unlock_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "badge_id": self.badge_id,
            "name": self.name,
            "icon": self.icon,
            "description": self.description,
            "tier": self.tier,
            "unlocked": self.unlocked,
            "unlock_time": self.unlock_time
        }


@dataclass
class CongestionEvent:
    event_id: str
    event_type: str  # "rush_hour", "emergency", "accident", "cascade"
    target_junction: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    time_limit_s: float = 30.0
    spawn_time: float = 0.0
    resolved: bool = False
    expired: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "target_junction": self.target_junction,
            "severity": self.severity,
            "description": self.description,
            "time_limit_s": self.time_limit_s,
            "spawn_time": self.spawn_time,
            "resolved": self.resolved,
            "expired": self.expired,
            "remaining_s": max(0, self.time_limit_s - (time.time() - self.spawn_time))
        }


@dataclass
class MoveResult:
    points_base: int
    points_total: int
    multipliers_applied: List[str]
    penalties_applied: List[str]
    player_score: float
    ai_score: float
    ai_strategy_id: str
    beat_ai: bool
    streak_count: int
    streak_multiplier: float
    new_badges: List[Badge]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "points_base": self.points_base,
            "points_total": self.points_total,
            "multipliers_applied": self.multipliers_applied,
            "penalties_applied": self.penalties_applied,
            "player_score": round(self.player_score, 3),
            "ai_score": round(self.ai_score, 3),
            "ai_strategy_id": self.ai_strategy_id,
            "beat_ai": self.beat_ai,
            "streak_count": self.streak_count,
            "streak_multiplier": self.streak_multiplier,
            "new_badges": [b.to_dict() for b in self.new_badges]
        }


@dataclass
class GameState:
    session_id: str
    player_name: str
    mode: str  # "free_play", "challenge", "ai_duel"
    difficulty: str  # "easy", "normal", "hard"
    total_points: int = 0
    current_streak: int = 0
    max_streak: int = 0
    decisions_made: int = 0
    ai_beats: int = 0
    spillback_free_streak: int = 0
    emergency_perfect_count: int = 0
    low_emission_count: int = 0
    total_delay_reduction_pct: float = 0.0
    badges_unlocked: List[Badge] = field(default_factory=list)
    active_event: Optional[CongestionEvent] = None
    active_challenge: Optional[str] = None
    challenge_passed: Optional[bool] = None
    move_history: List[Dict[str, Any]] = field(default_factory=list)
    session_start: float = 0.0
    session_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "player_name": self.player_name,
            "mode": self.mode,
            "difficulty": self.difficulty,
            "total_points": self.total_points,
            "current_streak": self.current_streak,
            "max_streak": self.max_streak,
            "decisions_made": self.decisions_made,
            "ai_beats": self.ai_beats,
            "spillback_free_streak": self.spillback_free_streak,
            "emergency_perfect_count": self.emergency_perfect_count,
            "low_emission_count": self.low_emission_count,
            "badges_unlocked": [b.to_dict() for b in self.badges_unlocked],
            "active_event": self.active_event.to_dict() if self.active_event else None,
            "active_challenge": self.active_challenge,
            "challenge_passed": self.challenge_passed,
            "session_active": self.session_active,
            "session_duration_s": round(time.time() - self.session_start, 1) if self.session_start else 0
        }


@dataclass
class LeaderboardEntry:
    player: str
    score: int
    mode: str
    decisions: int
    badges: List[str]
    max_streak: int
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player": self.player,
            "score": self.score,
            "mode": self.mode,
            "decisions": self.decisions,
            "badges": self.badges,
            "max_streak": self.max_streak,
            "timestamp": self.timestamp
        }


# ---------------------------------------------------------------------------
# Badge Definitions
# ---------------------------------------------------------------------------

ALL_BADGES = [
    Badge("traffic_novice", "Traffic Novice", "traffic_light", "Complete your first challenge scenario", "bronze"),
    Badge("spillback_free", "Spillback-Free Master", "shield", "10 consecutive decisions with 0 spillback", "silver"),
    Badge("speed_demon", "Speed Demon", "bolt", "Maintain avg speed > 42 km/h for 5+ decisions", "silver"),
    Badge("green_hero", "Green Hero", "leaf", "Select lowest-emissions strategy 15 times", "silver"),
    Badge("emergency_ace", "Emergency Ace", "ambulance", "Clear 5 emergencies with 0.0s delay", "gold"),
    Badge("ai_challenger", "AI Challenger", "robot", "Beat the AI's optimal move 20 times", "gold"),
    Badge("grand_commander", "Grand Commander", "crown", "Accumulate 50,000 lifetime points", "platinum"),
]


# ---------------------------------------------------------------------------
# Challenge Definitions
# ---------------------------------------------------------------------------

CHALLENGE_SCENARIOS = {
    "rush_hour": {
        "name": "Rush Hour Surge",
        "description": "Vehicle demand surging at J2. Manage queues across all approaches without spillback.",
        "events_count": 5,
        "time_limit_s": 180,
        "win_conditions": {"max_avg_delay_s": 0.30, "max_spillback_events": 0},
    },
    "emergency_dispatch": {
        "name": "Emergency Dispatch",
        "description": "Ambulance inbound. Clear green corridor while minimizing network disruption.",
        "events_count": 3,
        "time_limit_s": 120,
        "win_conditions": {"max_emergency_delay_s": 0.0, "max_network_delay_s": 0.40},
    },
    "accident_blockage": {
        "name": "Accident Blockage",
        "description": "Lane blocked on J1-J2. Divert traffic and rebalance signals.",
        "events_count": 4,
        "time_limit_s": 150,
        "win_conditions": {"max_total_queue_m": 50.0},
    },
    "cascade_prevention": {
        "name": "Cascade Prevention",
        "description": "J2 congestion propagating to J1 and J3. Prevent full gridlock within 60s.",
        "events_count": 3,
        "time_limit_s": 60,
        "win_conditions": {"min_queue_reduction_pct": 40.0},
    }
}


# ---------------------------------------------------------------------------
# Congestion Event Generator
# ---------------------------------------------------------------------------

# Event templates for each type
EVENT_TEMPLATES = {
    "rush_hour": [
        {"severity": "high", "desc": "Heavy traffic surge detected! Vehicle count rising rapidly at {junction}. Manage signal timing to prevent queue buildup.", "time_limit": 30},
        {"severity": "medium", "desc": "Moderate demand increase at {junction}. Queues are growing on the approach lanes.", "time_limit": 25},
        {"severity": "critical", "desc": "CRITICAL: Peak hour congestion at {junction}! Queue exceeding 50m. Immediate intervention needed.", "time_limit": 20},
    ],
    "emergency": [
        {"severity": "critical", "desc": "EMERGENCY VEHICLE approaching {junction}! Clear the corridor immediately for AMBULANCE.", "time_limit": 15},
        {"severity": "critical", "desc": "FIRE ENGINE inbound via corridor through {junction}. Override signals to create green wave.", "time_limit": 15},
    ],
    "accident": [
        {"severity": "high", "desc": "Accident reported on approach to {junction}. Lane partially blocked. Divert traffic to alternate routes.", "time_limit": 30},
        {"severity": "medium", "desc": "Minor collision near {junction} causing lane restriction. Rebalance signal phases.", "time_limit": 25},
    ],
    "cascade": [
        {"severity": "critical", "desc": "SPILLBACK ALERT: Queue from {junction} propagating to adjacent junctions! Prevent full corridor gridlock.", "time_limit": 20},
        {"severity": "high", "desc": "Congestion cascade building from {junction}. Downstream queues rising. Act fast to contain.", "time_limit": 25},
    ],
}


class GameEngine:
    """Core game engine managing sessions, events, scoring, badges, and leaderboard."""

    def __init__(self):
        self.optimizer = StrategyOptimizer()
        self.state: Optional[GameState] = None
        self.event_counter = 0
        self.last_event_time = 0.0
        self.leaderboard_path = PROJECT_ROOT / "data" / "leaderboard.json"

    # ------------------------------------------------------------------
    # Session Management
    # ------------------------------------------------------------------

    def start_session(self, player_name: str = "Commander", mode: str = "free_play",
                      difficulty: str = "normal", challenge_id: str = None) -> GameState:
        """Initialize a new game session."""
        session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
        self.state = GameState(
            session_id=session_id,
            player_name=player_name,
            mode=mode,
            difficulty=difficulty,
            session_start=time.time(),
            active_challenge=challenge_id if mode == "challenge" else None,
            badges_unlocked=[]
        )
        self.event_counter = 0
        self.last_event_time = time.time()
        return self.state

    def end_session(self) -> Dict[str, Any]:
        """End the current game session, save to leaderboard, return summary."""
        if not self.state:
            return {"error": "No active session"}

        self.state.session_active = False
        duration = time.time() - self.state.session_start

        # Evaluate challenge pass/fail
        if self.state.mode == "challenge" and self.state.active_challenge:
            self.state.challenge_passed = self._evaluate_challenge_pass()
            # Award Traffic Novice badge on first challenge completion
            if self.state.challenge_passed:
                self._try_unlock_badge("traffic_novice")

        # Grand Commander check
        self._try_unlock_badge("grand_commander")

        summary = {
            "session_id": self.state.session_id,
            "player_name": self.state.player_name,
            "mode": self.state.mode,
            "total_points": self.state.total_points,
            "decisions_made": self.state.decisions_made,
            "max_streak": self.state.max_streak,
            "ai_beats": self.state.ai_beats,
            "badges_earned": [b.to_dict() for b in self.state.badges_unlocked],
            "challenge_passed": self.state.challenge_passed,
            "session_duration_s": round(duration, 1)
        }

        # Save to leaderboard
        self._save_to_leaderboard()

        return summary

    # ------------------------------------------------------------------
    # Event Spawning
    # ------------------------------------------------------------------

    def spawn_event(self, traffic_state: Dict[str, Any] = None) -> Optional[CongestionEvent]:
        """Generate a contextual congestion event based on current traffic conditions."""
        if not self.state or not self.state.session_active:
            return None

        # Don't spawn if there's already an active unresolved event
        if self.state.active_event and not self.state.active_event.resolved and not self.state.active_event.expired:
            elapsed = time.time() - self.state.active_event.spawn_time
            if elapsed < self.state.active_event.time_limit_s:
                return self.state.active_event
            else:
                # Mark expired (timeout penalty applied on next move or here)
                self.state.active_event.expired = True

        # Determine event interval based on difficulty
        interval_map = {"easy": 35, "normal": 25, "hard": 15}
        min_interval = interval_map.get(self.state.difficulty, 25)

        if time.time() - self.last_event_time < min_interval:
            return self.state.active_event  # Still in cooldown

        # Contextual event type selection
        event_type = self._select_event_type(traffic_state)
        junction = self._select_target_junction(traffic_state, event_type)

        # Pick a template
        templates = EVENT_TEMPLATES.get(event_type, EVENT_TEMPLATES["rush_hour"])
        template = random.choice(templates)

        self.event_counter += 1
        event = CongestionEvent(
            event_id=f"evt_{self.event_counter}",
            event_type=event_type,
            target_junction=junction,
            severity=template["severity"],
            description=template["desc"].format(junction=junction),
            time_limit_s=float(template["time_limit"]),
            spawn_time=time.time()
        )

        self.state.active_event = event
        self.last_event_time = time.time()
        return event

    def _select_event_type(self, traffic_state: Dict[str, Any] = None) -> str:
        """Select event type contextually based on traffic conditions."""
        if self.state.mode == "challenge" and self.state.active_challenge:
            challenge = CHALLENGE_SCENARIOS.get(self.state.active_challenge)
            if challenge:
                return self.state.active_challenge

        # Weighted random based on game progression
        if traffic_state and traffic_state.get("junctions"):
            max_queue = max(
                j.get("total_queue_m", 0) for j in traffic_state["junctions"].values()
            )
            if max_queue > 50:
                return random.choice(["cascade", "cascade", "rush_hour"])
            elif max_queue > 30:
                return random.choice(["rush_hour", "accident", "cascade"])

        weights = [0.40, 0.20, 0.20, 0.20]  # rush_hour, emergency, accident, cascade
        return random.choices(
            ["rush_hour", "emergency", "accident", "cascade"],
            weights=weights, k=1
        )[0]

    def _select_target_junction(self, traffic_state: Dict[str, Any], event_type: str) -> str:
        """Select the most relevant junction for the event."""
        if traffic_state and traffic_state.get("junctions"):
            junctions = traffic_state["junctions"]
            # Pick junction with highest queue for congestion events
            if event_type in ("rush_hour", "cascade"):
                return max(junctions.keys(), key=lambda j: junctions[j].get("total_queue_m", 0))
            elif event_type == "accident":
                return random.choice(list(junctions.keys()))
        return random.choice(["J1", "J2", "J3"])

    # ------------------------------------------------------------------
    # Player Move Evaluation
    # ------------------------------------------------------------------

    def evaluate_player_move(self, player_strategy: Strategy,
                             traffic_state: Dict[str, Any] = None) -> MoveResult:
        """Evaluate the player's chosen strategy against AI optimal and baseline."""
        if not self.state:
            raise RuntimeError("No active game session")

        event = self.state.active_event
        decision_time = time.time() - (event.spawn_time if event else time.time())

        # Build simulated scenario results for player's strategy and baselines
        state_snapshot = traffic_state or {}
        junctions = state_snapshot.get("junctions", {})
        nm = state_snapshot.get("network_metrics", {})

        base_delay = nm.get("avg_waiting_time_s", 0.25)
        base_queue = nm.get("mean_queue_length_m", 30.0)
        base_emissions = 14.0

        # Simulate do-nothing result
        res_do_nothing = ScenarioResult(
            strategy_id="do_nothing", strategy_type="do_nothing", parameters={},
            simulation_start_time=0.0, simulation_end_time=180.0, horizon_seconds=180.0,
            predicted_delay_s=base_delay, predicted_queue_m=base_queue,
            predicted_throughput=1001, predicted_emissions=base_emissions
        )

        # Simulate player's strategy result (with realistic impact modeling)
        player_result = self._simulate_strategy_impact(player_strategy, res_do_nothing, event)

        # Generate AI optimal candidates and pick best
        ai_candidates = self._generate_ai_candidates(res_do_nothing, event)
        ai_best, ai_best_score = self.optimizer.select_best_strategy(ai_candidates)

        # Score player's move
        player_score = self.optimizer.score_candidate(player_result, res_do_nothing)
        dn_score = self.optimizer.score_candidate(res_do_nothing)

        # Calculate base points
        if dn_score > 0:
            improvement_ratio = (dn_score - player_score) / dn_score
        else:
            improvement_ratio = 0.0
        points_base = round(1000 * improvement_ratio)

        # Apply multipliers and penalties
        multipliers = []
        penalties = []
        multiplier_total = 1.0

        # Beat-the-AI bonus
        beat_ai = player_score <= ai_best_score
        if beat_ai:
            multiplier_total *= 2.0
            multipliers.append("Beat-the-AI x2.0")
            self.state.ai_beats += 1

        # Speed bonus (decision within 5s)
        if event and decision_time <= 5.0:
            multiplier_total *= 1.3
            multipliers.append("Speed Bonus x1.3")

        # Streak tracking
        if points_base > 0:
            self.state.current_streak += 1
        else:
            self.state.current_streak = 0

        if self.state.current_streak > self.state.max_streak:
            self.state.max_streak = self.state.current_streak

        # Streak multiplier
        streak_mult = 1.0
        if self.state.current_streak >= 10:
            streak_mult = 3.0
            multipliers.append("10-Streak x3.0")
        elif self.state.current_streak >= 5:
            streak_mult = 2.0
            multipliers.append("5-Streak x2.0")
        elif self.state.current_streak >= 3:
            streak_mult = 1.5
            multipliers.append("3-Streak x1.5")
        multiplier_total *= streak_mult

        # Flat bonuses
        flat_bonus = 0

        # Zero-spillback bonus
        spillback = self.optimizer.compute_spillback_penalty(player_result, res_do_nothing)
        if spillback == 0:
            flat_bonus += 200
            multipliers.append("+200 Zero-Spillback")
            self.state.spillback_free_streak += 1
        else:
            self.state.spillback_free_streak = 0

        # Emergency ace bonus
        if event and event.event_type == "emergency" and player_strategy.strategy_type == "emergency_priority":
            emergency_delay = player_result.predicted_emergency_delay_s or 0.0
            if emergency_delay == 0.0:
                flat_bonus += 500
                multipliers.append("+500 Emergency Ace")
                self.state.emergency_perfect_count += 1

        # Low emissions tracking
        if player_result.predicted_emissions is not None and player_result.predicted_emissions < base_emissions * 0.95:
            self.state.low_emission_count += 1

        # Penalties
        # Gridlock penalty: any junction queue > 80m
        if player_result.predicted_queue_m > 80:
            penalties.append("-300 Gridlock")
            flat_bonus -= 300

        # Spillback transfer penalty
        if spillback > 10:
            penalties.append("-150 Spillback Transfer")
            flat_bonus -= 150

        # Emergency missed penalty
        if event and event.event_type == "emergency":
            e_delay = player_result.predicted_emergency_delay_s
            if e_delay is not None and e_delay > 5.0:
                penalties.append("-500 Missed Emergency")
                flat_bonus -= 500

        # Inaction timeout penalty
        if event and event.expired and player_strategy.strategy_type == "do_nothing":
            penalties.append("-100 Inaction Timeout")
            flat_bonus -= 100

        # Final points
        points_total = round(points_base * multiplier_total) + flat_bonus

        # Update game state
        self.state.total_points += points_total
        self.state.decisions_made += 1

        # Track delay reduction
        if base_delay > 0:
            delay_red = ((base_delay - player_result.predicted_delay_s) / base_delay) * 100
            self.state.total_delay_reduction_pct += delay_red

        # Mark event resolved
        if event:
            event.resolved = True

        # Record move
        self.state.move_history.append({
            "event_id": event.event_id if event else None,
            "strategy": player_strategy.strategy_id,
            "points": points_total,
            "beat_ai": beat_ai,
            "timestamp": time.time()
        })

        # Check badge unlocks
        new_badges = self._check_badges()

        return MoveResult(
            points_base=points_base,
            points_total=points_total,
            multipliers_applied=multipliers,
            penalties_applied=penalties,
            player_score=player_score,
            ai_score=ai_best_score,
            ai_strategy_id=ai_best.strategy_id,
            beat_ai=beat_ai,
            streak_count=self.state.current_streak,
            streak_multiplier=streak_mult,
            new_badges=new_badges
        )

    def _simulate_strategy_impact(self, strategy: Strategy,
                                   baseline: ScenarioResult,
                                   event: Optional[CongestionEvent]) -> ScenarioResult:
        """Simulate the impact of a player's strategy choice on traffic metrics."""
        base_d = baseline.predicted_delay_s
        base_q = baseline.predicted_queue_m
        base_e = baseline.predicted_emissions or 14.0

        # Impact modifiers by strategy type
        if strategy.strategy_type == "green_extend":
            ext = float(strategy.parameters.get("extension_seconds", 20))
            factor = min(0.30, ext / 100.0)  # Up to 30% improvement
            pred_delay = max(0.10, base_d * (1 - factor))
            pred_queue = max(10.0, base_q * (1 - factor * 1.2))
            pred_emissions = base_e * (1 - factor * 0.5)
            pred_emergency = None
        elif strategy.strategy_type == "diversion":
            pct = float(strategy.parameters.get("diversion_percent", 25))
            factor = min(0.25, pct / 150.0)
            pred_delay = max(0.12, base_d * (1 - factor))
            pred_queue = max(12.0, base_q * (1 - factor * 0.8))
            pred_emissions = base_e * (1 - factor * 0.3)
            pred_emergency = None
        elif strategy.strategy_type == "dynamic_lane":
            pred_delay = base_d * 1.02  # Slight increase (not always effective)
            pred_queue = base_q * 1.05
            pred_emissions = base_e * 1.03
            pred_emergency = None
        elif strategy.strategy_type == "emergency_priority":
            pred_delay = base_d * 1.15  # Network delay increases slightly
            pred_queue = base_q * 0.85
            pred_emissions = base_e * 0.9
            pred_emergency = 0.0  # Perfect emergency clearance
        elif strategy.strategy_type == "do_nothing":
            pred_delay = base_d
            pred_queue = base_q
            pred_emissions = base_e
            pred_emergency = None
            if event and event.event_type == "emergency":
                pred_emergency = 8.0  # Doing nothing during emergency = bad
        else:
            pred_delay = base_d
            pred_queue = base_q
            pred_emissions = base_e
            pred_emergency = None

        # Event severity modifier
        if event and event.severity == "critical":
            pred_delay *= 1.15
            pred_queue *= 1.1

        return ScenarioResult(
            strategy_id=strategy.strategy_id,
            strategy_type=strategy.strategy_type,
            parameters=strategy.parameters,
            simulation_start_time=0.0,
            simulation_end_time=180.0,
            horizon_seconds=180.0,
            predicted_delay_s=round(pred_delay, 3),
            predicted_queue_m=round(pred_queue, 1),
            predicted_throughput=1005,
            predicted_emissions=round(pred_emissions, 2),
            predicted_emergency_delay_s=pred_emergency
        )

    def _generate_ai_candidates(self, baseline: ScenarioResult,
                                 event: Optional[CongestionEvent]) -> List[ScenarioResult]:
        """Generate AI candidate strategies and their results for comparison."""
        candidates = [baseline]  # do_nothing as baseline

        junction = event.target_junction if event else "J2"

        # Green extend candidate
        s_green = Strategy("ai_green_extend", "green_extend",
                           {"junction_id": junction, "extension_seconds": 20.0})
        candidates.append(self._simulate_strategy_impact(s_green, baseline, event))

        # Diversion candidate
        s_div = Strategy("ai_diversion", "diversion",
                         {"from_edge": "J1_to_J2", "diversion_percent": 25.0})
        candidates.append(self._simulate_strategy_impact(s_div, baseline, event))

        # Emergency if applicable
        if event and event.event_type == "emergency":
            s_emg = Strategy("ai_emergency", "emergency_priority",
                             {"corridor": "J1-J2-J3", "vehicle_id": "AI_UNIT"})
            candidates.append(self._simulate_strategy_impact(s_emg, baseline, event))

        return candidates

    # ------------------------------------------------------------------
    # Badge System
    # ------------------------------------------------------------------

    def _check_badges(self) -> List[Badge]:
        """Check all badge conditions and unlock any newly earned badges."""
        new_badges = []
        already_unlocked = {b.badge_id for b in self.state.badges_unlocked}

        for badge_def in ALL_BADGES:
            if badge_def.badge_id in already_unlocked:
                continue
            if self._badge_condition_met(badge_def.badge_id):
                badge = Badge(
                    badge_id=badge_def.badge_id,
                    name=badge_def.name,
                    icon=badge_def.icon,
                    description=badge_def.description,
                    tier=badge_def.tier,
                    unlocked=True,
                    unlock_time=time.time()
                )
                self.state.badges_unlocked.append(badge)
                new_badges.append(badge)

        return new_badges

    def _badge_condition_met(self, badge_id: str) -> bool:
        """Evaluate whether a specific badge's unlock condition is met."""
        s = self.state
        if badge_id == "traffic_novice":
            return s.mode == "challenge" and s.challenge_passed is True
        elif badge_id == "spillback_free":
            return s.spillback_free_streak >= 10
        elif badge_id == "speed_demon":
            return s.decisions_made >= 5 and (s.total_delay_reduction_pct / max(1, s.decisions_made)) > 10.0
        elif badge_id == "green_hero":
            return s.low_emission_count >= 15
        elif badge_id == "emergency_ace":
            return s.emergency_perfect_count >= 5
        elif badge_id == "ai_challenger":
            return s.ai_beats >= 20
        elif badge_id == "grand_commander":
            return s.total_points >= 50000
        return False

    def _try_unlock_badge(self, badge_id: str):
        """Manually try to unlock a specific badge."""
        already_unlocked = {b.badge_id for b in self.state.badges_unlocked}
        if badge_id in already_unlocked:
            return
        for badge_def in ALL_BADGES:
            if badge_def.badge_id == badge_id:
                badge = Badge(
                    badge_id=badge_def.badge_id, name=badge_def.name,
                    icon=badge_def.icon, description=badge_def.description,
                    tier=badge_def.tier, unlocked=True, unlock_time=time.time()
                )
                self.state.badges_unlocked.append(badge)
                break

    # ------------------------------------------------------------------
    # Challenge Evaluation
    # ------------------------------------------------------------------

    def _evaluate_challenge_pass(self) -> bool:
        """Evaluate whether the current challenge's win conditions are met."""
        if not self.state.active_challenge:
            return False
        challenge = CHALLENGE_SCENARIOS.get(self.state.active_challenge)
        if not challenge:
            return False

        # Simple heuristic: positive total points = pass
        conditions = challenge["win_conditions"]
        if self.state.total_points > 0 and self.state.decisions_made > 0:
            avg_points = self.state.total_points / self.state.decisions_made
            return avg_points > 50  # Must average > 50 points per decision
        return False

    # ------------------------------------------------------------------
    # Leaderboard
    # ------------------------------------------------------------------

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Load and return the top 10 leaderboard entries."""
        try:
            with open(self.leaderboard_path, "r") as f:
                entries = json.load(f)
            entries.sort(key=lambda x: x.get("score", 0), reverse=True)
            return entries[:10]
        except Exception:
            return []

    def _save_to_leaderboard(self):
        """Save current session to persistent leaderboard."""
        if not self.state or self.state.total_points <= 0:
            return

        entry = {
            "player": self.state.player_name,
            "score": self.state.total_points,
            "mode": self.state.mode,
            "decisions": self.state.decisions_made,
            "badges": [b.badge_id for b in self.state.badges_unlocked],
            "max_streak": self.state.max_streak,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        try:
            with open(self.leaderboard_path, "r") as f:
                entries = json.load(f)
        except Exception:
            entries = []

        entries.append(entry)
        entries.sort(key=lambda x: x.get("score", 0), reverse=True)
        entries = entries[:50]  # Keep top 50

        self.leaderboard_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.leaderboard_path, "w") as f:
            json.dump(entries, f, indent=2)
