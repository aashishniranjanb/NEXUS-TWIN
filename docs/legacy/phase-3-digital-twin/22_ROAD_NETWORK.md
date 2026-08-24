# 22 — Road Network

## Goal
Select and prepare the **one real (or realistic) road network** the whole prototype will run on, per the scope defined in `10_SCOPE_AND_NON_SCOPE.md`: **3–5 junctions**.

## Selection Criteria

- Small enough to keep SUMO simulation and Scenario Engine evaluation fast (needed for a live demo — see `46_LATENCY_ANALYSIS.md`).
- Contains at least one clear **arterial + side-road** structure, so diversion/dynamic-lane strategies are meaningful (a single straight road has no interesting alternative routes).
- Ideally recognizable/local (e.g., a real corridor near the team, such as a stretch in Chennai) so the demo narrative ("here is a real place") is stronger — optional but preferred over a synthetic grid.
- Avoids extremely complex intersections (multi-lane roundabouts, highway interchanges) that would take disproportionate setup time for limited demo value.

## Workflow: OpenStreetMap → SUMO

```text
1. Identify the target area on OpenStreetMap (openstreetmap.org),
   export or note the bounding box (lat/lon).
2. Use SUMO's OSM import tooling (netconvert / osmWebWizard) to
   convert the OSM extract into a SUMO .net.xml network.
3. Visually inspect the imported network in sumo-gui:
      - Confirm junction count matches expectations (3–5).
      - Confirm lane connectivity looks sane (no broken turns).
      - Simplify/clean if the import brought in unnecessary detail
        (e.g., footpaths, unrelated minor roads) — netconvert
        options can filter road types.
4. Save the cleaned network as simulation/network/nexustwin.net.xml
```

SUMO officially supports importing real road networks from OpenStreetMap, which is the basis for this workflow (see `04_RESEARCH_LITERATURE.md`, reference 7, and `11_TECH_STACK.md`).

## Fallback: Synthetic Network
If a suitable real network cannot be cleanly imported in time, fall back to a **hand-built synthetic grid/arterial network** using SUMO's `netgenerate` tool (e.g., a 4-junction grid or a linear arterial with 2 side streets). This is an acceptable substitute — the research contribution (`07_NOVELTY_AND_CONTRIBUTIONS.md`) does not depend on the network being real, only on the *architecture* being sound. If this fallback is used, it should be stated plainly rather than implied to be a real corridor.

## Deliverables of This Document/Task

- `simulation/network/nexustwin.net.xml` — the finalized network file.
- A short written description (below) of the chosen network's structure, to be reused in `56_DEMO_SCRIPT.md` and pitch materials.

## Network Description (to be filled in once finalized)

```text
Name:            <corridor name>
Junctions:       <count, IDs>
Arterial roads:  <description>
Side roads:      <description>
Alternative routes available for diversion strategy: <yes/no, which>
Approx. length:  <meters>
```

## Dependencies
- Feeds directly into `23_TRAFFIC_DEMAND_MODEL.md` (routes need a finalized network) and `24_TRAFFIC_SIGNAL_MODEL.md` (signal definitions attach to this network's junctions).
