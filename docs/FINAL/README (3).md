# NEXUS-TWIN

**AI Urban Traffic Intelligence** — a decision-support command center that detects abnormal
traffic behaviour, classifies it, predicts congestion five minutes ahead, forecasts where that
congestion will spread, generates constrained intervention strategies, tests them in a Digital
Twin, and presents an explainable recommendation for a human operator to approve or override.

Primary dataset: **BigQuery-Geotab Intersection Congestion Dataset**.

---

## The core pipeline

```
Geotab traffic data
  -> Feature engineering
  -> Current traffic state
  -> Anomaly detection
  -> Traffic fingerprint
  -> 5-minute prediction
  -> Congestion domino effect
  -> Intervention window
  -> Strategy generation
  -> Digital Twin simulation
  -> Strategy comparison
  -> Explainable recommendation
  -> Human decision
  -> Outcome evaluation
```

Every document in `docs/` describes some part of this single pipeline. Nothing in this repository
should exist that does not serve it.

---

## Read this first

| Order | Document | Who must read it |
|---|---|---|
| 1 | [`docs/00_MASTER_PROJECT_SPEC.md`](docs/00_MASTER_PROJECT_SPEC.md) | Everyone |
| 2 | [`docs/01_PRODUCT/PRD.md`](docs/01_PRODUCT/PRD.md) | Everyone |
| 3 | [`docs/03_ARCHITECTURE/TECH_STACK.md`](docs/03_ARCHITECTURE/TECH_STACK.md) | Everyone |
| 4 | [`docs/04_API/API_DATA_CONTRACTS.md`](docs/04_API/API_DATA_CONTRACTS.md) | Everyone |
| 5 | [`docs/10_IMPLEMENTATION/IMPLEMENTATION_MASTER_PLAN.md`](docs/10_IMPLEMENTATION/IMPLEMENTATION_MASTER_PLAN.md) | Everyone |

Then read the documents owned by your laptop (see the ownership table in the master spec).

---

## Documentation map

```
docs/
├── 00_MASTER_PROJECT_SPEC.md        Single source of truth
├── 01_PRODUCT/
│   ├── PRD.md                       What the product does, screen by screen
│   └── PROBLEM_STATEMENT.md         Competition requirement mapping
├── 02_RESEARCH/
│   └── DATASET_SPECIFICATION.md     Geotab schema, columns, limits
├── 03_ARCHITECTURE/
│   ├── TECH_STACK.md                Frozen stack
│   ├── SYSTEM_ARCHITECTURE.md       Runtime topology
│   ├── AI_ARCHITECTURE.md           Models and how they connect
│   └── AGENT_ARCHITECTURE.md        LangGraph, 5 agents
├── 04_API/
│   ├── API_SPECIFICATION.md         Endpoints, requests, responses
│   ├── API_DATA_CONTRACTS.md        Shared types (the anti-collision file)
│   └── AGENT_TOOL_CONTRACTS.md      Tools the LLM may call
├── 05_DATA/
│   ├── DATA_PIPELINE.md             Geotab CSV to Command Center
│   └── DATA_PROVENANCE.md           Evidence the dataset is real
├── 06_AI/
│   ├── TRAFFIC_FINGERPRINT.md       Anomaly classification
│   ├── DOMINO_EFFECT.md             Spillover propagation
│   ├── STRATEGY_ENGINE.md           Constrained strategy catalogue
│   └── EXPLAINABLE_AI.md            Evidence, confidence, trade-offs, safety
├── 07_SIMULATION/
│   └── DIGITAL_TWIN_SPEC.md         What-if simulation
├── 08_FRONTEND/
│   └── FRONTEND_ARCHITECTURE.md     Command Center components
├── 09_DATABASE/
│   └── DATABASE_SCHEMA.md           PostgreSQL tables
├── 10_IMPLEMENTATION/
│   └── IMPLEMENTATION_MASTER_PLAN.md  Phases 0-7, timeboxed
├── 12_DEVOPS/
│   └── GIT_WORKFLOW.md              Branches, PRs, merge rules
└── 13_HACKATHON/
    └── JUDGE_DEMO_SCRIPT.md         The five-minute demo, line by line
```

Documents not yet written are Level-2 subsystem specs. They are listed in the master spec under
"Documentation status" and are not required before implementation begins.

---

## Scope discipline

The single largest risk to this project is building twenty features that are sixty percent
finished. The priority is fixed:

- **P0** — must work: prediction, anomaly + fingerprint, domino effect, Digital Twin, explainable
  recommendation, human decision.
- **P1** — only after every P0 item works end to end: LangGraph orchestration, AI Copilot,
  3D Digital Twin, SSE, AI-vs-Human comparison, Emergency Corridor.
- **P2** — do not start: Redis, Celery, WebSockets, authentication, Sentry, Prometheus, Grafana,
  advanced SUMO, RBAC.

A smaller number of completely working features beats many partially implemented ones.

---

## Repository layout

```
apps/web/            Next.js Command Center (Laptop 3)
services/api/        FastAPI (Laptop 2)
ai/                  Models: prediction, anomaly, fingerprint, domino, strategy (Laptop 1)
agents/              LangGraph orchestration (Laptop 2, P1)
simulation/          Digital Twin engine; SUMO network files (Laptop 2)
database/            Migrations and seeds (Laptop 2)
shared/contracts/    TypeScript + Pydantic types — changed only by agreement
data/                raw/ processed/ samples/
tests/
docs/
```

An earlier Unity prototype exists under `game/unity/`. It is a backup demonstration only. Do not
modify it, and do not let it block the web build.
