"""
Unit Tests for Traffic Fingerprint Classification.
"""

import pytest
from intelligence.fingerprint.classifier import TrafficFingerprintEngine, FingerprintClass

def test_fingerprint_engine():
    engine = TrafficFingerprintEngine()
    
    # 1. Normal Case
    normal_ctx = {"City": "Atlanta", "IntersectionId": 0, "Hour": 11, "Weekend": 0, "EntryHeading": "N"}
    fp_normal = engine.diagnose(normal_ctx, observed_wait_s=5.0, observed_dist_m=30.0)
    assert fp_normal.classification == FingerprintClass.NORMAL
    assert len(fp_normal.evidence) > 0
    assert fp_normal.limitation_disclaimer != ""

    # 2. Recurring Congestion Case (Peak commute hour)
    peak_ctx = {"City": "Boston", "IntersectionId": 100, "Hour": 8, "Weekend": 0, "EntryHeading": "N"}
    fp_peak = engine.diagnose(peak_ctx, observed_wait_s=55.0, observed_dist_m=15.0)
    assert fp_peak.classification in [FingerprintClass.RECURRING_CONGESTION, FingerprintClass.NORMAL, FingerprintClass.DEMAND_SURGE]

    # 3. Incident-Like Case (Severe off-peak delay)
    offpeak_ctx = {"City": "Philadelphia", "IntersectionId": 12, "Hour": 2, "Weekend": 0, "EntryHeading": "E"}
    fp_incident = engine.diagnose(offpeak_ctx, observed_wait_s=85.0, observed_dist_m=5.0)
    assert fp_incident.classification in [FingerprintClass.INCIDENT_LIKE, FingerprintClass.DEMAND_SURGE]
