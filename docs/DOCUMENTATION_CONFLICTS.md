# DOCUMENTATION_CONFLICTS.md — Conflict Audit & Resolution Log

**Status**: [IMPLEMENTED] Active Resolution Record  
**Last Updated**: 2026-08-23

---

## 1. Overview
This document tracks all identified conflicts across product, technical, design, and plan specifications (`PRD.md`, `TECH_STACK.md`, `DESIGN_GUIDELINES.md`, `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md`), along with their authoritative resolutions.

---

## 2. Conflict Log

### Conflict 001: Web UI vs Unity 3D Client
- **Source Documents**: Legacy `Resources/phase-6-productization/` vs `PRD.md` & `TECH_STACK.md`.
- **Description**: Early documentation referenced a 2D web dashboard using HTML5 Canvas (`web/`). `PRD.md` and `TECH_STACK.md` mandate Unity 6 with URP as the canonical game client.
- **Resolution**: `web/` is archived as `[LEGACY]` in `docs/legacy/web_ui/`. **Unity 6 + URP is the authoritative client**.

### Conflict 002: Decision Server Technology (Python `http.server` vs FastAPI)
- **Source Documents**: `backend/api/decision_server.py` implementation vs `TECH_STACK.md` §12.
- **Description**: Current code uses Python standard `http.server`. `TECH_STACK.md` mandates FastAPI with WebSocket support.
- **Resolution**: Current `decision_server.py` is tagged `[PARTIALLY IMPLEMENTED]`. It serves MVP HTTP endpoints today, and will be upgraded to FastAPI + WebSockets during Unity integration.

### Conflict 003: Document Location (`docs/game/` vs `docs/`)
- **Source Documents**: Repository layout vs prompt specification §4 & §29.
- **Description**: `PRD.md`, `TECH_STACK.md`, `DESIGN_GUIDELINES.md`, and `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md` existed inside `docs/game/`.
- **Resolution**: Copies are maintained in `docs/` to satisfy both the modular layout (`docs/game/`) and the root documentation contract (`docs/`).

### Conflict 004: Multi-Agent Role in MVP
- **Source Documents**: Early design notes vs `PRD.md` §14 & `TECH_STACK.md` §17–21.
- **Description**: Ambiguity around whether LangGraph multi-agent orchestration is required for the initial hackathon demo.
- **Resolution**: **Multi-Agent is tagged [FUTURE] (Phase 2)**. The MVP relies strictly on deterministic Python Strategy Generator + XGBoost Predictor + Scenario Engine. Multi-agent architecture must be documented but NOT required for MVP execution.
