"""
Baseline 1: Fixed-Time Traffic Signal Controller for NEXUS-TWIN.
Executes pre-timed, cyclic phase durations regardless of live traffic queues.
"""

from typing import List, Dict

class FixedTimeController:
    def __init__(self, tls_ids: List[str], green_duration: int = 30, yellow_duration: int = 4):
        self.tls_ids = tls_ids
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration
        # Cycle: Phase 0 (Green N-S) -> Phase 1 (Yellow) -> Phase 2 (Green E-W) -> Phase 3 (Yellow)
        self.phase_timer: Dict[str, int] = {tls_id: 0 for tls_id in tls_ids}

    def step(self, traci_module, step_time: float):
        """Called every simulation step to advance fixed-time signal logic."""
        for tls_id in self.tls_ids:
            self.phase_timer[tls_id] += 1
            current_phase = traci_module.trafficlight.getPhase(tls_id)
            
            # Determine duration for current phase
            # Phase 0 & 2 are Green (30s), Phase 1 & 3 are Yellow (4s)
            target_duration = self.yellow_duration if (current_phase % 2 == 1) else self.green_duration
            
            if self.phase_timer[tls_id] >= target_duration:
                # Transition to next phase in definition
                num_phases = len(traci_module.trafficlight.getAllProgramLogics(tls_id)[0].phases)
                next_phase = (current_phase + 1) % num_phases
                traci_module.trafficlight.setPhase(tls_id, next_phase)
                self.phase_timer[tls_id] = 0
