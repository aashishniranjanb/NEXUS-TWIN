# 20 — Security & Ethics

## Why This Document Exists
NexusTwin's real-world framing touches CCTV-style perception, vehicles, public infrastructure, and AI-driven decision-making. Even though the prototype is simulation-only (`10_SCOPE_AND_NON_SCOPE.md`), the design should hold up if judges or reviewers ask "how would this behave responsibly at scale?" This document is also the natural home for addressing the **Responsible & Explainable AI** track directly.

## Privacy

- **No facial recognition.** The Edge-AI Nodes classify vehicles (car/bus/truck/motorcycle), not people.
- **No license-plate storage or recognition.** Only aggregate counts, speeds, and queue estimates leave a node — see the Per-Node Traffic Metadata schema in `14_DATA_ARCHITECTURE.md`.
- **No raw video leaves the edge node** in the target architecture — only derived metadata is transmitted (`16_EDGE_AI_ARCHITECTURE.md`).
- Any demonstration video/footage used for the CV pipeline should avoid, where possible, footage with clearly identifiable individuals; if unavoidable (e.g., public traffic footage), this is disclosed as a data-source limitation in `48_LIMITATIONS.md`.

## Human Oversight

- NexusTwin is positioned as a **decision-support / recommendation system**, not an unattended autonomous controller — see the "Control / Operator Advice" stage in `12_SYSTEM_ARCHITECTURE.md`.
- The `/strategy/evaluate` vs `/strategy/apply` API split (`17_API_SPECIFICATION.md`) is a deliberate design choice enforcing that a recommendation is always visible and separable from an action.
- In the real-world framing, the design assumes a human operator remains in the loop for consequential actions; the competition prototype's "player" role is a deliberate proxy for this human-in-the-loop framing.

## Explainability as a Safety Feature

- Every recommendation includes action, reason, expected impact, and confidence (`37_EXPLAINABLE_AI.md`) specifically so that a human (operator or player) can evaluate — and reject — a recommendation, not just receive it.
- Low-confidence recommendations should be visually/textually flagged as such in the UI (`54_UI_UX_SPECIFICATION.md`) rather than presented with false certainty.

## Safety Constraints (Design-Level)

- The Scenario Engine never applies a candidate strategy directly to the reference simulation — only the chosen, scored candidate is applied, and only after evaluation (`19_SIMULATION_ARCHITECTURE.md`).
- Emergency-vehicle-priority strategies are explicitly weighted in the optimization score (`38_EMERGENCY_PRIORITY.md`) rather than treated as an equal-priority option, reflecting real safety priorities.
- The system is explicitly described (including to judges) as a **simulation/testbed**, and this framing is repeated consistently across `10_SCOPE_AND_NON_SCOPE.md`, `48_LIMITATIONS.md`, and pitch materials (`57_MASATHON_PITCH.md`) — this consistency matters for credibility.

## Data Handling in the Prototype

- All data generated/used in the hackathon build is synthetic (SUMO-generated) or drawn from public traffic footage/datasets used only for demonstrating the CV pipeline, not for any production use.
- No persistent personal data is collected, stored, or required for the system to function.
- Database schema (`18_DATABASE_SCHEMA.md`) contains no personally identifying fields by design.

## Known Ethical/Trust Risks to Acknowledge (not hide)

- **Over-trust risk**: a fluent explanation can make a wrong recommendation seem more trustworthy than it is — mitigated by showing confidence and by explicitly not fabricating results (`24_...`/`43_BASELINE_COMPARISON.md`: "no fabricated numbers").
- **Equity risk**: network-level optimization could, in a real deployment, systematically favor some routes/areas over others — flagged as a real-world consideration for future work in `48_LIMITATIONS.md`, not something the hackathon prototype claims to solve.
- **Simulation-to-reality gap**: sensor noise, latency, and occlusion are real-world issues that simulation can understate — directly tested via `45_ROBUSTNESS_TESTING.md` rather than ignored.

## Summary Statement (for pitch use)

> NexusTwin is designed as an explainable, human-overseen decision-support layer, not an autonomous controller. It processes only aggregate, non-identifying traffic metadata, keeps recommendation and action explicitly separate, and is presented — honestly — as a simulation/testbed rather than a production traffic-control system.
