# DEPLOYMENT.md — Local Setup & Build Pipeline

**Status**: [IMPLEMENTED] Local Dev Environment / [PLANNED] Standalone Builds  
**Last Updated**: 2026-08-23

---

## 1. Prerequisites
- **Python**: 3.12+ (Virtual environment recommended)
- **SUMO**: 1.27.1 (with `SUMO_HOME` environment variable set)
- **Unity**: Unity 6 LTS (6000.0.x) with URP package

---

## 2. Startup Sequence (Local Execution)

```bash
# Step 1: Start Backend API & Game Engine
python backend/api/decision_server.py

# Step 2: Verify Backend Status
curl http://localhost:8000/api/status

# Step 3: Launch Unity Client (from Unity Editor or Standalone Build)
# Open project in game/unity/ and press Play
```
