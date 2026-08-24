# JUDGE_DEMO_CHECKLIST.md — Pre-Demo Launch Verification Checklist

**Status**: [IMPLEMENTED] Operational Readiness Checklist  
**Last Updated**: 2026-08-23

---

## Pre-Demo Launch Sequence
- [x] Python Virtual Environment Activated (`python 3.12+`)
- [x] `SUMO_HOME` environment variable verified (`SUMO 1.27.1`)
- [x] Test suite passing (`python -m pytest tests/`)
- [x] Decision Server REST API running (`python backend/api/decision_server.py`)
- [x] API Health Check verified (`curl http://localhost:8000/api/status`)
- [x] Leaderboard file present (`data/leaderboard.json`)
- [x] XGBoost model weights present (`data/congestion_model.pkl`)
- [x] Unity 6 Client launched in 1080p Desktop Mode
- [x] Emergency scenario pre-loaded
