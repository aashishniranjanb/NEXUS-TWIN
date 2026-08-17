# 04 — Research Literature Survey

This document summarizes the current (2024–2026) literature landscape that NexusTwin is positioned against. Claims are paraphrased from the source; each subsection lists the reference at the end. This survey should be expanded with additional sources as the project progresses, and every quantitative claim used in the final pitch/paper must trace back to a real citation here.

## 1. Intelligent Transportation Systems (ITS) — General

ITS research spans traffic detection, adaptive control, prediction, and — increasingly — Digital Twin representations of the physical road network. Digital Twin-based Intelligent Transportation Systems (DT-ITS) have been the subject of systematic review work covering their architecture, applications, and open challenges. [Ge et al., "Digital twin intelligent transportation system (DT-ITS) — A systematic review," IET Intelligent Transport Systems, 2024]

## 2. Adaptive Traffic Signal Control

AI- and RL-based traffic signal control is a mature research area. A comprehensive 2026 review covering more than 400 publications identifies reinforcement learning, deep learning, graph neural networks (GNNs), evolutionary algorithms, and fuzzy logic as the major approaches to intelligent traffic signal control. [Springer, "A comprehensive review of artificial intelligence techniques for traffic signal control in intelligent transportation systems," Discover Applied Sciences, 2026]

**Implication for NexusTwin**: "AI changes traffic light timing" is, on its own, not a novel claim — this space is already extensively researched.

## 3. Digital Twin + Simulation-Based Signal Control

A March 2026 study built an IoT-driven Digital Twin inside SUMO and used Q-learning for adaptive signal control, comparing fixed-time, vehicle-actuated, and AI control, and reporting reductions in waiting time and queue length. [PMC, "IoT-Simulated Digital Twin with AI Traffic Signal Control for Real-Time Traffic Optimization in SUMO," 2026; also published in MDPI Sensors, 2026]

This same study explicitly notes that simulation experiments can assume near-perfect information, while real sensors introduce noise, latency, and occlusion — a caveat directly relevant to our robustness experiments (`45_ROBUSTNESS_TESTING.md`). [MDPI Sensors, 2026]

**Implication for NexusTwin**: "Digital Twin + SUMO + Q-learning" has already been demonstrated — this combination alone is not sufficient novelty.

## 4. Edge–Cloud Digital Twin Architectures

A June 2026 paper proposes an edge-cloud Digital Twin traffic framework (GEC-DTSP) combining Graph Convolutional Networks (GCN), LSTM, and Transformer-based forecasting with Digital Twin synchronization and deep reinforcement learning for adaptive signal control, reporting a 17% reduction in average vehicle waiting time. [PLOS One, "GEC-DTSP: A GNN–RL-based Edge–Cloud Digital Twin framework for real-time traffic forecasting and adaptive signal control," 2026]

**Implication for NexusTwin**: We cannot claim to be first to combine edge AI, Digital Twin, and RL for traffic — that combination already exists and is well documented.

## 5. Advancing ITS via Digital Twin — Challenges and Future Directions

A broader review of Digital Twin applications in transportation discusses current challenges, modeling approaches, and future prospects, and identifies data fusion, edge computing, virtual modeling, and edge-cloud collaboration as key enabling technologies. [ScienceDirect, "Advancing intelligent transportation through digital twin: Challenges, models, and future prospects," 2025]

## 6. Edge Computer Vision for Vehicle Detection

Recent work on lightweight/edge-deployable object detection (improved YOLO variants) targets real-time vehicle detection specifically for edge computing scenarios, supporting the feasibility of running detection locally at each camera node rather than streaming raw video to a central server. [Springer, "Real-time vehicle detection methods based on an improved YOLO-Lite approach in edge computing scenarios," Discover Artificial Intelligence, 2026]

## 7. Simulation Tooling — SUMO

SUMO (Simulation of Urban MObility) supports importing real road geometry from OpenStreetMap, synthetic and observation-based demand generation, and closed-loop online control of a running simulation via the TraCI interface — retrieving simulation values and injecting actions mid-run. [Eclipse SUMO official documentation: OpenStreetMap import; Trip/demand generation tools; Routes from Observation Points; TraCI interface documentation]

**Implication for NexusTwin**: SUMO + OSM + TraCI is a credible, well-documented foundation for building both the physical/simulated network and the Digital Twin's synchronized copy, and for implementing the Scenario Engine's "simulate before you act" loop.

## Summary Table

| Theme | What exists | What NexusTwin adds |
|---|---|---|
| Adaptive signal control (RL/DL/GNN/fuzzy) | Extensive, 400+ papers reviewed | Not our novelty claim |
| Digital Twin + SUMO + Q-learning | Demonstrated (2026) | Not our novelty claim alone |
| Edge-cloud DT + GCN/LSTM/Transformer + RL | Demonstrated, 17% waiting-time reduction (2026) | Not our novelty claim alone |
| DT-ITS architecture reviews | Establishes DT as visualization + simulation + prediction + control | We treat the Twin specifically as a **decision-validation layer**, not primarily a visualization |
| Edge vehicle detection (YOLO-Lite) | Establishes edge feasibility | We use this as the perception layer feeding our Scenario Engine |
| SUMO/OSM/TraCI | Mature tooling | Foundation for our Twin + closed-loop Scenario Engine |

See `06_RESEARCH_GAP.md` for the explicit gap analysis and `07_NOVELTY_AND_CONTRIBUTIONS.md` for what we claim as original.

## References

1. Ge et al., "Digital twin intelligent transportation system (DT-ITS) — A systematic review," *IET Intelligent Transport Systems*, 2024.
2. "A comprehensive review of artificial intelligence techniques for traffic signal control in intelligent transportation systems," *Discover Applied Sciences* (Springer Nature), 2026.
3. "IoT-Simulated Digital Twin with AI Traffic Signal Control for Real-Time Traffic Optimization in SUMO," *PMC / MDPI Sensors*, 2026.
4. "GEC-DTSP: A GNN–RL-based Edge–Cloud Digital Twin framework for real-time traffic forecasting and adaptive signal control," *PLOS One*, 2026.
5. "Advancing intelligent transportation through digital twin: Challenges, models, and future prospects," *ScienceDirect*, 2025.
6. "Real-time vehicle detection methods based on an improved YOLO-Lite approach in edge computing scenarios," *Discover Artificial Intelligence* (Springer Nature), 2026.
7. Eclipse SUMO Documentation — OpenStreetMap import, Trip generation, Routes from Observation Points, TraCI interface. https://sumo.dlr.de/docs/

> Note: Some source links were accessed via a research assistant pass and should be re-verified with direct searches before final submission, since publication metadata (dates, volume numbers) can shift.
