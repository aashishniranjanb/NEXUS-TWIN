# PERFORMANCE_GUIDELINES.md — Performance Budgets & Optimization

**Status**: [PLANNED] Technical Performance Budget  
**Target FPS**: 60 FPS (Desktop Target) / 30 FPS Minimum  
**Last Updated**: 2026-08-23

---

## 1. Performance Budgets

| Metric | Desktop Target | WebGL Limit |
| :--- | :--- | :--- |
| **Frame Rate** | 60 FPS | 30 FPS |
| **Draw Calls** | < 150 | < 80 |
| **Triangles / Scene** | < 100k | < 50k |
| **Active Vehicles** | Up to 500 pooled | Up to 200 pooled |
| **WebSocket Update Rate**| 10 Hz | 5 Hz |

---

## 2. Key Optimization Strategies
1. **Vehicle Prefab Pooling**: Pre-instantiate 300 vehicle GameObjects at startup (`VehiclePoolManager.cs`). Never `Instantiate()` or `Destroy()` during simulation.
2. **URP Material Batching**: Use a single master palette texture for all low-poly environment meshes.
