# DATA_CONTRACT.md — Single Source of Truth Data Schemas

**Status**: [IMPLEMENTED] Authoritative Data Contract  
**Last Updated**: 2026-08-23

---

## 1. Overview
This document serves as the **single source of truth** for all data structures exchanged between Unity, FastAPI, Python Intelligence, and SUMO.

---

## 2. Identifiers & Enums

### 2.1 Junction Identifiers
- `J1`: North Intersection
- `J2`: Central Bottleneck Intersection
- `J3`: South Intersection

### 2.2 Vehicle Types
- `car`: Standard passenger car
- `bus`: Public transit vehicle
- `truck`: Heavy freight transport
- `motorcycle`: Two-wheeled light vehicle
- `ambulance`: Priority emergency vehicle (Red LED)
- `police`: Emergency law enforcement
- `fire`: Emergency fire engine

### 2.3 Strategy Types
- `do_nothing`: Maintain baseline controller unchanged
- `green_extend`: Extend green light phase duration on target junction
- `diversion`: Reroute percentage of incoming traffic to alternate edges
- `dynamic_lane`: Open shoulder/dynamic lane for traffic flow
- `emergency_priority`: Force green wave corridor for priority vehicle

---

## 3. Core JSON Schemas

### 3.1 `TrafficState` Schema
```json
{
  "type": "object",
  "required": ["step", "active_vehicles", "avg_speed_kmh", "total_waiting_time_s", "junctions"],
  "properties": {
    "step": {"type": "number", "minimum": 0, "description": "Simulation time in seconds"},
    "active_vehicles": {"type": "integer", "minimum": 0},
    "avg_speed_kmh": {"type": "number", "minimum": 0.0, "unit": "km/h"},
    "total_waiting_time_s": {"type": "number", "minimum": 0.0, "unit": "seconds"},
    "junctions": {"type": "object"}
  }
}
```

### 3.2 `Strategy` Schema
```json
{
  "type": "object",
  "required": ["strategy_id", "strategy_type", "parameters"],
  "properties": {
    "strategy_id": {"type": "string", "example": "green_extend_J2"},
    "strategy_type": {"type": "string", "enum": ["do_nothing", "green_extend", "diversion", "dynamic_lane", "emergency_priority"]},
    "parameters": {"type": "object"}
  }
}
```
