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
    gameState.player_name = document.getElementById('playerName').value || 'Player1';
    
    let payload = {
        player_name: gameState.player_name,
        mode: gameState.mode,
        difficulty: gameState.difficulty
    };
    if (gameState.mode === 'challenge') payload.challenge_id = document.getElementById('challengeSelector').value;
    
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
    document.getElementById('hudPlayerName').textContent = gameState.player_name;
    document.getElementById('hudModeBadge').textContent = gameState.mode.replace('_', ' ').toUpperCase();
    
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

async function fetchEvent() {
    if(!gameState.session_active || currentState !== STATES.PLAYING) return;
    
    try {
        const res = await fetch(`${API_BASE}/game/event`);
        if(res.ok) {
            const ev = await res.json();
            if(ev && !ev.resolved && !ev.expired) {
                gameState.active_event = ev;
                triggerEvent(ev);
            }
        }
    } catch(e) {
        // Fallback random event generator (10% chance every 2s)
        if(Math.random() < 0.1 && !gameState.active_event) {
            let t = ['rush_hour', 'emergency', 'accident'][Math.floor(Math.random()*3)];
            let j = ['J1', 'J2', 'J3'][Math.floor(Math.random()*3)];
            let ev = { event_type: t, target_junction: j, severity: t==='emergency'?'critical':'high', description: `Detected ${t} at ${j}!`, time_limit_s: 30, remaining_s: 30 };
            gameState.active_event = ev;
            triggerEvent(ev);
        }
    }
}

function triggerEvent(ev) {
    currentState = STATES.EVENT_ACTIVE;
    
    let icon = "⚠️";
    if(ev.event_type === 'emergency') icon = "🚑";
    if(ev.event_type === 'accident') icon = "💥";
    
    document.getElementById('eventIcon').textContent = icon;
    document.getElementById('eventText').textContent = ev.description;
    
    views.alert.className = `event-alert severity-${ev.severity}`;
    
    if(gameState.difficulty === 'easy') {
        document.getElementById('aiHint').classList.remove('hidden');
        document.getElementById('aiHint').textContent = `AI Suggests: Focus on ${ev.target_junction}`;
    } else {
        document.getElementById('aiHint').classList.add('hidden');
    }
    
    document.getElementById('actionTargetJunction').value = ev.target_junction;
}

// Telemetry & Canvas Logic (kept similar to original)
async function fetchStateData() {
    try {
        const res = await fetch(`${API_BASE}/state`);
        if (res.ok) {
            liveData = await res.json();
            updateTelemetryUI(liveData);
        }
    } catch (err) {
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

    // Event Highlight
    if (gameState.active_event && gameState.active_event.target_junction) {
        const targetX = jx[gameState.active_event.target_junction];
        ctx.strokeStyle = gameState.active_event.severity === 'critical' ? 'rgba(239, 68, 68, 0.8)' : 'rgba(245, 158, 11, 0.8)';
        ctx.lineWidth = 3;
        ctx.setLineDash([8, 8]);
        let tOffset = (Date.now() / 50) % 16;
        ctx.lineDashOffset = -tOffset;
        ctx.strokeRect(targetX - 40, centerY - 40, 80, 80);
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
        const barW = Math.min(80, lengthM * 1.5);
        ctx.fillStyle = "rgba(245, 158, 11, 0.2)"; ctx.fillRect(x - 40, y + 36, 80, 8);
        ctx.fillStyle = "#f59e0b"; ctx.fillRect(x - 40, y + 36, barW || 0, 8);
    }

    drawQueueBar(jx.J1, centerY, liveData?.junctions?.J1?.total_queue_m);
    drawQueueBar(jx.J2, centerY, liveData?.junctions?.J2?.total_queue_m);
    drawQueueBar(jx.J3, centerY, liveData?.junctions?.J3?.total_queue_m);

    // Vehicles
    const t = Date.now() / 300.0;
    ctx.fillStyle = "#3b82f6";
    for (let i = 0; i < 12; i++) {
        const vx = (40 + (t * 40 + i * 65) % (w - 80));
        ctx.fillRect(vx, centerY - 6, 12, 6);
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
        // Fallback mock leaderboard
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
