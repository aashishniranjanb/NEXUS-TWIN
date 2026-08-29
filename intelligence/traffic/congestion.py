"""
Congestion Scoring and Severity Classifier Module.
Translates predicted and observed stopping durations into normalized congestion scores and severity tiers.
"""

from typing import Tuple
from intelligence.traffic.schema import CongestionSeverity

def calculate_congestion_score(predicted_wait_s: float, baseline_median_s: float, baseline_p80_s: float) -> Tuple[float, CongestionSeverity]:
    """
    Computes normalized congestion score [0.0, 1.0] and assigns operational severity.
    Grounds score in physical relative deviation from historical percentiles.
    """
    med = max(1.0, baseline_median_s)
    p80 = max(med + 1.0, baseline_p80_s)
    
    if predicted_wait_s <= med:
        score = 0.25 * (predicted_wait_s / med)
    elif predicted_wait_s <= p80:
        ratio = (predicted_wait_s - med) / (p80 - med)
        score = 0.25 + 0.45 * ratio
    else: # Above 80th percentile
        excess_ratio = (predicted_wait_s - p80) / max(15.0, p80)
        score = min(1.0, 0.70 + 0.30 * excess_ratio)
        
    score = round(float(score), 3)
    
    if score < 0.25:
        severity = CongestionSeverity.NORMAL
    elif score < 0.45:
        severity = CongestionSeverity.LOW
    elif score < 0.70:
        severity = CongestionSeverity.MODERATE
    elif score < 0.85:
        severity = CongestionSeverity.HIGH
    else:
        severity = CongestionSeverity.CRITICAL
        
    return score, severity

def estimate_queue_length_m(predicted_wait_s: float, baseline_mean_dist_m: float) -> float:
    """Estimates physical queue length proxy in meters."""
    # Physical traffic accumulation factor: ~1.2m of queue per second of average stopped time
    est_q = max(0.0, predicted_wait_s * 1.25 + baseline_mean_dist_m * 0.3)
    return round(float(est_q), 1)
