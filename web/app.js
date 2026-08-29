/**
 * NEXUS-TWIN P2 Decision Support Command Center Web Application
 * Implements: Counterfactual Futures Simulation, Multi-Objective Optimizer Evaluation,
 * Grounded Explainability, Human Operator Decision State Machine (Approve/Reject/Try Another),
 * and Applied Strategy Result Transition.
 */

// API Base Configuration
const API_BASE = "http://localhost:8000/api";

// Decision State Machine Definitions
const DECISION_STATES = {
    IDLE: "IDLE",
    TRIGGERED: "TRIGGERED",
    EVALUATING: "EVALUATING",
    EVALUATED: "EVALUATED",
    RECOMMENDED: "RECOMMENDED",
    AWAITING_HUMAN: "AWAITING_HUMAN",
    APPROVED: "APPROVED",
    REJECTED: "REJECTED",
    APPLIED: "APPLIED",
    MONITORING: "MONITORING"
};

// Central P2 Application State
const appState = {
    selectedJunction: "J2",
    connectionStatus: "CHECKING", // "ONLINE" | "DEMO_MODE" | "RECONNECTING"
    lastUpdated: new Date(),
    isDemoScenario: false,
    
    // Decision State Machine
    decisionState: DECISION_STATES.AWAITING_HUMAN,
    selectedCandidateId: "cand_dynamic_lane",
    appliedStrategy: null,

    // Layer visibility toggles
    layers: {
        traffic: true,
        prediction: true,
        anomaly: true,
        spillover: true
    },

    // Normalized Traffic State
    traffic: {
        networkSpeedKmh: 38.4,
        totalVehicles: 128,
        totalQueueMeters: 26.5,
        avgWaitingTimeSeconds: 0.28,
        junctions: {
            J1: { id: "J1", name: "J1 (Westbound Inflow)", status: "normal", queueMeters: 18.0, speedKmh: 42.0, isGreen: true, vehicleCount: 42, anomalyScore: 0.08, anomalyStatus: "normal" },
            J2: { id: "J2", name: "J2 (Central Hub)", status: "critical", queueMeters: 61.0, speedKmh: 18.0, isGreen: false, vehicleCount: 58, anomalyScore: 0.91, anomalyStatus: "critical" },
            J3: { id: "J3", name: "J3 (Eastbound Exit)", status: "warning", queueMeters: 34.0, speedKmh: 29.0, isGreen: true, vehicleCount: 28, anomalyScore: 0.42, anomalyStatus: "warning" }
        }
    },
    
    // Normalized AI Predictions per Junction
    predictions: {
        J1: { junctionId: "J1", congestionProbability: 0.24, forecastMinutes: 5, confidence: 0.88, riskLevel: "low", predictedQueueGrowth: "+2.0 m", fingerprint: "NORMAL FLOW", fpConfidence: 0.95, fpSeverity: "normal", evidence: [{ metric: "Flow Balance", value: "98%", dir: "nominal" }, { metric: "Queue Speed", value: "42 km/h", dir: "stable" }] },
        J2: { junctionId: "J2", congestionProbability: 0.87, forecastMinutes: 5, confidence: 0.82, riskLevel: "critical", predictedQueueGrowth: "+34.0 m", fingerprint: "RAPID QUEUE BUILD-UP", fpConfidence: 0.89, fpSeverity: "critical", evidence: [{ metric: "Queue Growth Rate", value: "+34% / min", dir: "increasing" }, { metric: "Speed Collapse", value: "18.0 km/h", dir: "decreasing" }, { metric: "Wait Time Anomaly", value: "0.52s", dir: "elevated" }] },
        J3: { junctionId: "J3", congestionProbability: 0.52, forecastMinutes: 5, confidence: 0.79, riskLevel: "warning", predictedQueueGrowth: "+11.0 m", fingerprint: "RECURRING CONGESTION", fpConfidence: 0.84, fpSeverity: "warning", evidence: [{ metric: "Downstream Drag", value: "+12% / min", dir: "increasing" }, { metric: "Exit Speed", value: "29.0 km/h", dir: "moderate" }] }
    },

    // Counterfactual Candidate Futures (Evaluated by Digital Twin Scenario Engine)
    candidates: [
        {
            id: "cand_dynamic_lane",
            type: "dynamic_lane",
            name: "Activate Dynamic Lane",
            rank: 1,
            score: 21.4,
            delayDeltaPct: -34,
            queueDeltaPct: -28,
            throughputDeltaPct: +24,
            spillback: "LOW",
            emergencySafety: "SAFE",
            isRecommended: true,
            isBaseline: false,
            success: true,
            explanation: "Dynamic lane at J2 relieves eastbound backlog without diverting overflow onto residential connectors. Best network score (21.4)."
        },
        {
            id: "cand_diversion",
            type: "diversion",
            name: "30% Traffic Diversion",
            rank: 2,
            score: 27.8,
            delayDeltaPct: -31,
            queueDeltaPct: -25,
            throughputDeltaPct: +16,
            spillback: "MODERATE (J3 +8%)",
            emergencySafety: "SAFE",
            isRecommended: false,
            isBaseline: false,
            success: true,
            explanation: "Diverts flow to arterial routes, but incurs minor downstream queue displacement near J3."
        },
        {
            id: "cand_green_extend",
            type: "green_extend",
            name: "Extend Green (+20s)",
            rank: 3,
            score: 34.2,
            delayDeltaPct: -18,
            queueDeltaPct: -15,
            throughputDeltaPct: +10,
            spillback: "HIGH (J1 +18%)",
            emergencySafety: "WARNING (Cross street delay)",
            isRecommended: false,
            isBaseline: false,
            success: true,
            explanation: "Clears local J2 queue but starves north-south feeder movements, elevating J1 spillover risk."
        },
        {
            id: "cand_do_nothing",
            type: "do_nothing",
            name: "No Action (Baseline)",
            rank: 4,
            score: 52.1,
            delayDeltaPct: +4,
            queueDeltaPct: +12,
            throughputDeltaPct: -8,
            spillback: "CRITICAL (J2 -> J1 in 6 min)",
            emergencySafety: "UNSAFE (Gridlock in 8 min)",
            isRecommended: false,
            isBaseline: true,
            success: true,
            explanation: "Unmitigated queue buildup leads to complete corridor blockage and gridlock."
        }
    ],

    // Domino Propagation Paths
    domino: {
        sourceJunctionId: "J2",
        paths: [
            { source: "J2", target: "J1", probability: 0.73, estimatedMinutes: 4, direction: "UPSTREAM_WEST", severity: "high" },
            { source: "J2", target: "J3", probability: 0.41, estimatedMinutes: 7, direction: "DOWNSTREAM_EAST", severity: "moderate" }
        ]
    },

    // Time-Bounded Intervention Window
    interventionWindow: {
        sourceJunctionId: "J2",
        targetJunctionId: "J1",
        minutesRemaining: 6,
        confidence: 0.81,
        severity: "critical"
    },

    // Realtime Event Feed & Decision Audit Log (Newest first, max 5)
    events: [
        { id: 1, text: "Anomaly detected at J2 (Isolation Forest score: 0.91)", severity: "critical", time: "12:40:12" },
        { id: 2, text: "Digital Twin simulated 4 counterfactual futures for J2 decision point", severity: "success", time: "12:40:15" },
        { id: 3, text: "Multi-Objective Optimizer ranked Dynamic Lane as best candidate (Score: 21.4)", severity: "success", time: "12:40:18" },
        { id: 4, text: "AI Recommendation presented to operator. Awaiting authorization...", severity: "warning", time: "12:40:20" },
        { id: 5, text: "Intervention Window calculated: 06:00 min remaining before J1 spillover", severity: "warning", time: "12:40:24" }
    ]
};

