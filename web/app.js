const API_BASE = "http://localhost:8000/api";

const STATES = { MENU: 'menu', PLAYING: 'playing', EVENT_ACTIVE: 'event_active', AWAITING_RESULT: 'awaiting_result', RESULT_SHOWN: 'result_shown', GAME_OVER: 'game_over' };
let currentState = STATES.MENU;

let gameState = {
    session_id: null,
    player_name: '',
    mode: 'free_play',
    difficulty: 'easy',
    total_points: 0,
    current_streak: 0,
    max_streak: 0,
    badges_unlocked: [],
    active_event: null,
    session_active: false,
    session_start_time: 0,
    time_elapsed: 0
};

let liveData = null;
let pollStateInterval = null;
let pollEventInterval = null;
let timerInterval = null;

// DOM Elements
const views = {
    menu: document.getElementById('gameMenu'),
    dashboard: document.getElementById('gameDashboard'),
    alert: document.getElementById('eventAlert'),
    popup: document.getElementById('scorePopup'),
    leaderboard: document.getElementById('leaderboardSidebar')
};

const canvas = document.getElementById("networkCanvas");
const ctx = canvas.getContext("2d");

// Event Listeners for Menu
document.querySelectorAll('.mode-card').forEach(card => {
    card.addEventListener('click', () => {
        document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        gameState.mode = card.dataset.mode;
        
        const sel = document.getElementById('challengeSelector');
        if (gameState.mode === 'challenge') sel.classList.remove('hidden');
        else sel.classList.add('hidden');
    });
});

document.querySelectorAll('.btn-diff').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-diff').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        gameState.difficulty = btn.dataset.diff;
    });
});

