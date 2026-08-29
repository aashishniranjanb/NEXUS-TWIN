"""
End-to-End Integration Test for Data/ML Intelligence Pipeline.
Passes a raw traffic context through Preprocess -> Features -> Predict -> TrafficState -> Anomaly -> Fingerprint.
"""

import pytest
from pathlib import Path
from intelligence.traffic.state_builder import TrafficStateBuilder
from intelligence.fingerprint.classifier import TrafficFingerprintEngine
from intelligence.contracts.contracts import (
    TrafficStateContract, TrafficFingerprintContract
)

def test_full_pipeline_integration():
    state_builder = TrafficStateBuilder()
    fingerprint_engine = TrafficFingerprintEngine()

    raw_input = {
        "City": "Philadelphia",
        "IntersectionId": 463,
        "Hour": 17,
        "Weekend": 0,
        "Month": 10,
        "EntryHeading": "NW",
        "ExitHeading": "SE",
        "Latitude": 39.95,
        "Longitude": -75.16,
        "EntryStreetName": "Market St",
        "ExitStreetName": "15th St"
    }

    # Step 1: Build Traffic State
    traffic_state = state_builder.build_state(raw_input)
    assert traffic_state.intersection_id == 463
    assert traffic_state.predicted_stopped_time_s >= 0.0
    assert len(traffic_state.evidence) >= 2

    # Step 2: Validate against Shared Contract
    state_contract = TrafficStateContract(**traffic_state.model_dump())
    assert state_contract.city == "Philadelphia"

    # Step 3: Run Fingerprint Diagnosis
    observed_w = traffic_state.predicted_stopped_time_s
    observed_d = traffic_state.estimated_queue_m
    fp = fingerprint_engine.diagnose(raw_input, observed_wait_s=observed_w, observed_dist_m=observed_d)
    
    # Step 4: Validate Fingerprint Contract
    fp_contract = TrafficFingerprintContract(**fp.model_dump())
    assert fp_contract.classification in ["NORMAL", "RECURRING_CONGESTION", "INCIDENT_LIKE", "DEMAND_SURGE", "SIGNAL_RELATED"]
    assert fp_contract.confidence > 0.0
    assert len(fp_contract.evidence) > 0
