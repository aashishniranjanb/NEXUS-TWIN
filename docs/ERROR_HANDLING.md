# ERROR_HANDLING.md — Resilience & Fallback Matrix

**Status**: [IMPLEMENTED] Python Exception Handling / [PLANNED] Unity Mock Mode  
**Last Updated**: 2026-08-23

---

## 1. Failure Resilience Matrix

| Failure Mode | Detection Mechanism | Recovery Action | User Experience |
| :--- | :--- | :--- | :--- |
| **SUMO Crashes / Timeout** | TraCI connection reset | Restart SUMO instance; restore snapshot | Notification banner; simulation resets |
| **FastAPI Offline** | Unity REST request timeout (3s) | Switch Unity client to Mock Offline Mode | HUD banner: *"Offline Mode Active"* |
| **WebSocket Disconnect** | Socket error handler | Auto-reconnect with exponential backoff | Signal status indicator turns yellow |
| **Invalid Strategy** | API `400 Bad Request` | Fallback to `do_nothing` strategy | Error dialog: *"Invalid action"* |
