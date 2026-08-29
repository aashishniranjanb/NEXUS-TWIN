# 3D Traffic Visualization Architecture

| Specification | Implementation |
|---|---|
| **Render Engine** | Three.js / High-Performance 2.5D Canvas Viewport |
| **Geometry** | Procedural corridor nodes, directional arterial road links, and animated shockwave vectors |
| **Performance** | Particle batching & requestAnimationFrame interpolation (60 FPS smooth rendering) |
| **Interactivity** | Click to focus intersection, inspect telemetry, zoom & pan |

---

## 1. Visual Highlights
- **Congestion Heatmap Colors**:
  - `NORMAL`: Emerald Green (`#10b981`)
  - `MODERATE`: Amber (`#f59e0b`)
  - `CRITICAL / BOTTLENECK`: Rose Red (`#f43f5e`)
- **Domino Shockwave Animation**: Pulsing orange vectors propagating upstream along the cascade path ($J_2 \to J_1 \to J_4$).
- **Emergency Vehicle**: High-visibility flashing ambulance traversing the green wave corridor.
