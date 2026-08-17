# 01 — Product Requirements Document (PRD)

## Project Name
**NexusTwin** — *A Predictive Digital Twin for AI-Driven Network-Level Traffic Management*

Competition name: **NexusTwin: Traffic Command**

## Vision
Urban traffic authorities today can *see* congestion and can *react* to it locally, but they have no safe, fast way to test whether an intervention will actually help the wider road network before deploying it. NexusTwin's vision is to give a traffic operator (in the real system) or a player (in the competition prototype) a **synchronized virtual city** that can be used to simulate, compare, and explain interventions before they are applied to the physical/simulated network.

## Problem (Summary)
Traffic control systems generally operate as:

`Detect → Predict → Control`

This is reactive and locally optimized: fixing one junction can silently push congestion onto a neighboring junction (spillback). Testing new signal strategies directly on live infrastructure is risky and expensive, and there is no fast feedback loop between "we changed something" and "did the whole network actually improve."

NexusTwin reframes this as:

`Detect → Predict → Simulate Futures → Compare → Decide → Validate → Control`

## Target Users

| User type | Context |
|---|---|
| Traffic control room operator | Real-world framing — needs a decision-support tool, not a black box |
| City planning / ITS researcher | Wants to evaluate strategies without touching live infrastructure |
| MASATHON judges / players | Competition framing — experiences the same engine as an interactive game |
| Our own team | Needs a system that is genuinely demonstrable within an 8-hour build window |

## Proposed Solution
A Digital Twin of a small (3–5 junction) road network, built in **SUMO**, fed by simulated/edge-AI traffic perception, that:

1. Reconstructs the current traffic state.
2. Predicts short-term congestion.
3. Generates several candidate interventions (signal timing change, diversion, dynamic lane, emergency priority).
4. **Simulates each candidate inside the Twin before recommending it.**
5. Selects the intervention with the best network-wide outcome (not just the best local outcome).
6. Explains *why* that intervention was chosen.
7. In the competition build, this becomes a playable loop where the player is the "Traffic Intelligence Operator."

## Core Features

- Distributed edge-AI traffic perception (simulated via YOLO on traffic video / synthetic SUMO data)
- Central Traffic Intelligence Hub (state fusion + prediction)
- Digital Twin (SUMO + TraCI, continuously synchronized state)
- Scenario Engine (parallel "what-if" simulation of candidate strategies)
- Optimization layer (deterministic scoring first; RL as a stretch goal)
- Explainable AI output (action, reason, expected impact, confidence)
- Procedural incident generator (accidents, surges, road closures, weather, emergencies)
- Game layer: scenario-based play loop, scoring, level progression

## Functional Requirements

1. System shall ingest or simulate traffic-state data per junction (vehicle counts, speed, queue length).
2. System shall maintain a Digital Twin whose state is kept in sync with the observed/simulated network.
3. System shall forecast short-term congestion (e.g., 5–10 minutes ahead).
4. System shall generate at least 3–4 candidate interventions per decision point.
5. System shall simulate each candidate inside the Twin and compute comparable metrics (delay, queue, throughput, emissions, emergency response time).
6. System shall select and apply/recommend the intervention with the best network-level score.
7. System shall output a human-readable explanation for the chosen intervention.
8. System shall support procedurally generated incidents that alter the traffic state mid-run.
9. (Competition build) System shall expose the above as an interactive, playable interface with scoring.

## Non-Functional Requirements

- **Explainability**: every AI decision must be traceable to a reason and a quantified expected impact.
- **Safety framing**: the prototype is explicitly a simulation/testbed, not a live traffic controller.
- **Reproducibility**: experiments must be runnable from a clean clone (see `49_REPRODUCIBILITY.md`).
- **Scope discipline**: prototype targets a small representative network, not a full city (see `10_SCOPE_AND_NON_SCOPE.md`).
- **Performance**: scenario evaluation for a decision point should complete within a few seconds in the demo build.

## User Journeys

**Real-world framing:**
Operator sees rising congestion → system predicts gridlock in ~5 minutes → operator (or system) requests options → Twin simulates 3–4 strategies → system recommends best network-level action with reasoning → operator applies it → outcome is monitored.

**Competition framing:**
Player opens a scenario ("08:45 — Morning Rush") → an incident fires (e.g., accident) → player is shown candidate actions (A–D) → player presses **SIMULATE** → Twin evaluates all options → system shows expected impact per option → player chooses → city state updates → score is computed → next event.

## Success Criteria

- A working SUMO network with fixed-time baseline running end-to-end.
- A functioning Scenario Engine that can simulate ≥3 candidate strategies and rank them.
- Demonstrated, measured improvement of NexusTwin's strategy selection over a fixed-time and a simple reactive baseline (see `43_BASELINE_COMPARISON.md`).
- A playable interface implementing the gameplay loop with at least 3 scenario types and procedural incidents.
- A clear, honest explanation layer for every AI recommendation.

## Constraints

- 8-hour offline build window for Round 2, if shortlisted.
- Small team (2–4 members).
- No claim of real-world deployment or live signal control — simulation-only.
- Must remain within the chosen track(s) requirements of MASATHON 2026.

## Competition Requirements (Reference)

- **Event**: IEEE MASATHON 2026 (IEEE Computer Society AU-CEG & IEEE Madras Section).
- **Round 1**: Online concept submission — original game concept (story, gameplay mechanics, tech stack, development plan, team roles), submitted as PPT or video pitch only, by **16 August 2026**.
- **Round 2**: 8-hour offline prototype build for shortlisted teams — must be functional, playable, and demonstrated live; source code and documentation required.
- **Team size**: 2–4 members, cross-college/interdisciplinary encouraged.
- **Primary track**: Generative AI & Intelligent Game Systems.
- **Secondary tracks**: Computer Vision & Perception; Responsible & Explainable AI.
- Original contribution required — no plagiarism/copied projects; AI tools and public libraries allowed with disclosure where required.
