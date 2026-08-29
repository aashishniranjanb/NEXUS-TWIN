/**
 * NEXUS-TWIN P0 Command Center Web Platform Application
 * Strict Separation: Clean API Adapter, Response Normalization, Fallback Mock State, and Dynamic Canvas Visualization
 */

// API Base Configuration
const API_BASE = "http://localhost:8000/api";

// Central Application State
const appState = {
    selectedJunction: "J2",
    connectionStatus: "CHECKING", // "ONLINE" | "DEMO_MODE" | "RECONNECTING"
    lastUpdated: new Date(),
    isDemoScenario: false,
    
    // Normalized Traffic State
    traffic: {
        networkSpeedKmh: 38.4,
        totalVehicles: 128,
        totalQueueMeters: 26.5,
        avgWaitingTimeSeconds: 0.28,
        junctions: {
            J1: { id: "J1", name: "J1 (Westbound Inflow)", status: "normal", queueMeters: 18.0, speedKmh: 42.0, isGreen: true, vehicleCount: 42 },
            J2: { id: "J2", name: "J2 (Central Hub)", status: "critical", queueMeters: 61.0, speedKmh: 18.0, isGreen: false, vehicleCount: 58 },
            J3: { id: "J3", name: "J3 (Eastbound Exit)", status: "warning", queueMeters: 34.0, speedKmh: 29.0, isGreen: true, vehicleCount: 28 }
        }
    },
    
    // Normalized AI Predictions per Junction
    predictions: {
        J1: { junctionId: "J1", congestionProbability: 0.24, forecastMinutes: 5, confidence: 0.88, riskLevel: "low", predictedQueueGrowth: "+2.0 m", fingerprint: "NORMAL FLOW (95%)", spillover: "None" },
        J2: { junctionId: "J2", congestionProbability: 0.87, forecastMinutes: 5, confidence: 0.82, riskLevel: "critical", predictedQueueGrowth: "+34.0 m", fingerprint: "INCIDENT-LIKE (91%)", spillover: "J1 (73% in 4 min)" },
        J3: { junctionId: "J3", congestionProbability: 0.52, forecastMinutes: 5, confidence: 0.79, riskLevel: "warning", predictedQueueGrowth: "+11.0 m", fingerprint: "RECURRING CONGESTION (84%)", spillover: "None" }
    }
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

async function fetchTrafficState() {
    try {
        // Polling existing backend evaluation / state endpoints
        const res = await fetch(`${API_BASE}/evaluate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ junction_id: appState.selectedJunction, horizon_seconds: 300, strategy_type: "diversion" }),
            signal: AbortSignal.timeout(2500)
        });

        if (res.ok) {
            const data = await res.json();
            normalizeBackendData(data);
            setConnectionStatus("ONLINE");
            return;
        }
    } catch (err) {
        setConnectionStatus("DEMO_MODE");
    }
}

function normalizeBackendData(backendData) {
    if (!backendData) return;
    
    // Normalize live situation telemetry if available
    if (backendData.situation) {
        const s = backendData.situation;
        appState.traffic.avgWaitingTimeSeconds = s.avg_waiting_time_s || appState.traffic.avgWaitingTimeSeconds;
        appState.traffic.totalQueueMeters = s.queue_length_m || appState.traffic.totalQueueMeters;
        appState.traffic.networkSpeedKmh = s.avg_speed_kmh || appState.traffic.networkSpeedKmh;
        appState.traffic.totalVehicles = s.active_vehicles || appState.traffic.totalVehicles;
        
        // Update selected junction telemetry
        const curJ = appState.traffic.junctions[appState.selectedJunction];
        if (curJ) {
            curJ.queueMeters = s.queue_length_m || curJ.queueMeters;
            curJ.speedKmh = s.avg_speed_kmh || curJ.speedKmh;
        }
    }

    // Normalize AI prediction if available
    if (backendData.prediction) {
        const p = backendData.prediction;
        const curPred = appState.predictions[appState.selectedJunction];
        if (curPred) {
            curPred.congestionProbability = p.congestion_probability || curPred.congestionProbability;
            curPred.predictedQueueGrowth = p.predicted_queue_5min_m ? `+${p.predicted_queue_5min_m.toFixed(1)} m` : curPred.predictedQueueGrowth;
            curPred.riskLevel = p.will_congest_5min ? "critical" : "low";
        }
    }

    if (backendData.fingerprint) {
        const fp = backendData.fingerprint;
        const curPred = appState.predictions[appState.selectedJunction];
        if (curPred && fp.pattern_type) {
            curPred.fingerprint = `${fp.pattern_type} (${Math.round((fp.dataset_similarity_score || 0.91) * 100)}%)`;
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
    const sysApi = document.getElementById("sysApi");

    if (status === "ONLINE") {
        if (dot) dot.className = "status-dot green";
        if (txt) txt.textContent = "SYSTEM ONLINE";
        if (liveTag) { liveTag.textContent = "LIVE TELEMETRY"; liveTag.className = "mode-tag"; }
        if (sysApi) { sysApi.textContent = "ONLINE (8000)"; sysApi.className = "sys-status green-text"; }
    } else {
        if (dot) dot.className = "status-dot amber";
        if (txt) txt.textContent = "DEMO MODE (OFFLINE)";
        if (liveTag) { liveTag.textContent = "DEMO SIMULATION"; liveTag.className = "mode-tag amber-text"; }
        if (sysApi) { sysApi.textContent = "DEMO FALLBACK"; sysApi.className = "sys-status amber-text"; }
    }
}

// ==============================================================================
// 2. UI RENDERING & COMPONENT BINDINGS
// ==============================================================================

function updateUI() {
    // 1. Global Metrics
    const spdEl = document.getElementById("globalSpeed");
    const vehEl = document.getElementById("globalVehicles");
    const qEl = document.getElementById("globalQueue");
    const dlyEl = document.getElementById("globalDelay");
    if (spdEl) spdEl.textContent = `${appState.traffic.networkSpeedKmh.toFixed(1)} km/h`;
    if (vehEl) vehEl.textContent = `${appState.traffic.totalVehicles}`;
    if (qEl) qEl.textContent = `${appState.traffic.totalQueueMeters.toFixed(1)} m`;
    if (dlyEl) dlyEl.textContent = `${appState.traffic.avgWaitingTimeSeconds.toFixed(2)} s`;

    // 2. Junction Cards
    ["J1", "J2", "J3"].forEach(jId => {
        const jData = appState.traffic.junctions[jId];
        const card = document.getElementById(`card${jId}`);
        const qVal = document.getElementById(`queue${jId}`);
        const spdVal = document.getElementById(`speed${jId}`);
        const sigVal = document.getElementById(`signal${jId}`);
        const statPill = document.getElementById(`status${jId}`);

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
    });

    // 3. AI Prediction Panel for Selected Node
    const curPred = appState.predictions[appState.selectedJunction] || appState.predictions.J2;
    const targetLabel = document.getElementById("predTargetNode");
    const probEl = document.getElementById("predProbability");
    const riskBadge = document.getElementById("predRiskBadge");
    const confEl = document.getElementById("predConfidence");
    const qDeltaEl = document.getElementById("predQueueDelta");
    const fpEl = document.getElementById("predFingerprint");
    const spillEl = document.getElementById("predSpillover");

    if (targetLabel) targetLabel.textContent = `Target: Junction ${appState.selectedJunction}`;
    if (probEl) probEl.textContent = `${Math.round(curPred.congestionProbability * 100)}%`;
    if (confEl) confEl.textContent = `${Math.round(curPred.confidence * 100)}%`;
    if (qDeltaEl) qDeltaEl.textContent = curPred.predictedQueueGrowth;
    if (fpEl) fpEl.textContent = curPred.fingerprint;
    if (spillEl) spillEl.textContent = curPred.spillover;

    if (riskBadge) {
        if (curPred.riskLevel === "critical") {
            riskBadge.textContent = "CRITICAL RISK";
            riskBadge.className = "pred-risk-badge bg-danger";
        } else if (curPred.riskLevel === "warning") {
            riskBadge.textContent = "ELEVATED RISK";
            riskBadge.className = "pred-risk-badge";
            riskBadge.style.background = "rgba(255, 176, 32, 0.2)";
            riskBadge.style.border = "1px solid var(--amber)";
            riskBadge.style.color = "var(--amber)";
        } else {
            riskBadge.textContent = "STABLE RISK";
            riskBadge.className = "pred-risk-badge";
            riskBadge.style.background = "rgba(57, 231, 95, 0.15)";
            riskBadge.style.border = "1px solid var(--green)";
            riskBadge.style.color = "var(--green)";
        }
    }

    // 4. Last Updated Timestamp
    const lastUp = document.getElementById("lastUpdatedText");
    if (lastUp) {
        const secAgo = Math.max(0, Math.floor((Date.now() - appState.lastUpdated.getTime()) / 1000));
        lastUp.textContent = `Updated: ${secAgo}s ago`;
    }
}

// ==============================================================================
// 3. CANVAS TOPOLOGY & FLOW ANIMATION
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
    
    // Road border lines
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

    // 2. Draw North-South Feeder Roads for each Junction
    Object.values(jx).forEach(x => {
        ctx.fillStyle = "#122133";
        ctx.fillRect(x - 20, 30, 40, h - 60);
        ctx.strokeStyle = "#1F3650";
        ctx.lineWidth = 2;
        ctx.strokeRect(x - 20, 30, 40, h - 60);
    });

    // 3. Draw Flow Vehicles
    const t = Date.now() / 350.0;
    ctx.fillStyle = "#22C7D6";
    for (let i = 0; i < 10; i++) {
        const vx = (40 + (t * 35 + i * 75) % (w - 100));
        ctx.fillRect(vx, centerY - 5, 12, 6);
    }

    // 4. Draw Junction Nodes & Signals
    function drawNode(name, x, y) {
        const isSelected = (appState.selectedJunction === name);
        const jData = appState.traffic.junctions[name];

        // Selection Aura
        if (isSelected) {
            ctx.strokeStyle = "rgba(34, 199, 214, 0.8)";
            ctx.lineWidth = 3;
            ctx.setLineDash([6, 6]);
            ctx.strokeRect(x - 38, y - 38, 76, 76);
            ctx.setLineDash([]);
        }

        // Signal Box
        ctx.fillStyle = "#0A1726";
        ctx.strokeStyle = isSelected ? "var(--cyan)" : "#223B59";
        ctx.lineWidth = 2;
        ctx.fillRect(x - 14, y - 26, 28, 52);
        ctx.strokeRect(x - 14, y - 26, 28, 52);

        // Signal Bulbs
        const isGreen = jData.isGreen;
        ctx.fillStyle = isGreen ? "#39E75F" : "#1A2E44";
        ctx.beginPath();
        ctx.arc(x, y - 12, 7, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = !isGreen ? "#EF4444" : "#1A2E44";
        ctx.beginPath();
        ctx.arc(x, y + 12, 7, 0, Math.PI * 2);
        ctx.fill();

        // Node Title
        ctx.fillStyle = isSelected ? "#22C7D6" : "#F4F8FC";
        ctx.font = "bold 12px Inter, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(name, x, y - 44);

        // Queue Indicator Bar
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
// 4. INTERACTION & EVENT LISTENERS
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

// Bind Canvas Clicks to select nodes directly
if (canvas) {
    canvas.addEventListener("click", e => {
        const rect = canvas.getBoundingClientRect();
        const clickX = ((e.clientX - rect.left) / rect.width) * canvas.width;
        if (clickX < canvas.width * 0.35) selectJunction("J1");
        else if (clickX < canvas.width * 0.65) selectJunction("J2");
        else selectJunction("J3");
    });
}

// Demo Toggle Button
const btnDemo = document.getElementById("btnToggleDemo");
if (btnDemo) {
    btnDemo.addEventListener("click", () => {
        appState.isDemoScenario = !appState.isDemoScenario;
        btnDemo.textContent = appState.isDemoScenario ? "SCENARIO: INCIDENT WAVE" : "RUN DEMO SCENARIO";
        
        if (appState.isDemoScenario) {
            appState.traffic.junctions.J2.queueMeters = 72.0;
            appState.traffic.junctions.J2.speedKmh = 12.0;
            appState.predictions.J2.congestionProbability = 0.94;
            appState.predictions.J2.predictedQueueGrowth = "+48.0 m";
        } else {
            appState.traffic.junctions.J2.queueMeters = 61.0;
            appState.traffic.junctions.J2.speedKmh = 18.0;
            appState.predictions.J2.congestionProbability = 0.87;
            appState.predictions.J2.predictedQueueGrowth = "+34.0 m";
        }
        updateUI();
    });
}

// ==============================================================================
// 5. BOOTSTRAP & POLLING LOOPS
// ==============================================================================

function init() {
    fetchHealthCheck();
    fetchTrafficState();
    updateUI();
    renderCanvas();

    // Polling Intervals
    setInterval(fetchHealthCheck, 5000);
    setInterval(fetchTrafficState, 3000);
    setInterval(updateUI, 1000);
}

document.addEventListener("DOMContentLoaded", init);
