# SECURITY.md — Payload Validation & Security Specs

**Status**: [IMPLEMENTED] Input Sanitize Contracts  
**Last Updated**: 2026-08-23

---

## 1. Security & Validation Rules
1. **Input Payload Validation**: All incoming REST/WebSocket JSON payloads are strictly validated against Pydantic schemas in `backend/schemas/scenario_models.py`.
2. **Localhost Scoping**: The API server binds to `127.0.0.1` by default for local development.
3. **Model Artifact Integrity**: Trained XGBoost pickle files (`congestion_model.pkl`) are loaded strictly from the local `data/` directory.