document.getElementById('btnStartGame').addEventListener('click', async () => {
    gameState.player_name = 'Operator';
    
    let payload = {
        player_name: gameState.player_name,
        mode: 'free_play',
        difficulty: 'normal'
    };
    
    try {
        const res = await fetch(`${API_BASE}/game/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            const data = await res.json();
            gameState.session_id = data.session_id;
        } else {
            throw new Error('API Error');
        }
    } catch (err) {
        console.warn("Server offline, using local mock session.");
        gameState.session_id = 'sess_' + Math.random().toString(36).substr(2, 9);
    }
    
    gameState.session_active = true;
    gameState.session_start_time = Date.now();
    gameState.total_points = 0;
    gameState.current_streak = 0;
    gameState.badges_unlocked = [];
    
    // UI Update
    views.menu.classList.add('hidden');
    views.dashboard.classList.remove('hidden');
    document.getElementById('hudPlayerName').textContent = "TRAFFIC OPERATIONS CONTROL";
    document.getElementById('hudModeBadge').textContent = "AI CRISIS MODEL ACTIVE";
    
    currentState = STATES.PLAYING;
    startLoops();
});

document.getElementById('btnEndGame').addEventListener('click', async () => {
    if(confirm("Are you sure you want to end the game?")) {
        try {
            await fetch(`${API_BASE}/game/end`, { method: 'POST' });
        } catch(e) {}
        
        stopLoops();
        fetchLeaderboard();
        views.leaderboard.classList.add('open');
        views.menu.classList.remove('hidden');
        views.dashboard.classList.add('hidden');
        currentState = STATES.MENU;
    }
});

document.getElementById('btnToggleLeaderboard').addEventListener('click', () => {
    views.leaderboard.classList.toggle('open');
    if (views.leaderboard.classList.contains('open')) fetchLeaderboard();
});

// Action Console Logic
let currentStrategy = null;
document.querySelectorAll('.strategy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        if(currentState === STATES.AWAITING_RESULT) return;
        
        document.querySelectorAll('.strategy-btn').forEach(b => b.classList.remove('selected'));
        document.querySelectorAll('.strategy-options').forEach(o => o.classList.add('hidden'));
        
        btn.classList.add('selected');
        currentStrategy = btn.dataset.strategy;
        
        const opt = document.getElementById(`opt_${currentStrategy}`);
        if(opt) opt.classList.remove('hidden');
        
        document.getElementById('btnCommitMove').disabled = false;
    });
});

// Sliders updates
document.getElementById('param_green_extend').addEventListener('input', e => document.getElementById('val_green_extend').textContent = `${e.target.value}s`);
document.getElementById('param_diversion').addEventListener('input', e => document.getElementById('val_diversion').textContent = `${e.target.value}%`);

// Commit Move
document.getElementById('btnCommitMove').addEventListener('click', async () => {
    if(!currentStrategy || currentState === STATES.AWAITING_RESULT) return;
    
    currentState = STATES.AWAITING_RESULT;
    document.getElementById('btnCommitMove').disabled = true;
    document.getElementById('btnCommitMove').textContent = "SIMULATING...";
    
    let payload = {
        strategy_type: currentStrategy,
        junction_id: document.getElementById('actionTargetJunction').value
    };
    if (currentStrategy === 'green_extend') payload.extension_seconds = parseInt(document.getElementById('param_green_extend').value);
    if (currentStrategy === 'diversion') payload.extension_seconds = parseInt(document.getElementById('param_diversion').value); // Reusing field
    
    let result = null;
    try {
        const res = await fetch(`${API_BASE}/game/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if(res.ok) result = await res.json();
        else throw new Error("API Move Error");
    } catch(err) {
        // Fallback mock
        let base = currentStrategy === 'do_nothing' ? -100 : Math.floor(Math.random() * 300) + 100;
        let ai = base - (Math.floor(Math.random() * 100) - 20);
        let beat = base > ai;
        result = {
            points_base: base,
            points_total: beat ? base * 1.5 : base,
            multipliers_applied: beat ? ["Beat AI x1.5"] : [],
            penalties_applied: currentStrategy === 'do_nothing' ? ["-50 Inaction"] : [],
            player_score: base,
            ai_score: ai,
            beat_ai: beat,
            streak_count: beat ? gameState.current_streak + 1 : 0,
            new_badges: beat && gameState.current_streak === 2 ? [{name: "Streak Master", icon: "🔥", tier: "gold"}] : []
        };
    }
    
    showScorePopup(result);
});

function showScorePopup(res) {
    currentState = STATES.RESULT_SHOWN;
    
    // Update local state
    gameState.total_points += res.points_total;
    gameState.current_streak = res.streak_count;
    if(res.new_badges) gameState.badges_unlocked.push(...res.new_badges);
    
    const isPos = res.points_total >= 0;
    
    document.getElementById('popupResultTitle').textContent = res.beat_ai ? "BEAT THE AI!" : "AI WAS BETTER";
    const pts = document.getElementById('popupPoints');
    pts.textContent = (isPos ? "+" : "") + res.points_total;
    pts.className = "popup-points " + (isPos ? "positive" : "negative");
    
    document.getElementById('popupBasePoints').textContent = `Base Points: ${res.points_base}`;
    
    const mults = document.getElementById('popupMultipliers');
    mults.innerHTML = '';
    res.multipliers_applied?.forEach(m => {
        let li = document.createElement('li'); li.textContent = m; mults.appendChild(li);
    });
    
    const pens = document.getElementById('popupPenalties');
    pens.innerHTML = '';
    res.penalties_applied?.forEach(p => {
        let li = document.createElement('li'); li.textContent = p; pens.appendChild(li);
    });
    
    document.getElementById('popupComparison').textContent = `Your Score: ${res.player_score.toFixed(2)} vs AI Score: ${res.ai_score.toFixed(2)}`;
    
    const bcontainer = document.getElementById('popupNewBadges');
    bcontainer.innerHTML = '';
    res.new_badges?.forEach(b => {
        let div = document.createElement('div');
        div.className = `badge-circle tier-${b.tier} unlocked`;
        div.textContent = b.icon;
        div.title = b.name;
        bcontainer.appendChild(div);
    });
    
    views.popup.classList.remove('hidden');
    
    // Dismiss and reset
    setTimeout(() => {
        views.popup.classList.add('hidden');
        document.getElementById('btnCommitMove').disabled = false;
        document.getElementById('btnCommitMove').textContent = "COMMIT MOVE";
        
        // Hide event if active
        gameState.active_event = null;
        views.alert.classList.add('hidden');
        
        updateHUD();
        currentState = STATES.PLAYING;
    }, 4000);
}

// Game Loops
function startLoops() {
    timerInterval = setInterval(() => {
        gameState.time_elapsed++;
        let m = Math.floor(gameState.time_elapsed / 60).toString().padStart(2, '0');
        let s = (gameState.time_elapsed % 60).toString().padStart(2, '0');
        document.getElementById('hudTimer').textContent = `${m}:${s}`;
        
        if (gameState.active_event) {
            let remain = gameState.active_event.remaining_s || 0;
            remain--;
            gameState.active_event.remaining_s = remain;
            let pct = Math.max(0, (remain / gameState.active_event.time_limit_s) * 100);
            document.getElementById('eventTimerBar').style.width = pct + "%";
            if (remain <= 0) {
                // Event expired
                gameState.active_event = null;
                views.alert.classList.add('hidden');
                currentState = STATES.PLAYING;
            }
        }
    }, 1000);
    
    pollStateInterval = setInterval(fetchGameState, 3000);
    pollEventInterval = setInterval(fetchEvent, 2000);
    setInterval(fetchStateData, 1000);
    requestAnimationFrame(renderCanvas);
}

function stopLoops() {
    clearInterval(timerInterval);
    clearInterval(pollStateInterval);
    clearInterval(pollEventInterval);
    gameState.session_active = false;
}

async function fetchGameState() {
    if(!gameState.session_active) return;
    try {
        const res = await fetch(`${API_BASE}/game/state`);
        if(res.ok) {
            const st = await res.json();
            gameState.total_points = st.total_points;
            gameState.current_streak = st.current_streak;
            gameState.badges_unlocked = st.badges_unlocked || [];
            updateHUD();
        }
    } catch(e) {
        updateHUD(); // fallback uses local state
    }
}

function updateHUD() {
    document.getElementById('hudScore').textContent = gameState.total_points;
    if (gameState.current_streak > 1) {
        views.dashboard.querySelector('#hudStreak').classList.remove('hidden');
        document.getElementById('hudStreakText').textContent = `x${gameState.current_streak}`;
    } else {
        views.dashboard.querySelector('#hudStreak').classList.add('hidden');
    }
    
    document.getElementById('canvasScoreOverlay').textContent = gameState.total_points;
    
    // Render badges
    const bgrid = document.getElementById('badgeGrid');
    bgrid.innerHTML = '';
    const allBadges = [
        {id:'first_blood', icon:'🩸'}, {id:'streak_3', icon:'🔥'}, {id:'streak_5', icon:'☄️'},
        {id:'ai_crusher', icon:'🤖'}, {id:'zero_delay', icon:'⏱️'}, {id:'hero', icon:'🦸'}
    ];
    
    allBadges.forEach(tb => {
        let unlocked = gameState.badges_unlocked.find(b => b.badge_id === tb.id || b.name === tb.name);
        let div = document.createElement('div');
        div.className = `badge-circle ${unlocked ? `tier-${unlocked.tier || 'bronze'} unlocked` : ''}`;
        div.textContent = unlocked ? (unlocked.icon || tb.icon) : '🔒';
        bgrid.appendChild(div);
    });
}

// Interactive Scenario Controller Timeline States
const TIMELINE_STEPS = [
    { id: 'normal', name: 'NORMAL', desc: 'Normal traffic operations baseline' },
    { id: 'anomaly', name: 'ANOMALY', desc: 'J2 queue accumulates rapidly' },
    { id: 'fingerprint', name: 'FINGERPRINT', desc: 'Incident pattern fingerprint matched' },
    { id: 'prediction', name: 'PREDICTION', desc: 'XGBoost forecasts 5-min congestion probability' },
    { id: 'domino', name: 'DOMINO EFFECT', desc: 'Congestion domino spreading toward J1/J3' },
    { id: 'recommendation', name: 'RECOMMENDATION', desc: 'AI Copilot suggests Bypass Diversion' },
    { id: 'simulation', name: 'SIMULATION', desc: 'Digital Twin evaluates what-if candidates' },
    { id: 'decision', name: 'HUMAN DECISION', desc: 'Awaiting operator approval/override' },
    { id: 'outcome', name: 'OUTCOME', desc: 'Evaluation report: before vs after' }
];

let currentTimelineIndex = 0;
let demoTimer = null;

// Populate Timeline Steps visual nodes in HTML
function renderTimeline() {
    const container = document.getElementById('timelineSteps');
    if (!container) return;
    container.innerHTML = '';
    TIMELINE_STEPS.forEach((step, idx) => {
        const stepDiv = document.createElement('div');
        stepDiv.style.flex = '1';
        stepDiv.style.padding = '8px';
        stepDiv.style.textAlign = 'center';
        stepDiv.style.borderRadius = '4px';
        stepDiv.style.fontSize = '10px';
        stepDiv.style.fontWeight = 'bold';
        
        let bgColor = 'rgba(255, 255, 255, 0.03)';
        let border = '1px solid var(--border-color)';
        let textColor = 'var(--text-dim)';
        
        if (idx === currentTimelineIndex) {
            bgColor = 'rgba(33, 199, 232, 0.2)';
            border = '1px solid var(--cyan)';
            textColor = 'var(--cyan)';
        } else if (idx < currentTimelineIndex) {
            bgColor = 'rgba(16, 185, 129, 0.1)';
            border = '1px solid var(--emerald)';
            textColor = 'var(--emerald)';
        }
        
        stepDiv.style.backgroundColor = bgColor;
        stepDiv.style.border = border;
        stepDiv.style.color = textColor;
        stepDiv.innerHTML = `<div>${step.id.toUpperCase()}</div><div style="font-size: 8px; font-weight: normal; margin-top: 2px;">${step.name}</div>`;
        container.appendChild(stepDiv);
    });

    // Update Scenario Desc
    const currentStep = TIMELINE_STEPS[currentTimelineIndex];
    document.getElementById('currentStepDesc').textContent = currentStep.desc;
}

// Interactive Controller: Apply step parameters on telemetry indicators
function applyTimelineStep(idx) {
    currentTimelineIndex = idx;
    renderTimeline();

    // Default telemetry structure to simulate pipeline values
    let telemetry = {
        avg_waiting_time_s: 0.24,
        queue_length_m: 20.0,
        avg_speed_kmh: 39.6,
        active_vehicles: 124,
        probability: 0.12,
        will_congest: false,
        predicted_q: 20.0,
        fingerprint: "NORMAL",
        similarity: 0.76,
        rec_strategy: "do_nothing",
        confidence: 0.85
    };

    switch (TIMELINE_STEPS[idx].id) {
        case 'normal':
            break;
        case 'anomaly':
            telemetry.queue_length_m = 32.5;
            telemetry.avg_speed_kmh = 28.4;
            telemetry.avg_waiting_time_s = 0.38;
            telemetry.fingerprint = "RECURRING CONGESTION";
            break;
        case 'fingerprint':
            telemetry.queue_length_m = 44.2;
            telemetry.avg_speed_kmh = 21.0;
            telemetry.avg_waiting_time_s = 0.52;
            telemetry.fingerprint = "INCIDENT-LIKE";
            telemetry.similarity = 0.91;
            break;
        case 'prediction':
            telemetry.queue_length_m = 44.2;
            telemetry.avg_speed_kmh = 21.0;
            telemetry.avg_waiting_time_s = 0.52;
            telemetry.fingerprint = "INCIDENT-LIKE";
            telemetry.similarity = 0.91;
            telemetry.probability = 0.87;
            telemetry.will_congest = true;
            telemetry.predicted_q = 64.0;
            break;
        case 'domino':
        case 'recommendation':
            telemetry.queue_length_m = 44.2;
            telemetry.avg_speed_kmh = 21.0;
            telemetry.avg_waiting_time_s = 0.52;
            telemetry.fingerprint = "INCIDENT-LIKE";
            telemetry.similarity = 0.91;
            telemetry.probability = 0.87;
            telemetry.will_congest = true;
            telemetry.predicted_q = 64.0;
            telemetry.rec_strategy = "diversion";
            telemetry.confidence = 0.91;
            break;
        case 'simulation':
        case 'decision':
            telemetry.queue_length_m = 44.2;
            telemetry.avg_speed_kmh = 21.0;
            telemetry.avg_waiting_time_s = 0.52;
            telemetry.fingerprint = "INCIDENT-LIKE";
            telemetry.similarity = 0.91;
            telemetry.probability = 0.87;
            telemetry.will_congest = true;
            telemetry.predicted_q = 64.0;
            telemetry.rec_strategy = "diversion";
            telemetry.confidence = 0.91;
            break;
        case 'outcome':
            telemetry.queue_length_m = 12.0;
            telemetry.avg_speed_kmh = 42.5;
            telemetry.avg_waiting_time_s = 0.08;
            telemetry.fingerprint = "NORMAL";
            telemetry.rec_strategy = "diversion";
            break;
    }

    // Update frontend metrics elements
    document.getElementById("metricDelay").textContent = telemetry.avg_waiting_time_s.toFixed(2) + "s";
    document.getElementById("metricQueue").textContent = telemetry.queue_length_m.toFixed(1) + "m";
    document.getElementById("metricSpeed").textContent = telemetry.avg_speed_kmh.toFixed(1) + "km/h";
    document.getElementById("metricVehicles").textContent = telemetry.active_vehicles;

    // Update Forecast Panel
    document.getElementById('forecastProb').textContent = Math.round(telemetry.probability * 100) + "%";
    document.getElementById('forecastQueue').textContent = telemetry.predicted_q.toFixed(1) + "m";
    const trendEl = document.getElementById('forecastTrend');
    if (telemetry.will_congest) {
        trendEl.textContent = "▲ CRITICAL";
        trendEl.style.color = "var(--rose)";
        document.getElementById('eventAlert').classList.remove('hidden');
    } else {
        trendEl.textContent = "▼ STABLE";
        trendEl.style.color = "var(--emerald)";
        document.getElementById('eventAlert').classList.add('hidden');
    }

    // Update Similarity Index
    document.getElementById('trafficFingerprintBadge').textContent = `Fingerprint: ${telemetry.fingerprint}`;
    document.getElementById('fingerprintSimilarity').textContent = `Pattern match: ${Math.round(telemetry.similarity * 100)}%`;
    
    const fpFactors = document.getElementById('fingerprintFactors');
    fpFactors.innerHTML = '';
    const mockFactors = {
        "Directional Inflow": telemetry.queue_length_m > 30 ? 0.82 : 0.35,
        "Waiting Time Dev": telemetry.queue_length_m > 30 ? 0.91 : 0.12,
        "Speed Collapse": telemetry.queue_length_m > 30 ? 0.78 : 0.08,
        "Queue Rate Delta": telemetry.queue_length_m > 30 ? 0.85 : 0.15
    };
    Object.entries(mockFactors).forEach(([k, v]) => {
        const row = document.createElement('div');
        row.style.display = 'flex';
        row.style.justifyContent = 'space-between';
        row.style.fontSize = '12px';
        row.innerHTML = `<span style="color: var(--text-muted);">${k}</span><span style="font-weight: bold; color: var(--text-main);">${Math.round(v * 100)}%</span>`;
        fpFactors.appendChild(row);
    });

    // Update AI Copilot Advice
    document.getElementById('copilotRecommends').textContent = `RECOMMENDED: ${telemetry.rec_strategy.toUpperCase()}`;
    document.getElementById('copilotConfidence').textContent = `Confidence: ${Math.round(telemetry.confidence * 100)}%`;
    
    if (telemetry.rec_strategy === 'do_nothing') {
        document.getElementById('copilotExplanation').textContent = "Arterial corridor junctions flow within normal density parameters.";
    } else {
        document.getElementById('copilotExplanation').textContent = "Abnormal eastbound queue growth on J2 suggests incident blockage. Recommends bypass diversion to avoid gridlock propagating upstream to J1.";
    }

    // Update Digital Twin Simulator Matrix Rows
    const tbody = document.getElementById('dtSimulatorBody');
    tbody.innerHTML = '';
    const mocksCands = [
        { name: "DIVERT TRAFFIC", delay: -31.0, queue: -30.0, em: -14.2, eta: 0.0, score: 0.915, best: true },
        { name: "EXTEND GREEN", delay: -18.0, queue: -12.0, em: -8.1, eta: 4.2, score: 0.824, best: false },
        { name: "EMERGENCY PRIORITY", delay: 8.0, queue: 12.0, em: 5.0, eta: -48.0, score: 0.650, best: false },
        { name: "DO NOTHING", delay: 42.0, queue: 61.0, em: 35.0, eta: 24.5, score: 0.210, best: false }
    ];
    mocksCands.forEach(c => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--border-color)';
        tr.style.backgroundColor = c.best ? 'rgba(59, 130, 246, 0.1)' : 'transparent';
        const delayCol = c.delay <= 0 ? 'var(--emerald)' : 'var(--rose)';
        const queueCol = c.queue <= 0 ? 'var(--emerald)' : 'var(--rose)';
        
        tr.innerHTML = `
            <td style="padding: 10px; font-weight: bold; color: var(--text-main);">${c.name} ${c.best ? '★' : ''}</td>
            <td style="padding: 10px; color: ${delayCol};">${c.delay > 0 ? '+' : ''}${c.delay.toFixed(1)}%</td>
            <td style="padding: 10px; color: ${queueCol};">${c.queue > 0 ? '+' : ''}${c.queue.toFixed(1)}%</td>
            <td style="padding: 10px; color: var(--text-main);">${c.eta > 0 ? '+' : ''}${c.eta.toFixed(1)}s</td>
            <td style="padding: 10px; color: ${c.em <= 0 ? 'var(--emerald)' : 'var(--rose)'};">${c.em > 0 ? '+' : ''}${c.em.toFixed(1)}%</td>
            <td style="padding: 10px; font-weight: bold; color: var(--cyan);">${c.score.toFixed(3)}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Scenario stepping bindings
document.getElementById('btnNextStep').addEventListener('click', () => {
    let nextIdx = (currentTimelineIndex + 1) % TIMELINE_STEPS.length;
    applyTimelineStep(nextIdx);
});

document.getElementById('btnRunDemo').addEventListener('click', () => {
    if (demoTimer) clearInterval(demoTimer);
    let step = 0;
    applyTimelineStep(0);
    demoTimer = setInterval(() => {
        step++;
        if (step >= TIMELINE_STEPS.length) {
            clearInterval(demoTimer);
        } else {
            applyTimelineStep(step);
        }
    }, 2500); // Step scenario automatically every 2.5s
});

// Telemetry & Canvas Logic (kept similar to original)
async function fetchStateData() {
    // If timeline is not in 'normal' state, let manual/demo scenario overwrite live state polling
    if (currentTimelineIndex !== 0) return;
    
    try {
        const targetJunction = document.getElementById('actionTargetJunction').value || 'J2';
        const evalRes = await fetch(`${API_BASE}/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                horizon_seconds: 180,
                junction_id: targetJunction,
                strategy_type: currentStrategy || 'diversion'
            })
        });

        if (evalRes.ok) {
            const agentData = await evalRes.json();
            updateMultiAgentUI(agentData);
            
            if (agentData.situation) {
                const sit = agentData.situation;
                document.getElementById("metricDelay").textContent = sit.avg_waiting_time_s.toFixed(2) + "s";
                document.getElementById("metricQueue").textContent = sit.queue_length_m.toFixed(1) + "m";
                document.getElementById("metricSpeed").textContent = sit.avg_speed_kmh.toFixed(1) + "km/h";
                document.getElementById("metricVehicles").textContent = sit.active_vehicles;
            }
        }
    } catch (err) {
        // Fallback mockup
        const elapsed = Date.now() / 1000;
        liveData = {
            network_metrics: { active_vehicles: 124 + Math.floor(Math.sin(elapsed)*10), avg_waiting_time_s: (0.24 + Math.sin(elapsed)*0.05).toFixed(2), avg_speed_kmh: 39.6, mean_queue_length_m: 30.0 },
            junctions: {
                "J1": { phase: Math.floor(elapsed / 10) % 2, total_queue_m: 25.0 },
                "J2": { phase: Math.floor(elapsed / 8) % 2, total_queue_m: 35.0 },
                "J3": { phase: Math.floor(elapsed / 12) % 2, total_queue_m: 18.0 }
            }
        };
        updateTelemetryUI(liveData);
    }
}

