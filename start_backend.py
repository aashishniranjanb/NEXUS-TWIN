"""
NEXUS-TWIN Turnkey Backend Server Launcher.
Starts the FastAPI decision server and WebSocket telemetry stream on http://localhost:8000.
"""

import sys
import uvicorn
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    print("=" * 60)
    print("  NEXUS-TWIN Digital Twin Decision & Telemetry Server")
    print("  Version: 1.0.0 (Unity 6 + SUMO + XGBoost)")
    print("  REST API Base: http://localhost:8000")
    print("  WebSocket Stream: ws://localhost:8000/ws/traffic")
    print("=" * 60)

    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