// Canvas Setup
const canvas = document.getElementById("networkCanvas");
const ctx = canvas ? canvas.getContext("2d") : null;

// ==============================================================================
// 1. API ADAPTER & RESPONSE NORMALIZER
// ==============================================================================

async function fetchHealthCheck() {
    try {
        const res = await fetch(`${API_BASE}/health`, { method: "GET", signal: AbortSignal.timeout(2000) });
        if (res.ok) {
            setConnectionStatus("ONLINE");
            return true;
        }
    } catch (err) {
        setConnectionStatus("DEMO_MODE");
    }
    return false;
}

async function fetchTrafficIntelligence() {
    try {
        const res = await fetch(`${API_BASE}/evaluate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ junction_id: appState.selectedJunction, horizon_seconds: 300, strategy_type: "dynamic_lane" }),
            signal: AbortSignal.timeout(2500)
        });

        if (res.ok) {
            const data = await res.json();
            normalizeIntelligenceData(data);
            setConnectionStatus("ONLINE");
            return;
        }
    } catch (err) {
        setConnectionStatus("DEMO_MODE");
    }
}

function normalizeIntelligenceData(backendData) {
    if (!backendData) return;
    
    if (backendData.situation) {
        const s = backendData.situation;
        appState.traffic.avgWaitingTimeSeconds = s.avg_waiting_time_s || appState.traffic.avgWaitingTimeSeconds;
        appState.traffic.totalQueueMeters = s.queue_length_m || appState.traffic.totalQueueMeters;
        appState.traffic.networkSpeedKmh = s.avg_speed_kmh || appState.traffic.networkSpeedKmh;
        appState.traffic.totalVehicles = s.active_vehicles || appState.traffic.totalVehicles;
        
        const curJ = appState.traffic.junctions[appState.selectedJunction];
        if (curJ) {
            curJ.queueMeters = s.queue_length_m || curJ.queueMeters;
            curJ.speedKmh = s.avg_speed_kmh || curJ.speedKmh;
        }
    }

    appState.lastUpdated = new Date();
    updateUI();
}

function setConnectionStatus(status) {
    appState.connectionStatus = status;
    const dot = document.getElementById("backendStatusDot");
    const txt = document.getElementById("backendStatusText");
    const liveTag = document.getElementById("liveTag");

    if (status === "ONLINE") {
        if (dot) dot.className = "status-dot green";
        if (txt) txt.textContent = "SYSTEM ONLINE";
        if (liveTag) { liveTag.textContent = "LIVE TELEMETRY"; liveTag.className = "mode-tag"; }
    } else {
        if (dot) dot.className = "status-dot amber";
        if (txt) txt.textContent = "DEMO MODE (OFFLINE)";
        if (liveTag) { liveTag.textContent = "DEMO SIMULATION"; liveTag.className = "mode-tag amber-text"; }
    }
}

// ==============================================================================
// 2. UI RENDERING & DECISION STATE MACHINE
// ==============================================================================

function updateUI() {
    // 1. Global Metrics & Decision State
    const spdEl = document.getElementById("globalSpeed");
    const vehEl = document.getElementById("globalVehicles");
    const qEl = document.getElementById("globalQueue");
    const dlyEl = document.getElementById("globalDelay");
    const decStateEl = document.getElementById("globalDecisionState");

    if (spdEl) spdEl.textContent = `${appState.traffic.networkSpeedKmh.toFixed(1)} km/h`;
    if (vehEl) vehEl.textContent = `${appState.traffic.totalVehicles}`;
    if (qEl) qEl.textContent = `${appState.traffic.totalQueueMeters.toFixed(1)} m`;
    if (dlyEl) dlyEl.textContent = `${appState.traffic.avgWaitingTimeSeconds.toFixed(2)} s`;
    
    if (decStateEl) {
        if (appState.decisionState === DECISION_STATES.APPLIED) {
            decStateEl.textContent = `APPLIED (${appState.appliedStrategy.toUpperCase()})`;
            decStateEl.className = "metric-val green-text";
        } else if (appState.decisionState === DECISION_STATES.REJECTED) {
            decStateEl.textContent = "DECISION REJECTED (NO ACTION)";
            decStateEl.className = "metric-val amber-text";
        } else {
            decStateEl.textContent = "AWAITING HUMAN ACTION";
            decStateEl.className = "metric-val danger-text";
        }
    }

    // 2. Junction Cards
    ["J1", "J2", "J3"].forEach(jId => {
        const jData = appState.traffic.junctions[jId];
        const card = document.getElementById(`card${jId}`);
        const qVal = document.getElementById(`queue${jId}`);
        const spdVal = document.getElementById(`speed${jId}`);
        const sigVal = document.getElementById(`signal${jId}`);
        const statPill = document.getElementById(`status${jId}`);
        const anomVal = document.getElementById(`anom${jId}`);

        if (card) {
            if (appState.selectedJunction === jId) card.classList.add("selected-card");
            else card.classList.remove("selected-card");
        }
        if (qVal) qVal.textContent = `${jData.queueMeters.toFixed(1)} m`;
        if (spdVal) spdVal.textContent = `${jData.speedKmh.toFixed(1)} km/h`;
        if (sigVal) {
            sigVal.textContent = jData.isGreen ? "GREEN" : "RED";
            sigVal.className = jData.isGreen ? "val green-text" : "val red-text";
        }
        if (statPill) {
            statPill.textContent = jData.status.toUpperCase();
            statPill.className = `status-pill status-${jData.status}`;
        }
        if (anomVal) {
            if (jData.anomalyScore >= 0.8) {
                anomVal.textContent = `ABNORMAL (${jData.anomalyScore.toFixed(2)})`;
                anomVal.className = "val danger-text";
            } else if (jData.anomalyScore >= 0.3) {
                anomVal.textContent = `ELEVATED (${jData.anomalyScore.toFixed(2)})`;
                anomVal.className = "val amber-text";
            } else {
                anomVal.textContent = `None (${jData.anomalyScore.toFixed(2)})`;
                anomVal.className = "val green-text";
            }
        }
    });

    // 3. Counterfactual Futures Cards Grid
    const futureGrid = document.getElementById("futureCardsGrid");
    if (futureGrid) {
        futureGrid.innerHTML = "";
        appState.candidates.forEach(c => {
            const card = document.createElement("div");
            const isSelected = (c.id === appState.selectedCandidateId);
            card.className = `future-card ${c.isRecommended ? 'recommended-future' : ''} ${c.isBaseline ? 'baseline-future' : ''} ${isSelected ? 'selected-card' : ''}`;
            card.dataset.candidateId = c.id;
            
            let badgeHtml = "";
            if (c.isRecommended) badgeHtml = `<span class="future-badge badge-best">★ BEST</span>`;
            else if (c.isBaseline) badgeHtml = `<span class="future-badge badge-base">BASELINE</span>`;

            card.innerHTML = `
                ${badgeHtml}
                <div class="future-title">${c.name}</div>
                <div class="future-score-row">
                    <span>Rank #${c.rank}</span>
                    <strong class="${c.isRecommended ? 'green-text' : 'highlight'}">Score: ${c.score.toFixed(1)}</strong>
                </div>
                <div class="future-deltas">
                    <div class="delta-row">
                        <span class="lbl">Delay Delta:</span>
                        <strong class="${c.delayDeltaPct < 0 ? 'green-text' : 'danger-text'}">${c.delayDeltaPct > 0 ? '+' : ''}${c.delayDeltaPct}%</strong>
                    </div>
                    <div class="delta-row">
                        <span class="lbl">Queue Clearance:</span>
                        <strong class="${c.queueDeltaPct < 0 ? 'green-text' : 'danger-text'}">${c.queueDeltaPct > 0 ? '+' : ''}${c.queueDeltaPct}%</strong>
                    </div>
                    <div class="delta-row">
                        <span class="lbl">Spillback:</span>
                        <span style="font-size: 9.5px;" class="${c.spillback.includes('LOW') ? 'green-text' : 'amber-text'}">${c.spillback}</span>
                    </div>
                </div>
            `;
            
            card.addEventListener("click", () => {
                appState.selectedCandidateId = c.id;
                renderRecommendationForCandidate(c);
                updateUI();
            });

            futureGrid.appendChild(card);
        });
    }

    // 4. Recommendation & Explanation for Active Candidate
    const activeCand = appState.candidates.find(c => c.id === appState.selectedCandidateId) || appState.candidates[0];
    renderRecommendationForCandidate(activeCand);

    // 5. Domino Propagation Panel
    const dominoContainer = document.getElementById("dominoPathsGrid");
    if (dominoContainer) {
        dominoContainer.innerHTML = "";
        appState.domino.paths.forEach(p => {
            const card = document.createElement("div");
            card.className = "domino-path-card";
            const col = p.probability >= 0.6 ? "danger-text" : "amber-text";
            card.innerHTML = `
                <div class="domino-path-header">
                    <span>${p.source} &rarr; ${p.target} (${p.direction.replace('_', ' ')})</span>
                    <span class="domino-prob ${col}">${Math.round(p.probability * 100)}%</span>
                </div>
                <div class="domino-meta">Estimated Spillback: ~${p.estimatedMinutes} minutes to impact</div>
            `;
            dominoContainer.appendChild(card);
        });
    }

    // 6. Intervention Window Panel
    const iw = appState.interventionWindow;
    const iwBadge = document.getElementById("interventionTimeBadge");
    const iwSub = document.getElementById("interventionSub");
    const iwProgress = document.getElementById("interventionProgress");
    const iwDesc = document.getElementById("interventionDesc");

    if (iwBadge) iwBadge.textContent = `0${iw.minutesRemaining}:00 MIN`;
    if (iwSub) iwSub.textContent = `Before predicted spillover reaches ${iw.targetJunctionId}`;
    if (iwProgress) iwProgress.style.width = `${Math.min(100, (iw.minutesRemaining / 8) * 100)}%`;
    if (iwDesc) {
        iwDesc.innerHTML = `Origin at <strong class="danger-text">${iw.sourceJunctionId}</strong> has an estimated <strong>${iw.minutesRemaining} minutes</strong> before queue spillback cascades upstream into <strong class="amber-text">${iw.targetJunctionId}</strong>.`;
    }

    // 7. Fingerprint & Evidence Panel
    const curPred = appState.predictions[appState.selectedJunction] || appState.predictions.J2;
    const fpTarget = document.getElementById("fingerprintTarget");
    const fpLabel = document.getElementById("fingerprintLabel");
    const fpConf = document.getElementById("fingerprintConfidence");
    const fpSev = document.getElementById("fingerprintSeverity");
    const fpEvidence = document.getElementById("fingerprintEvidenceList");

    if (fpTarget) fpTarget.textContent = `Target: Junction ${appState.selectedJunction}`;
    if (fpLabel) fpLabel.textContent = curPred.fingerprint;
    if (fpConf) fpConf.textContent = `Confidence: ${Math.round(curPred.fpConfidence * 100)}% (Geotab Pattern Match)`;
    if (fpSev) {
        fpSev.textContent = curPred.fpSeverity.toUpperCase();
        fpSev.className = `status-pill status-${curPred.fpSeverity}`;
    }

    if (fpEvidence && curPred.evidence) {
        fpEvidence.innerHTML = "";
        curPred.evidence.forEach(ev => {
            const row = document.createElement("div");
            row.className = "evidence-item";
            row.innerHTML = `<span>${ev.metric}</span><strong class="highlight">${ev.value}</strong>`;
            fpEvidence.appendChild(row);
        });
    }

    // 8. Event Feed & Decision Audit Trail
    const feedContainer = document.getElementById("eventFeedList");
    if (feedContainer) {
        feedContainer.innerHTML = "";
        appState.events.slice(0, 5).forEach(ev => {
            const row = document.createElement("div");
            row.className = `event-feed-item ${ev.severity}`;
            row.innerHTML = `<span>${ev.text}</span><span class="event-time">${ev.time}</span>`;
            feedContainer.appendChild(row);
        });
    }

    // 9. Last Updated
    const lastUp = document.getElementById("lastUpdatedText");
    if (lastUp) {
        const secAgo = Math.max(0, Math.floor((Date.now() - appState.lastUpdated.getTime()) / 1000));
        lastUp.textContent = `Updated: ${secAgo}s ago`;
    }
}

function renderRecommendationForCandidate(cand) {
    const titleEl = document.getElementById("recStrategyTitle");
    const taglineEl = document.getElementById("recStrategyTagline");
    const delayEl = document.getElementById("recImpactDelay");
    const queueEl = document.getElementById("recImpactQueue");
    const spillEl = document.getElementById("recImpactSpillover");
    const safetyEl = document.getElementById("recImpactSafety");
    const expText = document.getElementById("recExplanationText");
    const confBadge = document.getElementById("recConfidenceBadge");

    if (titleEl) titleEl.textContent = cand.name.toUpperCase();
    if (taglineEl) taglineEl.textContent = `${cand.isRecommended ? 'AI RECOMMENDED' : 'OPERATOR ALTERNATIVE'} (Score: ${cand.score.toFixed(1)})`;
    
    if (delayEl) {
        delayEl.textContent = `${cand.delayDeltaPct > 0 ? '+' : ''}${cand.delayDeltaPct}%`;
        delayEl.className = `impact-val ${cand.delayDeltaPct < 0 ? 'green-text' : 'danger-text'}`;
    }
    if (queueEl) {
        queueEl.textContent = `${cand.queueDeltaPct > 0 ? '+' : ''}${cand.queueDeltaPct}%`;
        queueEl.className = `impact-val ${cand.queueDeltaPct < 0 ? 'green-text' : 'danger-text'}`;
    }
    if (spillEl) {
        spillEl.textContent = cand.spillback.split(' ')[0];
        spillEl.className = `impact-val ${cand.spillback.includes('LOW') ? 'green-text' : 'amber-text'}`;
    }
    if (safetyEl) {
        safetyEl.textContent = cand.emergencySafety.split(' ')[0];
        safetyEl.className = `impact-val ${cand.emergencySafety.includes('SAFE') ? 'green-text' : 'danger-text'}`;
    }

    if (expText) expText.textContent = cand.explanation;
    if (confBadge) {
        if (cand.isRecommended) {
            confBadge.textContent = "HIGH CONFIDENCE (89%)";
            confBadge.className = "rec-confidence-badge";
        } else {
            confBadge.textContent = `EXPLORING ALTERNATIVE (Rank #${cand.rank})`;
            confBadge.className = "rec-confidence-badge amber-text";
        }
    }
}

// ==============================================================================
// 3. HUMAN OPERATOR DECISION ACTIONS (Approve / Reject / Try Another)
// ==============================================================================

async function approveStrategy() {
    const activeCand = appState.candidates.find(c => c.id === appState.selectedCandidateId) || appState.candidates[0];
    appState.decisionState = DECISION_STATES.APPLIED;
    appState.appliedStrategy = activeCand.type;

    // Apply Post-Intervention Traffic Result
    appState.traffic.junctions.J2.queueMeters = Math.max(12, appState.traffic.junctions.J2.queueMeters * 0.55);
    appState.traffic.junctions.J2.speedKmh = 36.0;
    appState.traffic.junctions.J2.anomalyScore = 0.15;
    appState.traffic.junctions.J2.status = "normal";
    appState.traffic.junctions.J2.isGreen = true;
    appState.predictions.J2.congestionProbability = 0.22;
    appState.interventionWindow.minutesRemaining = 8;
    appState.domino.paths[0].probability = 0.18;

    const msgEl = document.getElementById("decisionStatusMsg");
    if (msgEl) {
        msgEl.innerHTML = `✅ <strong class="green-text">STRATEGY APPLIED:</strong> ${activeCand.name} active on corridor. Traffic normalizing.`;
    }

    // Add to Audit Trail
    const nowStr = new Date().toLocaleTimeString();
    appState.events.unshift({
        id: Date.now(),
        text: `Operator APPROVED & APPLIED ${activeCand.name}. J2 queue cleared to ${appState.traffic.junctions.J2.queueMeters.toFixed(1)}m.`,
        severity: "success",
        time: nowStr
    });

    updateUI();
}

function rejectStrategy() {
    appState.decisionState = DECISION_STATES.REJECTED;
    appState.appliedStrategy = null;

    const msgEl = document.getElementById("decisionStatusMsg");
    if (msgEl) {
        msgEl.innerHTML = `⚠️ <strong class="danger-text">RECOMMENDATION REJECTED:</strong> No action taken. Traffic monitoring continues.`;
    }

    const nowStr = new Date().toLocaleTimeString();
    appState.events.unshift({
        id: Date.now(),
        text: `Operator REJECTED intervention. Baseline traffic progression resumed.`,
        severity: "warning",
        time: nowStr
    });

    updateUI();
}

function tryAnotherCandidate() {
    // Cycle to next candidate
    const currentIndex = appState.candidates.findIndex(c => c.id === appState.selectedCandidateId);
    const nextIndex = (currentIndex + 1) % appState.candidates.length;
    appState.selectedCandidateId = appState.candidates[nextIndex].id;

    const msgEl = document.getElementById("decisionStatusMsg");
    if (msgEl) {
        msgEl.textContent = `Inspecting alternative #${appState.candidates[nextIndex].rank}: ${appState.candidates[nextIndex].name}`;
    }

    updateUI();
}

// ==============================================================================
// 4. CANVAS TOPOLOGY, FLOW ANIMATION & OVERLAYS
// ==============================================================================

function renderCanvas() {
    if (!ctx || !canvas) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;
    const centerY = h / 2;

    const jx = {
        J1: w * 0.20,
        J2: w * 0.50,
        J3: w * 0.80
    };

    // 1. Draw Main East-West Corridor Roadway
    ctx.fillStyle = "#122133";
    ctx.fillRect(40, centerY - 28, w - 80, 56);
    ctx.strokeStyle = "#1F3650";
    ctx.lineWidth = 2;
    ctx.strokeRect(40, centerY - 28, w - 80, 56);

    // Dashed center line
    ctx.strokeStyle = "#385270";
    ctx.lineWidth = 2;
    ctx.setLineDash([12, 10]);
    ctx.beginPath();
    ctx.moveTo(40, centerY);
    ctx.lineTo(w - 40, centerY);
    ctx.stroke();
    ctx.setLineDash([]);

    // 2. Draw North-South Feeder Roads
    Object.values(jx).forEach(x => {
        ctx.fillStyle = "#122133";
        ctx.fillRect(x - 20, 30, 40, h - 60);
        ctx.strokeStyle = "#1F3650";
        ctx.lineWidth = 2;
        ctx.strokeRect(x - 20, 30, 40, h - 60);
    });

    // 3. Draw Flow Vehicles
    if (appState.layers.traffic) {
        const t = Date.now() / 350.0;
        ctx.fillStyle = "#22C7D6";
        for (let i = 0; i < 10; i++) {
            const vx = (40 + (t * 35 + i * 75) % (w - 100));
            ctx.fillRect(vx, centerY - 5, 12, 6);
        }
    }

    // 4. Draw Domino Cascade Arrow Overlay
    if (appState.layers.spillover && appState.decisionState !== DECISION_STATES.APPLIED) {
        const timeOffset = (Date.now() / 40) % 30;
        ctx.strokeStyle = "rgba(239, 68, 68, 0.8)";
        ctx.lineWidth = 3;
        ctx.setLineDash([8, 8]);
        ctx.lineDashOffset = timeOffset;
        ctx.beginPath();
        ctx.moveTo(jx.J2 - 40, centerY - 14);
        ctx.lineTo(jx.J1 + 40, centerY - 14);
        ctx.stroke();

        ctx.fillStyle = "#EF4444";
        ctx.font = "bold 10px Inter, sans-serif";
        ctx.fillText("▲ 73% Spillover", (jx.J1 + jx.J2) / 2, centerY - 20);

        ctx.strokeStyle = "rgba(255, 176, 32, 0.7)";
        ctx.lineDashOffset = -timeOffset;
        ctx.beginPath();
        ctx.moveTo(jx.J2 + 40, centerY - 14);
        ctx.lineTo(jx.J3 - 40, centerY - 14);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.fillStyle = "#FFB020";
        ctx.fillText("▲ 41% Risk", (jx.J2 + jx.J3) / 2, centerY - 20);
    }

    // 5. Draw Junction Nodes, Signals, and Anomaly Pulses
    function drawNode(name, x, y) {
        const isSelected = (appState.selectedJunction === name);
        const jData = appState.traffic.junctions[name];

        if (appState.layers.anomaly && jData.anomalyScore >= 0.8 && appState.decisionState !== DECISION_STATES.APPLIED) {
            const pulse = (Math.sin(Date.now() / 250) + 1) * 3;
            ctx.strokeStyle = `rgba(239, 68, 68, ${0.4 + pulse / 10})`;
            ctx.lineWidth = 3 + pulse;
            ctx.strokeRect(x - 42 - pulse, y - 42 - pulse, 84 + pulse * 2, 84 + pulse * 2);
        }

        if (isSelected) {
            ctx.strokeStyle = "rgba(34, 199, 214, 0.9)";
            ctx.lineWidth = 2.5;
            ctx.setLineDash([6, 6]);
            ctx.strokeRect(x - 38, y - 38, 76, 76);
            ctx.setLineDash([]);
        }

        ctx.fillStyle = "#0A1726";
        ctx.strokeStyle = isSelected ? "var(--cyan)" : "#223B59";
        ctx.lineWidth = 2;
        ctx.fillRect(x - 14, y - 26, 28, 52);
        ctx.strokeRect(x - 14, y - 26, 28, 52);

        const isGreen = jData.isGreen;
        ctx.fillStyle = isGreen ? "#39E75F" : "#1A2E44";
        ctx.beginPath();
        ctx.arc(x, y - 12, 7, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = !isGreen ? "#EF4444" : "#1A2E44";
        ctx.beginPath();
        ctx.arc(x, y + 12, 7, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = isSelected ? "#22C7D6" : "#F4F8FC";
        ctx.font = "bold 12px Inter, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(name, x, y - 44);

        const barWidth = Math.min(70, jData.queueMeters * 1.0);
        ctx.fillStyle = "rgba(255, 176, 32, 0.2)";
        ctx.fillRect(x - 35, y + 36, 70, 7);
        ctx.fillStyle = (jData.status === "critical") ? "#EF4444" : "#FFB020";
        ctx.fillRect(x - 35, y + 36, barWidth, 7);
    }

    drawNode("J1", jx.J1, centerY);
    drawNode("J2", jx.J2, centerY);
    drawNode("J3", jx.J3, centerY);

    requestAnimationFrame(renderCanvas);
}

// ==============================================================================
// 5. EVENT LISTENERS & BOOTSTRAP
// ==============================================================================

function selectJunction(jId) {
    if (!appState.traffic.junctions[jId]) return;
    appState.selectedJunction = jId;
    updateUI();
}

// Bind Card Clicks
["J1", "J2", "J3"].forEach(jId => {
    const card = document.getElementById(`card${jId}`);
    if (card) card.addEventListener("click", () => selectJunction(jId));
});

// Bind Canvas Clicks
if (canvas) {
    canvas.addEventListener("click", e => {
        const rect = canvas.getBoundingClientRect();
        const clickX = ((e.clientX - rect.left) / rect.width) * canvas.width;
        if (clickX < canvas.width * 0.35) selectJunction("J1");
        else if (clickX < canvas.width * 0.65) selectJunction("J2");
        else selectJunction("J3");
    });
}

// Layer Toggle Buttons
["traffic", "prediction", "anomaly", "spillover"].forEach(layerKey => {
    const btn = document.getElementById(`toggle${layerKey.charAt(0).toUpperCase() + layerKey.slice(1)}Layer`);
    if (btn) {
        btn.addEventListener("click", () => {
            appState.layers[layerKey] = !appState.layers[layerKey];
            if (appState.layers[layerKey]) btn.classList.add("active");
            else btn.classList.remove("active");
        });
    }
});

// Bind Human Decision Buttons
document.getElementById("btnApproveStrategy")?.addEventListener("click", approveStrategy);
document.getElementById("btnRejectStrategy")?.addEventListener("click", rejectStrategy);
document.getElementById("btnTryAnother")?.addEventListener("click", tryAnotherCandidate);
document.getElementById("btnReevaluate")?.addEventListener("click", () => {
    tryAnotherCandidate();
});

// Demo Toggle Button
const btnDemo = document.getElementById("btnToggleDemo");
if (btnDemo) {
    btnDemo.addEventListener("click", () => {
        appState.isDemoScenario = !appState.isDemoScenario;
        btnDemo.textContent = appState.isDemoScenario ? "SCENARIO: INCIDENT WAVE" : "RUN DEMO SCENARIO";
        
        if (appState.isDemoScenario) {
            appState.traffic.junctions.J2.queueMeters = 74.0;
            appState.traffic.junctions.J2.speedKmh = 11.0;
            appState.traffic.junctions.J2.anomalyScore = 0.96;
            appState.predictions.J2.congestionProbability = 0.94;
            appState.interventionWindow.minutesRemaining = 4;
            appState.domino.paths[0].probability = 0.88;
        } else {
            appState.traffic.junctions.J2.queueMeters = 61.0;
            appState.traffic.junctions.J2.speedKmh = 18.0;
            appState.traffic.junctions.J2.anomalyScore = 0.91;
            appState.predictions.J2.congestionProbability = 0.87;
            appState.interventionWindow.minutesRemaining = 6;
            appState.domino.paths[0].probability = 0.73;
        }
        updateUI();
    });
}

function init() {
    fetchHealthCheck();
    fetchTrafficIntelligence();
    updateUI();
    renderCanvas();

    setInterval(fetchHealthCheck, 5000);
    setInterval(fetchTrafficIntelligence, 3000);
    setInterval(updateUI, 1000);
}

document.addEventListener("DOMContentLoaded", init);
