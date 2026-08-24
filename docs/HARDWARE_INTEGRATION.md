# HARDWARE_INTEGRATION.md — Edge & Physical Traffic Signal Spec

**Status**: [FUTURE] Phase 3 Extension (DOCUMENT ONLY — NOT AN MVP DEPENDENCY)  
**Microcontroller Target**: ESP32 + MQTT Broker  
**Last Updated**: 2026-08-23

---

## 1. Physical Hardware Flow
```text
Live Traffic Camera ──► Edge Computer ──► MQTT Broker ──► NEXUS-TWIN ──► MQTT ──► ESP32 LED Traffic Light
```

---

## 2. Hardware Signal Protocol
- **Broker**: Mosquitto MQTT (`mqtt://localhost:1883`)
- **Topic**: `nexus/signals/J2/command`
- **Payload**: `{"junction_id": "J2", "phase": "GREEN_NORTH", "duration_s": 20}`
