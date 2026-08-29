"""
Constants and Schema Definitions for BigQuery-Geotab Preprocessing.
"""

from typing import Dict, List

CITIES: List[str] = ["Atlanta", "Boston", "Chicago", "Philadelphia"]

HEADINGS: List[str] = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

HEADING_TO_DEGREES: Dict[str, float] = {
    "N": 0.0,
    "NE": 45.0,
    "E": 90.0,
    "SE": 135.0,
    "S": 180.0,
    "SW": 225.0,
    "W": 270.0,
    "NW": 315.0
}

UNKNOWN_STREET: str = "UNKNOWN"

CONTEXT_COLUMNS: List[str] = [
    "RowId",
    "IntersectionId",
    "Latitude",
    "Longitude",
    "EntryStreetName",
    "ExitStreetName",
    "EntryHeading",
    "ExitHeading",
    "Hour",
    "Weekend",
    "Month",
    "Path",
    "City"
]

PERCENTILE_TARGETS: Dict[str, List[str]] = {
    "TotalTimeStopped": [
        "TotalTimeStopped_p20",
        "TotalTimeStopped_p40",
        "TotalTimeStopped_p50",
        "TotalTimeStopped_p60",
        "TotalTimeStopped_p80"
    ],
    "TimeFromFirstStop": [
        "TimeFromFirstStop_p20",
        "TimeFromFirstStop_p40",
        "TimeFromFirstStop_p50",
        "TimeFromFirstStop_p60",
        "TimeFromFirstStop_p80"
    ],
    "DistanceToFirstStop": [
        "DistanceToFirstStop_p20",
        "DistanceToFirstStop_p40",
        "DistanceToFirstStop_p50",
        "DistanceToFirstStop_p60",
        "DistanceToFirstStop_p80"
    ]
}

ALL_BEHAVIORAL_TARGETS: List[str] = (
    PERCENTILE_TARGETS["TotalTimeStopped"] +
    PERCENTILE_TARGETS["TimeFromFirstStop"] +
    PERCENTILE_TARGETS["DistanceToFirstStop"]
)
