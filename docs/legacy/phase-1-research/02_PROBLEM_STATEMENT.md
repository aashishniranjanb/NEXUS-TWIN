# 02 — Problem Statement

## Background

Urban traffic congestion is a persistent, worsening problem in fast-growing cities. Intelligent Transportation Systems (ITS) have progressively added cameras, sensors, and adaptive signal controllers to detect and respond to congestion. Over the last few years, research has moved toward AI-driven signal control (reinforcement learning, deep learning, evolutionary algorithms) and, more recently, toward Digital Twins that simulate the road network in parallel with the physical system.

## Current Problem

Existing deployed systems are largely **reactive and locally scoped**:

- Fixed-time signals do not respond to real conditions at all.
- Actuated/adaptive signals respond to *local* sensor input at a single junction.
- Even AI-driven adaptive controllers typically optimize the junction (or a small cluster) they observe, without verifying the effect on the wider network.

This creates a well-known failure mode: an intervention that looks good locally (e.g., a junction's queue shrinks) can simply **displace** the congestion to a downstream or neighboring junction, sometimes making the network as a whole worse.

## Technical Problem

There is no lightweight, explainable mechanism that:

1. Reconstructs the *current* state of a road network from distributed observations,
2. Forecasts how that state is about to change,
3. **Tests multiple candidate interventions inside a simulated copy of the network before deployment**, and
4. Selects the intervention that improves *network-wide* outcomes — not just the outcome at the junction under observation — while explaining that choice in terms a human operator can evaluate.

## Research Problem

> Can a continuously synchronized Digital Twin evaluate multiple traffic-control strategies before deployment and select an intervention that reduces network-wide congestion, delay, and environmental impact — without simply shifting congestion to neighboring roads — while remaining explainable and robust to imperfect sensor data?

## Impact

- **Commuters**: reduced travel time and unpredictability.
- **City operators**: a decision-support layer instead of a black-box controller; interventions are evaluated for network-wide effect before use, reducing the risk of a "fix" that just moves the problem.
- **Emergency services**: faster, quantified emergency corridor response.
- **Environment**: reduced idling/congestion-related emissions.
- **Research community**: a testbed and set of experiments (fixed-time vs reactive vs predictive vs network-level optimization) that are reproducible in SUMO.

## Problem Statement (Final)

> Urban traffic management systems predominantly operate through reactive monitoring and localized control. Traffic cameras and sensors can detect congestion, and adaptive signal controllers can modify traffic signals, but determining whether a proposed intervention will improve the wider road network remains difficult. A local optimization may reduce congestion at one junction while transferring the queue to another junction, creating downstream spillback. Direct experimentation on live traffic infrastructure is also risky and costly. There is therefore a need for a predictive decision layer that can reconstruct the current traffic state, simulate alternative interventions in a virtual representation of the road network, quantify their network-wide consequences, and recommend an explainable action before deployment.

## Research Question

> Can a continuously synchronized Digital Twin evaluate multiple traffic-control strategies before deployment and select an intervention that reduces network-wide congestion, delay, and environmental impact without simply shifting congestion to neighboring junctions?

See `08_OBJECTIVES_AND_HYPOTHESES.md` for the secondary research questions and formal hypotheses (H1–H4) derived from this problem statement.
