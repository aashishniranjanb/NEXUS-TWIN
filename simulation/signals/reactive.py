"""
Baseline 2: Reactive Adaptive Traffic Signal Controller for NEXUS-TWIN.
Uses NEMA-style gap-out and queue-extension logic:
1. Identifies live active GREEN approach lanes vs opposing RED approach lanes using state strings.
2. IF elapsed < min_green (15s) -> Keep Green.
3. IF elapsed >= max_green (50s) -> Force Yellow.
4. IF opposing RED queue > active GREEN queue AND active GREEN queue <= threshold -> Switch to Yellow.
5. IF active GREEN queue > threshold -> Extend Green.
"""

from typing import List, Dict

class ReactiveAdaptiveController:
    def __init__(
        self, 
        tls_ids: List[str], 
        min_green: int = 15, 
        max_green: int = 50, 
        yellow_duration: int = 4,
        queue_threshold: int = 2
    ):
        self.tls_ids = tls_ids
        self.min_green = min_green
        self.max_green = max_green
        self.yellow_duration = yellow_duration
        self.queue_threshold = queue_threshold
        
        self.phase_timer: Dict[str, int] = {tls_id: 0 for tls_id in tls_ids}
        self.controlled_lanes: Dict[str, List[str]] = {}

    def initialize(self, traci_module):
        for tls_id in self.tls_ids:
            # Get controlled lanes corresponding to phase state indexes
            self.controlled_lanes[tls_id] = traci_module.trafficlight.getControlledLanes(tls_id)

    def step(self, traci_module, step_time: float):
        """Called every step to apply reactive rules based on live queue lengths."""
        for tls_id in self.tls_ids:
            self.phase_timer[tls_id] += 1
            current_phase = traci_module.trafficlight.getPhase(tls_id)
            elapsed = self.phase_timer[tls_id]
            
            # Yellow phase handling (fixed 4s duration)
            if current_phase % 2 == 1:
                if elapsed >= self.yellow_duration:
                    num_phases = len(traci_module.trafficlight.getAllProgramLogics(tls_id)[0].phases)
                    next_phase = (current_phase + 1) % num_phases
                    traci_module.trafficlight.setPhase(tls_id, next_phase)
                    self.phase_timer[tls_id] = 0
                continue

            # Minimum green constraint
            if elapsed < self.min_green:
                continue

            # Maximum green constraint (force switch)
            if elapsed >= self.max_green:
                num_phases = len(traci_module.trafficlight.getAllProgramLogics(tls_id)[0].phases)
                next_phase = (current_phase + 1) % num_phases
                traci_module.trafficlight.setPhase(tls_id, next_phase)
                self.phase_timer[tls_id] = 0
                continue

            # Read live phase state string (e.g. "GGrrGGrr")
            state_str = traci_module.trafficlight.getRedYellowGreenState(tls_id)
            lanes = self.controlled_lanes.get(tls_id, [])

            green_halting = 0
            red_halting = 0

            for i, lane_id in enumerate(lanes):
                if i < len(state_str):
                    char = state_str[i]
                    halting = traci_module.lane.getLastStepHaltingNumber(lane_id)
                    if char in ('G', 'g'):
                        green_halting += halting
                    elif char in ('r', 'R'):
                        red_halting += halting

            # Decision Logic:
            # If opposing red direction has higher demand AND green direction queue is clear/small -> Gap out (switch)
            if red_halting > green_halting and green_halting <= self.queue_threshold:
                num_phases = len(traci_module.trafficlight.getAllProgramLogics(tls_id)[0].phases)
                next_phase = (current_phase + 1) % num_phases
                traci_module.trafficlight.setPhase(tls_id, next_phase)
                self.phase_timer[tls_id] = 0