function updateMultiAgentUI(data) {
    if (!data) return;

    if (data.prediction) {
        const pred = data.prediction;
        const probPct = Math.round(pred.congestion_probability * 100);
        document.getElementById('forecastProb').textContent = probPct + "%";
        document.getElementById('forecastQueue').textContent = pred.predicted_queue_5min_m.toFixed(1) + "m";
        const trendEl = document.getElementById('forecastTrend');
        if (pred.will_congest_5min) {
            trendEl.textContent = "▲ CRITICAL";
            trendEl.style.color = "var(--rose)";
        } else {
            trendEl.textContent = "▼ STABLE";
            trendEl.style.color = "var(--emerald)";
        }
    }

    if (data.fingerprint) {
        const fp = data.fingerprint;
        document.getElementById('trafficFingerprintBadge').textContent = `Fingerprint: ${fp.pattern_type}`;
        document.getElementById('fingerprintSimilarity').textContent = `Pattern match: ${Math.round(fp.dataset_similarity_score * 100)}%`;
        
        const factorsContainer = document.getElementById('fingerprintFactors');
        factorsContainer.innerHTML = '';
        Object.entries(fp.factors).forEach(([key, val]) => {
            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.fontSize = '12px';
            row.innerHTML = `<span style="color: var(--text-muted); text-transform: capitalize;">${key.replace('_', ' ')}</span><span style="font-weight: bold; color: var(--text-main);">${Math.round(val * 100)}%</span>`;
            factorsContainer.appendChild(row);
        });
    }

    if (data.recommendation) {
        const rec = data.recommendation;
        document.getElementById('copilotRecommends').textContent = `RECOMMENDED: ${rec.strategy.replace('_', ' ').toUpperCase()}`;
        document.getElementById('copilotExplanation').textContent = rec.explanation;
        document.getElementById('copilotConfidence').textContent = `Confidence: ${Math.round(rec.confidence * 100)}%`;
    }

    if (data.candidates) {
        const tbody = document.getElementById('dtSimulatorBody');
        tbody.innerHTML = '';
        data.candidates.forEach(c => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid var(--border-color)';
            tr.style.backgroundColor = c.is_best ? 'rgba(59, 130, 246, 0.1)' : 'transparent';
            
            const delayColor = c.delay_change_pct <= 0 ? 'var(--emerald)' : 'var(--rose)';
            const queueColor = c.queue_change_pct <= 0 ? 'var(--emerald)' : 'var(--rose)';
            const emColor = c.emissions_change_pct <= 0 ? 'var(--emerald)' : 'var(--rose)';

            tr.innerHTML = `
                <td style="padding: 10px; font-weight: bold; color: var(--text-main);">${c.strategy_type.replace('_', ' ').toUpperCase()} ${c.is_best ? '★' : ''}</td>
                <td style="padding: 10px; color: ${delayColor};">${c.delay_change_pct > 0 ? '+' : ''}${c.delay_change_pct.toFixed(1)}%</td>
                <td style="padding: 10px; color: ${queueColor};">${c.queue_change_pct > 0 ? '+' : ''}${c.queue_change_pct.toFixed(1)}%</td>
                <td style="padding: 10px; color: var(--text-main);">${c.emergency_eta_change_sec.toFixed(1)}s</td>
                <td style="padding: 10px; color: ${emColor};">${c.emissions_change_pct > 0 ? '+' : ''}${c.emissions_change_pct.toFixed(1)}%</td>
                <td style="padding: 10px; font-weight: bold; color: var(--cyan);">${c.score.toFixed(3)}</td>
            `;
            tbody.appendChild(tr);
        });
    }
}

