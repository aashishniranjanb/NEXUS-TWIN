# NEXUS-TWIN — Friend 1 (Web Platform Lead)
## Branch: `feature/web-platform`

---

## Your job in one sentence
Build the NEXUS-TWIN browser Command Center that displays live AI predictions,
4-future Digital Twin comparisons, and lets a user approve or override decisions
through a browser — no Unity installation required.

---

## Setup (5 minutes)

```powershell
# Clone the repo
git clone https://github.com/aashishniranjanb/NEXUS-TWIN
cd NEXUS-TWIN

# Switch to your branch
git checkout feature/web-platform

# Start the backend (needed for live mode)
cd backend
pip install -r requirements.txt
python -m uvicorn api.main:app --reload --port 8000

# Open web/index.html in browser  (static mode — no server needed)
# OR serve it:
cd web
python -m http.server 3000
# Open http://localhost:3000
```

---

## What you own

```
web/
├── index.html        ← main page
├── style.css         ← styling
├── app.js            ← all JavaScript logic
└── components/       ← optional: split into components
```

---

## What to build (priority order)

### 1. Traffic Map Panel
Show J1, J2, J3 junctions as nodes with live queue indicators.
Color: green (OK) → amber (warning) → red (critical).

### 2. AI Alert Panel
Display:
```
CONGESTION ALERT
Junction: J2
Risk: 87%
Confidence: 82%
Forecast: 5 min
AI Recommendation: DIVERT TRAFFIC
```

### 3. Strategy Cards (4 futures)
Display all 4 strategies side-by-side:
```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ GREEN    │ │ DIVERT   │ │ EMERGENC │ │ NO ACTION│
│ -12.4%  │ │ -37.6%   │ │ +8.0%    │ │ +45.0%   │
│ ETA +4s  │ │ ETA -24s │ │ ETA -31s │ │ ETA +24s │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
         ★ AI recommends DIVERT
```

### 4. XAI Explanation Panel
Show the explanation text from `/strategy/evaluate`.

### 5. Human Decision
Two buttons:
```
[APPROVE AI RECOMMENDATION]   [OVERRIDE — MY DECISION]
```

### 6. Mission Timer + Score
Show the live timer and score bars.

---

## API endpoints to use

```javascript
// Check backend is alive
GET http://localhost:8000/health

// Get traffic state
GET http://localhost:8000/traffic/state

// Get AI prediction
GET http://localhost:8000/traffic/prediction?junction_id=J2

// Get all 4 strategy futures + XAI
POST http://localhost:8000/strategy/evaluate
Body: { "junction_id": "J2", "strategies": ["extend_green","diversion","emergency_priority","do_nothing"] }

// Apply chosen strategy
POST http://localhost:8000/strategy/apply
Body: { "junction_id": "J2", "strategy": "diversion" }
```

If backend is offline, fall back to **mock JSON** (see below).

---

## Mock data (use when backend is offline)

```javascript
const MOCK_STATE = {
  junction: "J2",
  congestion_probability: 0.87,
  forecast_minutes: 5,
  confidence: 0.82,
  recommended_strategy: "diversion",
  strategies: [
    { name: "extend_green",       label: "Extend Green Phase",     delay_change_pct: -12.4, queue_change_pct: -18.2, emergency_eta_change_sec: 4,   isBest: false },
    { name: "diversion",          label: "Divert Traffic",         delay_change_pct: -37.6, queue_change_pct: -30.1, emergency_eta_change_sec: -24,  isBest: true  },
    { name: "emergency_priority", label: "Emergency Priority",     delay_change_pct:  +8.0, queue_change_pct: +12.0, emergency_eta_change_sec: -31,  isBest: false },
    { name: "do_nothing",         label: "No Action (Baseline)",   delay_change_pct: +45.0, queue_change_pct: +62.0, emergency_eta_change_sec: +24,  isBest: false }
  ],
  explanation: {
    action: "Divert Traffic via Cross Street East/West bypass",
    reason: "Prevents J2 corridor gridlock and guarantees clearance for AMBULANCE_01.",
    evidence: "XGBoost confirms 87% bottleneck risk. Diversion reduces queue length by 30% without spillback.",
    confidence: 0.92
  }
};
```

---

## Style guide (match Aashish's Unity UI)

```css
:root {
  --bg:         #F5F6F8;
  --navy:       #0E1424;
  --green:      #39E75F;
  --red:        #D94040;
  --amber:      #F2B84B;
  --cyan:       #00E5FF;
  --panel-bg:   #FFFFFF;
  --border:     #DDE2EC;
  --font:       'IBM Plex Mono', monospace;
}
```

---

## Success criteria

Someone opens the browser and within 10 seconds can:
1. See traffic status at J1/J2/J3
2. See the AI alert (87% risk)
3. Compare all 4 strategy futures
4. Read the XAI explanation
5. Click Approve or Override

That's your deliverable.

---

## Do NOT touch

```
game/unity/        ← Aashish only
intelligence/      ← Friend 2 only
simulation/        ← Friend 2 only
backend/api/main.py  ← read the endpoints, don't change them
```

---

## Daily git workflow

```powershell
# Start of day
git checkout feature/web-platform
git merge main

# Work...

# End of day
git add web/
git commit -m "feat(web): [what you did]"
git push origin feature/web-platform
```

Then message Aashish to review your PR.
