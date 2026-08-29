"""
Integration Tests for SSE Streaming Decision Pipeline (/api/v1/decision/stream).
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_sse_streaming_events():
    with client.stream("GET", "/api/v1/decision/stream?city=Philadelphia&intersection_id=0&scenario=INCIDENT_LIKE_DISRUPTION") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        events = []
        for line in response.iter_lines():
            if line:
                events.append(line)
                
        # Assert events contain event headers and data payloads
        event_lines = [e for e in events if e.startswith("event: ")]
        assert len(event_lines) >= 8
        assert "event: traffic_state_received" in event_lines
        assert "event: prediction_complete" in event_lines
        assert "event: simulation_complete" in event_lines
        assert "event: critic_complete" in event_lines
        assert "event: pipeline_complete" in event_lines