function updateTelemetryUI(data) {
    if (!data || !data.network_metrics) return;
    const nm = data.network_metrics;
    document.getElementById("metricDelay").textContent = nm.avg_waiting_time_s + "s";
    document.getElementById("metricQueue").textContent = nm.mean_queue_length_m + "m";
    document.getElementById("metricSpeed").textContent = nm.avg_speed_kmh + "km/h";
    document.getElementById("metricVehicles").textContent = nm.active_vehicles;
}

function renderCanvas() {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width, h = canvas.height, centerY = h / 2;
    const jx = { J1: w * 0.2, J2: w * 0.5, J3: w * 0.8 };

    // Roads
    ctx.fillStyle = "#1e293b";
    ctx.fillRect(40, centerY - 25, w - 80, 50); // E-W
    
    ctx.strokeStyle = "#475569"; ctx.lineWidth = 2; ctx.setLineDash([12, 12]);
    ctx.beginPath(); ctx.moveTo(40, centerY); ctx.lineTo(w - 40, centerY); ctx.stroke();
    ctx.setLineDash([]);

    Object.values(jx).forEach(x => {
        ctx.fillStyle = "#1e293b";
        ctx.fillRect(x - 20, 30, 40, h - 60);
    });

    // Event Highlight / Congestion Spreading
    if (currentTimelineIndex > 0) {
        const targetX = jx.J2;
        let scale = 1;
        if (currentTimelineIndex === 1) scale = 1.1; // Anomaly alert
        if (currentTimelineIndex > 3) scale = 1.5;   // Spillover spreads
        
        ctx.strokeStyle = currentTimelineIndex > 3 ? 'rgba(239, 68, 68, 0.8)' : 'rgba(245, 158, 11, 0.8)';
        ctx.lineWidth = 3;
        ctx.setLineDash([8, 8]);
        let tOffset = (Date.now() / 50) % 16;
        ctx.lineDashOffset = -tOffset;
        ctx.strokeRect(targetX - 40 * scale, centerY - 40 * scale, 80 * scale, 80 * scale);
        ctx.setLineDash([]);
    }

    function drawSignal(x, y, isGreen, name) {
        ctx.fillStyle = "#0f172a"; ctx.strokeStyle = "#334155"; ctx.lineWidth = 2;
        ctx.fillRect(x - 14, y - 28, 28, 56); ctx.strokeRect(x - 14, y - 28, 28, 56);

        ctx.fillStyle = isGreen ? "#10b981" : "#334155";
        if (isGreen) { ctx.shadowColor = "#10b981"; ctx.shadowBlur = 12; }
        ctx.beginPath(); ctx.arc(x, y - 12, 8, 0, Math.PI * 2); ctx.fill(); ctx.shadowBlur = 0;

        ctx.fillStyle = !isGreen ? "#ef4444" : "#334155";
        if (!isGreen) { ctx.shadowColor = "#ef4444"; ctx.shadowBlur = 12; }
        ctx.beginPath(); ctx.arc(x, y + 12, 8, 0, Math.PI * 2); ctx.fill(); ctx.shadowBlur = 0;

        ctx.fillStyle = "#94a3b8"; ctx.font = "bold 11px Inter"; ctx.textAlign = "center";
        ctx.fillText(name, x, y - 36);
    }

    const j1Green = liveData?.junctions?.J1?.phase % 2 === 0;
    const j2Green = liveData?.junctions?.J2?.phase % 2 === 0;
    const j3Green = liveData?.junctions?.J3?.phase % 2 === 0;

    drawSignal(jx.J1, centerY, j1Green, "J1");
    drawSignal(jx.J2, centerY, j2Green, "J2 (Hub)");
    drawSignal(jx.J3, centerY, j3Green, "J3");

    // Queue Bars
    function drawQueueBar(x, y, lengthM) {
        const barW = Math.min(80, (lengthM || 0.0) * 1.5);
        ctx.fillStyle = "rgba(245, 158, 11, 0.2)"; ctx.fillRect(x - 40, y + 36, 80, 8);
        ctx.fillStyle = "#f59e0b"; ctx.fillRect(x - 40, y + 36, barW || 0, 8);
    }

    let q1 = 20.0, q2 = 30.0, q3 = 15.0;
    if (currentTimelineIndex === 1) { q2 = 45.0; }
    if (currentTimelineIndex > 1) { q2 = 65.0; q1 = 35.0; }
    if (currentTimelineIndex === 8) { q1 = 10.0; q2 = 12.0; q3 = 8.0; } // Cleared outcome

    drawQueueBar(jx.J1, centerY, q1);
    drawQueueBar(jx.J2, centerY, q2);
    drawQueueBar(jx.J3, centerY, q3);

    // Vehicles
    const t = Date.now() / 300.0;
    ctx.fillStyle = "#3b82f6";
    for (let i = 0; i < 12; i++) {
        const vx = (40 + (t * 40 + i * 65) % (w - 80));
        ctx.fillRect(vx, centerY - 6, 12, 6);
    }

    // Highlight Ambulance priority corridor if active
    if (currentTimelineIndex >= 7) {
        ctx.strokeStyle = "rgba(255, 255, 255, 0.8)";
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(jx.J1, centerY);
        ctx.lineTo(jx.J3, centerY);
        ctx.stroke();
    }

    if (gameState.session_active) requestAnimationFrame(renderCanvas);
}

// Leaderboard Logic
async function fetchLeaderboard() {
    try {
        const res = await fetch(`${API_BASE}/game/leaderboard`);
        if(res.ok) {
            const data = await res.json();
            populateLeaderboard(data);
        }
    } catch(e) {
        populateLeaderboard([
            {player: "TrafficGod", score: 14500, mode: "challenge"},
            {player: "SUMOMaster", score: 12300, mode: "free_play"},
            {player: gameState.player_name || "Player1", score: gameState.total_points, mode: gameState.mode},
            {player: "Newbie", score: 450, mode: "easy"}
        ].sort((a,b)=>b.score - a.score));
    }
}

function populateLeaderboard(data) {
    const tbody = document.getElementById('leaderboardBody');
    tbody.innerHTML = '';
    data.slice(0, 10).forEach(r => {
        let tr = document.createElement('tr');
        tr.innerHTML = `<td>${r.player}</td><td>${r.score}</td><td><span class="badge mode-badge" style="font-size:10px;">${r.mode}</span></td>`;
        if (r.player === gameState.player_name) tr.style.backgroundColor = "rgba(16, 185, 129, 0.2)";
        tbody.appendChild(tr);
    });
}

// Initial draw
renderCanvas();
renderTimeline();
applyTimelineStep(0);

