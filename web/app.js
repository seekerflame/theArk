// Ark OS - Main Application Logic
function main() {
    var BASE_RATE = 10;
    var LEVELS = [
        { threshold: 0, name: 'Newcomer', icon: '🌱' },
        { threshold: 100, name: 'Apprentice', icon: '🔨' },
        { threshold: 500, name: 'Journeyer', icon: '⚒️' },
        { threshold: 1500, name: 'Craftsman', icon: '🛠️' },
        { threshold: 5000, name: 'Master', icon: '⚡' },
        { threshold: 15000, name: 'Steward', icon: '👑' }
    ];
    // --- WALLET / IDENTITY SYSTEM ---
    var Wallet = {
        // Generate a simple 12-word mnemonic seed phrase
        generateMnemonic: function () {
            var words = [
                'abundance', 'village', 'solar', 'build', 'harvest', 'freedom',
                'labor', 'token', 'seed', 'grow', 'thrive', 'community',
                'earth', 'water', 'fire', 'air', 'metal', 'wood',
                'create', 'share', 'trust', 'work', 'trade', 'give'
            ];
            var phrase = [];
            for (var i = 0; i < 12; i++) {
                phrase.push(words[Math.floor(Math.random() * words.length)]);
            }
            return phrase.join(' ');
        },
        // Derive a deterministic address from mnemonic
        deriveAddress: function (mnemonic) {
            // Simple deterministic address (Simulated Hash)
            var hash = 0;
            for (var i = 0; i < mnemonic.length; i++) {
                hash = ((hash << 5) - hash) + mnemonic.charCodeAt(i);
                hash |= 0;
            }
            return "0x" + Math.abs(hash).toString(16).padStart(40, '0').substring(0, 40);
        }
    };

    var rawState = {
        currentUser: { name: 'Guest', role: 'worker', mnemonic: null },
        balance: 0,
        history: [],
        xp: 0,
        tasks: [],
        achievements: [],
        streak: 0,
        lastActiveDate: null,
        lastLevel: "Newcomer",
        token: localStorage.getItem('at_token') || null,
        privateSkills: JSON.parse(localStorage.getItem('at_private_skills') || '[]'),
        inventory: JSON.parse(localStorage.getItem('at_private_inventory') || '{}'),
        isBackupReminderVisible: false,
        nodes: [],
        ledger: [],
        lastId: 0,
        currentChannel: 'general',
        pendingSwap: JSON.parse(localStorage.getItem('at_pending_swap') || 'null'),
        focusSession: JSON.parse(localStorage.getItem('at_focus_session') || 'null')
    };

    // Deep Proxy Handler for nested objects
    var stateHandler = {
        set(target, prop, value) {
            if (target[prop] === value) return true; // No change
            target[prop] = value;
            if (window.updateUI) updateUI();
            if (window.saveState) saveState();
            return true;
        },
        get(target, prop) {
            const val = target[prop];
            // Only wrap if it's a plain object or array, and not already proxied
            if (val && typeof val === 'object' && !val._isProxy) {
                const proxy = new Proxy(val, stateHandler);
                Object.defineProperty(val, '_isProxy', { value: true, enumerable: false });
                return proxy;
            }
            return val;
        }
    };

    var appState = new Proxy(rawState, stateHandler);

    // Expose appState globally for external scripts (engagement.js, etc.)
    window.appState = appState;

    // --- AUTH ACTIONS ---
    // --- ENERGY & KARDASHEV POLLING ---
    window.pollEnergy = function () {
        fetch('/api/system/energy')
            .then(r => r.json())
            .then(res => {
                if (res.status === 'success') {
                    const data = res.data;
                    const wattsEl = document.getElementById('node-power-watts');
                    const kwhEl = document.getElementById('node-energy-kwh');
                    const kardashevRealtimeEl = document.getElementById('kardashev-realtime');
                    const kardashevBadgeEl = document.getElementById('kardashev-badge');

                    if (wattsEl) wattsEl.innerText = data.power_watts;
                    if (kwhEl) kwhEl.innerText = data.energy_kwh.toFixed(4);
                    if (kardashevRealtimeEl) kardashevRealtimeEl.innerText = data.kardashev_level.toFixed(8);
                    if (kardashevBadgeEl) kardashevBadgeEl.innerText = `Type ${data.kardashev_level.toFixed(2)} Civilization`;
                }
            })
            .catch(e => console.warn("[ENERGY] Polling failed:", e));
    };
    setInterval(window.pollEnergy, 1000);

    window.loginUser = function (username, password) {
        return apiFetch('/api/login', {
            method: 'POST',
            body: { username, password }
        }).then(data => {
            appState.token = data.token;
            localStorage.setItem('at_token', data.token);
            localStorage.setItem('at_username', username);
            appState.currentUser.name = username;
            appState.currentUser.role = data.user.role;
            appState.currentUser.verified_hours = data.user.verified_hours;
            appState.currentUser.safety_grade = data.user.safety_grade;
            appState.currentUser.hm = data.user.hm;
            appState.balance = data.user.balance;
            return { success: true };

        }).catch(e => {
            console.error("[AUTH] Login failed:", e);
            return { success: false, message: e.message || 'Login service unreachable' };
        });
    };

    window.registerUser = function (username, password) {
        return apiFetch('/api/register', {
            method: 'POST',
            body: { username, password }
        }).then(data => {
            appState.token = data.token;
            localStorage.setItem('at_token', data.token);
            localStorage.setItem('at_username', username);
            appState.currentUser.name = username;
            return { success: true, mnemonic: data.mnemonic };
        }).catch(e => {
            console.error("[AUTH] Registration failed:", e);
            return { success: false, message: e.message || 'Auth service unreachable' };
        });
    };

    // --- AUTHENTICATED API WRAPPER ---
    window.apiFetch = function (url, options = {}) {
        options.headers = options.headers || {};
        if (appState.token) {
            options.headers['Authorization'] = 'Bearer ' + appState.token;
        }
        if (options.body && typeof options.body === 'object') {
            options.body = JSON.stringify(options.body);
            options.headers['Content-Type'] = 'application/json';
        }
        return fetch(url, options).then(res => {
            if (res.status === 429) {
                if (window.notifyUser) {
                    window.notifyUser("System throttle active. Please slow down.", "warn", "Traffic Control");
                } else {
                    console.warn("Too many requests. Please slow down.");
                }
            }
            return res.json();
        }).then(res => {
            if (res && res.status === 'error') {
                throw new Error(res.data?.message || res.message || "Unknown error occurred");
            }
            // Return data if present, else the whole response
            return (res && res.data !== undefined) ? res.data : res;
        }).catch(err => {
            console.error("[API_FETCH_FAIL]", url, err);
            throw err;
        });
    };
    // --- UPDATE UI: SYNC STATE TO DOM ---
    function updateUI() {
        if (!appState.currentUser) return;

        // 1. Levels & XP Sync
        const levelData = getLevelData(appState.xp);
        const nextLevel = LEVELS[LEVELS.indexOf(levelData) + 1] || levelData;
        const xpProgress = ((appState.xp - levelData.threshold) / (nextLevel.threshold - levelData.threshold)) * 100;

        // Update Sidebar
        const sidebarName = document.getElementById('sidebar-username');
        if (sidebarName) sidebarName.innerText = appState.currentUser.name;

        const sidebarLevel = document.getElementById('sidebar-level');
        if (sidebarLevel) sidebarLevel.innerText = `${levelData.icon} ${levelData.name}`;

        const xpFill = document.getElementById('xp-fill-sidebar');
        if (xpFill) xpFill.style.width = `${Math.min(100, xpProgress)}%`;

        const xpText = document.getElementById('xp-text');
        if (xpText) xpText.innerText = `${appState.xp} / ${nextLevel.threshold} XP`;

        const sidebarBalance = document.getElementById('sidebar-balance');
        if (sidebarBalance) sidebarBalance.innerHTML = `${(appState.balance || 0).toFixed(2)} <span style="font-size:0.8rem; color:var(--text-muted);">AT</span>`;

        // --- TIME MOVIE INTEGRATION ---
        const timeWealthDisplay = document.getElementById('time-wealth-display');
        if (timeWealthDisplay) {
            // 1 AT = 1 Hour Liberated
            timeWealthDisplay.innerHTML = `+${(appState.balance || 0).toFixed(2)} <span style="font-size: 0.7rem;">HRS LIBERATED</span>`;
        }

        // --- LIFE CLOCK TICKER ---
        if (!window.lifeClockInterval) {
            let secondsRemaining = 1987654321; // Baseline (approx 63 years)
            window.lifeClockInterval = setInterval(() => {
                const clockEl = document.getElementById('life-clock');
                if (clockEl) {
                    secondsRemaining -= 1;
                    clockEl.innerText = `EST. ${secondsRemaining.toLocaleString()}s REMAINING`;
                }
            }, 1000);
        }

        // 2. Refresh Module UIs
        const activeView = document.querySelector('.app-view:not([style*="display: none"])');
        if (activeView) {
            const viewId = activeView.id.replace('view-', '');
            if (viewId === 'jobs') renderJobBoard();
            if (viewId === 'wallet') renderWalletUI();
            if (viewId === 'techtree') renderTechTree(appState.xp);
            if (viewId === 'leaderboard') renderLeaderboard();
            if (viewId === 'treasury') renderTreasuryUI();
            if (viewId === 'exodus') Exodus.render();
            if (viewId === 'intel') Intel.render();
            if (viewId === 'dashboard' && window.updateDashboardStats) window.updateDashboardStats();

        }

        // 3. Check for Level Up
        if (rawState.lastLevel && rawState.lastLevel !== levelData.name) {
            triggerLevelUp(levelData);
        }
        rawState.lastLevel = levelData.name;
    };

    // --- ADMIN DASHBOARD ---
    window.renderAdminDashboard = function () {
        if (!appState.currentUser || appState.currentUser.role !== 'ADMIN') {
            document.getElementById('view-admin').innerHTML = '<div style="padding:50px; text-align:center; color:#EF4444; font-family:\'JetBrains Mono\';">⛔ ACCESS DENIED. CLEARANCE LEVEL: GOD_MODE REQUIRED.</div>';
            return;
        }

        fetch('/api/evolution')
            .then(r => r.json())
            .then(data => {
                var container = document.getElementById('view-admin');

                // Calculate Time Wealth (Temporal Yield)
                const totalHours = data.verified_mints * 10; // Simplified for UI
                const timeWealth = (totalHours / 150).toFixed(2); // Wealth per capita in this node

                container.innerHTML = `
                <div class="section-header" style="border-bottom: 2px solid #10B981; padding-bottom: 10px; margin-bottom: 20px;">
                    <h2 style="letter-spacing: 2px; text-shadow: 0 0 10px #10B981;">🛰️ NEXUS ACCESS PORTAL</h2>
                    <p style="color: #64748b; font-family:'JetBrains Mono'; font-size: 0.8rem;">[SYSTEM STATE: SECURE] [NODE: THE ARK] [PROTOCOL: PSY_001 ACTIVE]</p>
                </div>
                
                <div class="grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div class="glass-panel" style="border: 1px solid rgba(16, 185, 129, 0.3);">
                        <h3 style="color:#10B981;">CORE METRICS (Sovereign Trio)</h3>
                        <div style="margin-top:15px; font-family:'JetBrains Mono'; font-size:0.85rem; color:var(--text-main); display:flex; flex-direction:column; gap:8px;">
                            <div style="display:flex; justify-content:space-between;">
                                <span>Temporal Yield:</span>
                                <span style="color:#10B981;">+${timeWealth}% Life Liberty</span>
                            </div>
                            <div style="display:flex; justify-content:space-between;">
                                <span>Metabolic Density:</span>
                                <span style="color:#60A5FA;">${(data.metabolic_yield * 100).toFixed(0)}% Efficiency</span>
                            </div>
                            <div style="display:flex; justify-content:space-between;">
                                <span>Entropic Resistance:</span>
                                <span style="color:#FBBF24;">-12.4% Friction</span>
                            </div>
                            <div style="margin-top:10px; border-top:1px dashed rgba(16,185,129,0.1); padding-top:10px;">
                                <div>System Pulse: <span style="color:#10B981; animation: pulse 2s infinite;">ONLINE</span></div>
                                <div>Evolution Cycles: <span style="color:#FBBF24;">${data.evolution_cycles}</span></div>
                                <div>Neural Filter (V/U): <span style="color:#10B981;">${data.verified_mints}</span> / <span style="color:#EF4444;">${data.unverified_count}</span></div>
                            </div>
                            <div id="dunbar-counter" style="margin-top:10px; padding:10px; background:rgba(59,130,246,0.1); border-radius:8px; border:1px solid rgba(59,130,246,0.3);">
                                <div style="font-size:0.7rem; color:#94a3b8; margin-bottom:5px;">DUNBAR MITOSIS (Phase 9)</div>
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span>Population:</span>
                                    <span id="population-count" style="font-weight:bold;">Loading...</span>
                                </div>
                                <div style="width:100%; height:8px; background:rgba(0,0,0,0.3); border-radius:4px; margin-top:5px; overflow:hidden;">
                                    <div id="population-bar" style="height:100%; background:linear-gradient(90deg, #10B981, #3B82F6); width:0%; transition:width 0.5s;"></div>
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 20px; display: flex; flex-direction: column; gap: 10px;">
                            <button onclick="window.adminAction('sync')" class="btn-secondary" style="text-align: left; border: 1px solid rgba(16, 185, 129, 0.2);">🔄 Trigger Universal Sync</button>
                            <button onclick="window.adminAction('verify_all')" class="btn-primary" style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10B981; color:#10B981;">🛡️ Harden Node Ledger</button>
                        </div>
                    </div>

                    <div class="glass-panel" style="border: 1px solid rgba(245, 158, 11, 0.3);">
                        <h3 style="color:#F59E0B;">GOVERNANCE & MINT</h3>
                        <div style="margin-top:10px; display:flex; flex-direction:column; gap:10px;">
                            <input type="number" id="cb-amount" class="input-dark" placeholder="Amount (AT)" style="margin-bottom:0;">
                            <input type="text" id="cb-recipient" class="input-dark" placeholder="Recipient (Sovereign ID)" style="margin-bottom:0;">
                            <button onclick="window.centralBankMint()" class="btn-primary" style="background: linear-gradient(135deg, #F59E0B, #D97706); font-weight:bold;">🖨️ MINT SOVEREIGN AT</button>
                            <div style="font-size:0.7rem; color:#94a3b8; text-align:center; margin-top:5px;">⚠️ Minting requires Oracle consensus in Mainnet.</div>
                        </div>
                    </div>
                </div>

                <div class="glass-panel" style="margin-top:20px; border: 1px solid rgba(16, 185, 129, 0.3); background: rgba(0,0,0,0.5);">
                    <h3 style="color:#10B981; font-size:0.9rem; letter-spacing:1px;">🛰️ GLOBAL MISSION PULSE</h3>
                    <div id="mission-pulse-container" style="height:250px; width:100%; position:relative; overflow:hidden;">
                        <!-- D3 Pulse Injected here -->
                    </div>
                </div>

                <div class="glass-panel" style="margin-top:20px; border: 1px solid rgba(239, 68, 68, 0.3);">
                    <h3 style="color:#EF4444;">ORACLE VERIFICATION QUEUE</h3>
                    <div id="verification-queue" style="margin-top:15px; display:flex; flex-direction:column; gap:10px; max-height:300px; overflow-y:auto;">
                        ${data.unverified_queue.length === 0 ? '<div style="color:#64748b; padding:10px; text-align:center;">NODE HISTORY IS HARDENED. NO PENDING BLOCKS.</div>' : ''}
                        ${data.unverified_queue.map(block => `
                            <div class="block-item" style="background: rgba(15, 23, 42, 0.7); padding: 12px; border-radius: 8px; border-left: 4px solid #EF4444; display:flex; justify-content:space-between; align-items:center; transition: all 0.3s ease;">
                                <div>
                                    <div style="font-weight:bold; color:#f1f5f9; display:flex; align-items:center; gap:8px;">
                                        <span style="background:#EF4444; color:white; font-size:0.6rem; padding:2px 4px; border-radius:2px;">UNVERIFIED</span>
                                        ${block.data.block_type}: ${block.data.task || 'UNNAMED OP'}
                                    </div>
                                    <div style="font-size:0.7rem; color:#94a3b8; font-family:'JetBrains Mono'; margin-top:4px;">HASH: ${block.hash.slice(0, 24)}...</div>
                                    ${block.data.minter ? `<div style="font-size:0.8rem; color:#60A5FA; margin-top:4px;">AGENT: ${block.data.minter} | MAGNITUDE: ${block.data.hours} AT</div>` : ''}
                                </div>
                                <button onclick="window.verifyBlock('${block.hash}')" class="btn-xs" style="background:#10B981; color:white; border-radius:4px; padding:4px 12px; font-weight:bold; border:none; cursor:pointer; box-shadow: 0 0 10px rgba(16,185,129,0.3);">HARDEN</button>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="glass-panel" style="margin-top:20px; background: rgba(0,0,0,0.4);">
                    <h3 style="color:#94a3b8; font-size:0.9rem;">SENTINEL LOGS (LIVE)</h3>
                    <div id="admin-logs" class="terminal-view" style="height:150px; overflow-y:auto; font-size:0.75rem;">Loading logs...</div>
                </div>
                `;
                window.fetchLogs();
                window.renderMissionPulse(data.evolution_cycles);

                // Fetch Dunbar population counter
                fetch('/api/mitosis/status')
                    .then(r => r.json())
                    .then(m => {
                        const popEl = document.getElementById('population-count');
                        const barEl = document.getElementById('population-bar');
                        if (popEl && m.population !== undefined) {
                            const pct = (m.population / m.dunbar_limit * 100).toFixed(1);
                            const color = m.population > 120 ? '#EF4444' : m.population > 100 ? '#F59E0B' : '#10B981';
                            popEl.innerHTML = `<span style="color:${color};">${m.population}</span>/${m.dunbar_limit} (${pct}%)`;
                            if (barEl) barEl.style.width = pct + '%';
                        }
                    })
                    .catch(() => { });
            })
            .catch(e => {
                console.error("[ADMIN] Dashboard load failed:", e);
                document.getElementById('view-admin').innerHTML = '<div class="glass-panel" style="color:#EF4444;">⚠️ Critical Dashboard Failure: Connection Lost</div>';
            });
    };

    window.renderTangle = function () {
        const container = document.getElementById('mission-pulse-container');
        if (!container) return;
        container.innerHTML = '';

        const width = container.clientWidth;
        const height = container.clientHeight;
        const blocks = rawState.ledger || [];

        const svg = d3.select("#mission-pulse-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        // Nodes from blocks, Links from prev_hash (Simulation uses indices for speed)
        const nodes = blocks.slice(-50).map((b, i) => ({
            id: b.id,
            hash: b.hash,
            type: b.type,
            label: b.type.substring(0, 1)
        }));

        const links = [];
        nodes.forEach((n, i) => {
            if (i > 0) {
                // Connect to previous block in sequence (Simulated Tangle)
                links.push({ source: nodes[i - 1].id, target: n.id });
                // Occasionally connect to a random older block for "Tangle" feel
                if (i > 5 && Math.random() > 0.7) {
                    links.push({ source: nodes[i - 5].id, target: n.id });
                }
            }
        });

        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(40))
            .force("charge", d3.forceManyBody().strength(-100))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(15));

        const link = svg.append("g")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke", "rgba(16, 185, 129, 0.15)")
            .attr("stroke-width", 1.5)
            .attr("stroke-dasharray", "5,5");

        const node = svg.append("g")
            .selectAll("g")
            .data(nodes)
            .join("g")
            .call(d3.drag()
                .on("start", (event, d) => {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x; d.fy = d.y;
                })
                .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
                .on("end", (event, d) => {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null; d.fy = null;
                }));

        node.append("circle")
            .attr("r", d => d.type === 'TX' ? 6 : 8)
            .attr("fill", d => {
                if (d.type === 'LABOR') return "#10B981";
                if (d.type === 'TX') return "#3B82F6";
                if (d.type === 'MISSION') return "#FBBF24";
                return "#6B7280";
            })
            .style("filter", "drop-shadow(0 0 5px rgba(16, 185, 129, 0.5))");

        node.append("text")
            .text(d => d.label)
            .attr("font-size", "8px")
            .attr("text-anchor", "middle")
            .attr("dy", ".35em")
            .attr("fill", "white")
            .attr("pointer-events", "none");

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });
    };

    function getLevelData(xp) {
        let current = LEVELS[0];
        for (let l of LEVELS) {
            if (xp >= l.threshold) current = l;
        }
        return current;
    }

    function triggerLevelUp(level) {
        const flash = document.createElement('div');
        flash.className = 'level-up-flash';
        document.body.appendChild(flash);
        setTimeout(() => flash.remove(), 1000);

        showCelebration(`✨ ASCENDED: ${level.name} ✨`);
        logToTerminal(`[EVOLUTION] You have reached Level: ${level.name}!`);
    }

    window.loadState = function () {
        const saved = localStorage.getItem('ose_state');
        if (saved) {
            const data = JSON.parse(saved);
            Object.assign(appState, data);
        }

        // Boot Sequence Integrations
        window.updateStreak();
        window.updateUI();
        console.log("[GAIA] State Synchronized.");
        if (window.Founders) window.Founders.init();
    };

    window.saveState = function () {
        localStorage.setItem('ose_state', JSON.stringify(appState));
        if (appState.focusSession) localStorage.setItem('at_focus_session', JSON.stringify(appState.focusSession));
        else localStorage.removeItem('at_focus_session');
    };

    // --- MONK MODE (FOCUS ECONOMY) ---
    window.startFocus = function () {
        if (appState.focusSession) return alert("Focus session already active.");

        apiFetch('/api/economy/focus/start', { method: 'POST' })
            .then(data => {
                appState.focusSession = {
                    id: data.session_id,
                    start_time: Date.now(),
                    target_duration: 3600 * 1000 // 1 hour in ms
                };
                window.saveState();
                window.resumeFocusTimer();
                logToTerminal("[MONK_MODE] Neural lock engaged. Stay focused.");
            })
            .catch(e => alert("Failed to start focus: " + e.message));
    };

    window.resumeFocusTimer = function () {
        if (window.focusInterval) clearInterval(window.focusInterval);
        window.focusInterval = setInterval(() => {
            if (!appState.focusSession) {
                clearInterval(window.focusInterval);
                return;
            }

            // HUD Elements
            const el = document.getElementById('focus-battery-fill');
            const txt = document.getElementById('focus-timer-text');

            // Large View Elements
            const elLarge = document.getElementById('focus-battery-fill-large');
            const txtLarge = document.getElementById('focus-timer-text-large');

            const elapsed = Date.now() - appState.focusSession.start_time;
            const progress = Math.min(100, (elapsed / appState.focusSession.target_duration) * 100);

            if (el) el.style.width = progress + '%';
            if (elLarge) elLarge.style.width = progress + '%';

            const remaining = Math.max(0, appState.focusSession.target_duration - elapsed);
            const hours = Math.floor(remaining / 3600000);
            const mins = Math.floor((remaining % 3600000) / 60000);
            const secs = Math.floor((remaining % 60000) / 1000);

            const timeStr = `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            const shortStr = `${mins}:${secs.toString().padStart(2, '0')} REMAINING`;

            if (txt) txt.innerText = shortStr;
            if (txtLarge) txtLarge.innerText = timeStr;

            if (progress >= 100) {
                if (el) el.style.background = 'var(--pip-green)';
                if (elLarge) elLarge.style.background = 'var(--pip-green)';
                if (txt) {
                    txt.innerText = "READY TO CLAIM";
                    txt.classList.add('blink');
                }
                if (txtLarge) {
                    txtLarge.innerText = "SYNTHESIS READY";
                    txtLarge.classList.add('blink');
                }

                // --- ENTROPY CHALLENGE ---
                // Every 10 minutes, regenerate a local "Attention Proof"
                if (Math.floor(elapsed / 60000) % 10 === 0 && !window.lastEntropyUpdate) {
                    window.lastEntropyUpdate = true;
                    console.log("[SOVEREIGN] Attention Entropy Verified locally.");
                    setTimeout(() => { window.lastEntropyUpdate = false; }, 60000);
                }
            }
        }, 1000);
    };

    // --- SOVEREIGN DATA SALE ---
    window.authorizeDataSale = function (packetId) {
        const mnemonic = prompt("🔐 Enter Mnemonic Seed to authorize local data signing:");
        if (!mnemonic) return;

        apiFetch('/api/sovereign/data-sale/sign', {
            method: 'POST',
            body: {
                mnemonic: mnemonic,
                packet_id: packetId,
                buyer: "GPM_RESEARCH_FOUNDATION"
            }
        }).then(data => {
            showCelebration(`💰 SOVEREIGN SALE SIGNED +${data.reward} AT`);
            logToTerminal(`[SOVEREIGN] Data Sale authorized. Reward: ${data.reward} AT`);
            syncWithLedger();
        }).catch(e => alert(e.message));
    };

    window.claimFocus = function () {
        if (!appState.focusSession) return;

        apiFetch('/api/economy/focus/claim', {
            method: 'POST',
            body: { session_id: appState.focusSession.id }
        }).then(data => {
            logToTerminal(`[MONK_MODE] Synthesis complete. +1.0 AT minted.`);
            appState.focusSession = null;
            window.saveState();
            syncWithLedger();
            // Show result
            showCelebration("🧘 FOCUS TRANSCENDED +1 AT");
        }).catch(e => alert(e.message));
    };

    window.fetchLogs = function () {
        fetch('/api/logs')
            .then(r => r.json())
            .then(logs => {
                var logBox = document.getElementById('admin-logs');
                if (!logBox) return;
                logBox.innerHTML = '';
                for (let [file, lines] of Object.entries(logs)) {
                    logBox.innerHTML += `<div style="color:#FBBF24; margin-top:10px; border-bottom:1px solid rgba(16,185,129,0.1);">${file}</div>`;
                    lines.forEach(l => {
                        logBox.innerHTML += `<div style="color:#94a3b8;">${l}</div>`;
                    });
                }
            })
            .catch(e => {
                console.warn("[ADMIN] Log fetch failed:", e);
                const logBox = document.getElementById('admin-logs');
                if (logBox) logBox.innerHTML = '⚠️ Failed to synchronize logs.';
            });
    }

    window.adminAction = function (action) {
        let endpoint = '/api/ledger/verify_all'; // Updated to match hardened ledger API if we add it
        if (action === 'sync') endpoint = '/api/sync';

        apiFetch(endpoint, { method: 'POST' })
            .then(data => {
                logToTerminal(`[ADMIN] Action ${action}: ${data.status}`);
                window.renderAdminDashboard();
            })
            .catch(e => alert("Error: " + e));
    };

    window.verifyBlock = function (blockHash) {
        logToTerminal(`[ORACLE] Hardening block ${blockHash.slice(0, 8)}...`);
        apiFetch('/api/ledger/verify', {
            method: 'POST',
            body: { hash: blockHash }
        }).then(data => {
            if (data.status === 'success') {
                logToTerminal(`[ORACLE] Block ${blockHash.slice(0, 8)} VERIFIED.`);
                window.renderAdminDashboard();
                syncWithLedger(); // Refresh balances
            } else {
                alert("Verification failed: " + data.message);
            }
        }).catch(e => {
            logToTerminal(`[ORACLE] Verification Error: ${e}`);
        });
    };

    window.centralBankMint = function () {
        var amt = parseFloat(document.getElementById('cb-amount').value);
        var rec = document.getElementById('cb-recipient').value;
        if (!amt || !rec) return alert("Fill fields.");

        apiFetch('/api/mint', {
            method: 'POST',
            body: {
                minter: rec,
                task: "Central Bank Grant",
                hours: amt / 10,
                timestamp: Date.now()
            }
        }).then(data => {
            alert("Funds injected: " + data.status);
            syncWithLedger();
        }).catch(e => {
            console.error("[ADMIN] Minting action failed:", e);
            alert("Sovereign minting failed.");
        });
    };

    // --- SOVEREIGN IDENTITY LOGIC ---
    window.showAuthMode = function (mode) {
        document.getElementById('auth-login-form').style.display = mode === 'login' ? 'block' : 'none';
        document.getElementById('auth-register-form').style.display = mode === 'register' ? 'block' : 'none';
        document.getElementById('auth-restore-form').style.display = mode === 'restore' ? 'block' : 'none';
        document.getElementById('auth-seed-display').style.display = 'none';

        // Toggle Active Button Style
        const btnLogin = document.getElementById('btn-mode-login');
        const btnReg = document.getElementById('btn-mode-register');
        const btnRestore = document.getElementById('btn-mode-restore');

        const btns = { login: btnLogin, register: btnReg, restore: btnRestore };
        const colors = { login: '#10B981', register: '#8B5CF6', restore: '#F59E0B' };

        Object.keys(btns).forEach(m => {
            if (btns[m]) {
                if (m === mode) {
                    btns[m].style.background = colors[m];
                    btns[m].style.color = 'white';
                } else {
                    btns[m].style.background = 'transparent';
                    btns[m].style.color = '#94a3b8';
                }
            }
        });
        document.getElementById('auth-error').style.display = 'none';
    };

    window.performRegister = function () {
        const user = document.getElementById('reg-username').value;
        const pass = document.getElementById('reg-password').value;
        const errorEl = document.getElementById('auth-error');

        if (!user || !pass) {
            errorEl.style.display = 'block';
            errorEl.innerText = "Please enter both username and password.";
            return;
        }

        fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass })
        })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    // Show Mnemonic Display instead of immediate redirect
                    document.getElementById('auth-register-form').style.display = 'none';
                    document.getElementById('auth-seed-display').style.display = 'block';
                    document.getElementById('seed-phrase-box').innerText = data.mnemonic;

                    // Pre-auth the state
                    appState.token = data.token;
                    localStorage.setItem('at_token', data.token);
                    localStorage.setItem('at_username', user);
                    appState.currentUser.name = user;
                } else {
                    errorEl.style.display = 'block';
                    errorEl.innerText = data.message;
                }
            })
            .catch(err => {
                errorEl.style.display = 'block';
                errorEl.innerText = "Connection Error: " + err;
            });
    };

    window.performRestore = function () {
        const user = document.getElementById('restore-username').value;
        const mnemonic = document.getElementById('restore-mnemonic').value;
        const pass = document.getElementById('restore-password').value;
        const errorEl = document.getElementById('auth-error');

        if (!user || !mnemonic || !pass) {
            errorEl.style.display = 'block';
            errorEl.innerText = "Username, mnemonic, and new password are required.";
            return;
        }

        fetch('/api/restore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, mnemonic: mnemonic, password: pass })
        })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    alert("Identity Restored Successfully. You can now login with your new password.");
                    showAuthMode('login');
                } else {
                    errorEl.style.display = 'block';
                    errorEl.innerText = data.message;
                }
            })
            .catch(err => {
                errorEl.style.display = 'block';
                errorEl.innerText = "Restore Error: " + err;
            });
    };

    window.performLogin = function () {
        const user = document.getElementById('login-username').value;
        const pass = document.getElementById('login-password').value;
        const errorEl = document.getElementById('auth-error');

        fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass })
        })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    // Login Success
                    appState.token = data.token;
                    localStorage.setItem('at_token', data.token);
                    appState.currentUser.name = user;
                    appState.currentUser.role = data.user.role;

                    alert("Welcome back, " + user);
                    switchView('dashboard');
                    updateUI();

                    if (window.APP_CONFIG && window.APP_CONFIG.modules) {
                        renderSidebar(window.APP_CONFIG.modules);
                    }
                } else {
                    errorEl.style.display = 'block';
                    errorEl.innerText = data.message;
                }
            })
            .catch(err => {
                errorEl.style.display = 'block';
                errorEl.innerText = "Login Failed: " + err;
            });
    };

    // --- SECURITY: DOOR CODE SYSTEM ---
    window.checkSecurity = function () {
        if (!localStorage.getItem('village_password')) {
            var pwd = prompt("🔒 Restricted System. Enter Village Door Code:");
            if (pwd) {
                localStorage.setItem('village_password', pwd);
            }
        }
    };
    // Run immediately
    window.checkSecurity();

    // INTERCEPT: Add Authorization Header to ALL fetches and UNWRAP Standardized Responses
    const { fetch: originalFetch } = window;
    window.fetch = async (...args) => {
        let [resource, config] = args;
        config = config || {};
        config.headers = config.headers || {};

        // Add JWT Token
        if (appState.token) {
            config.headers['Authorization'] = 'Bearer ' + appState.token;
        }

        const response = await originalFetch(resource, config);

        // Handle Expired Token
        if (response.status === 401 && appState.token && resource.includes('/api/')) {
            console.warn("🔒 401 Unauthorized encountered. Session may be invalid.");
            // Optional: Auto-logout or token refresh logic
        }

        // Automatic Unwrapping for Ark API
        if (typeof resource === 'string' && resource.includes('/api/')) {
            const originalJson = response.json.bind(response);
            response.json = async () => {
                try {
                    const json = await originalJson();
                    // If it follows the standard wrapper format {status, data, request_id, timestamp}
                    if (json && json.status && json.data !== undefined && json.request_id) {
                        return json.data;
                    }
                    return json;
                } catch (e) {
                    return null;
                }
            };
        }

        return response;
    };



    // --- JOB BOARD FILTER HELPER ---
    window.filterJobs = function () {
        renderJobBoard();
    }

    // --- WIKI PAGES LIST (Categorized) ---
    window.wikiCategories = [
        {
            name: 'Core Protocols',
            icon: '📜',
            color: '#10B981',
            pages: [
                { label: 'Master SOP Index', path: 'library/Master_SOP_Index.md', desc: 'Central hub for all operations' },
                { label: 'Whitepaper', path: 'library/Abundance_Token_Master_Whitepaper.md', desc: 'Token economics & vision' },
                { label: 'AFK Protocol', path: 'library/AFK_PROTOCOL.md', desc: 'Autonomous operation guide' }
            ]
        },
        {
            name: 'Operations',
            icon: '⚙️',
            color: '#3B82F6',
            pages: [
                { label: 'User Checklist', path: 'library/USER_CHECKLIST.md', desc: 'Onboarding requirements' },
                { label: 'Communication Channel', path: 'library/COMMUNICATION_CHANNEL.md', desc: 'Village comms setup' },
                { label: 'Mission Report', path: 'library/MISSION_REPORT.md', desc: 'Daily status updates' }
            ]
        },
        {
            name: 'System',
            icon: '🔧',
            color: '#8B5CF6',
            pages: [
                { label: 'README', path: 'library/README.md', desc: 'System overview' },
                { label: 'Presentation Script', path: 'library/PRESENTATION_SCRIPT.md', desc: 'Demo walkthrough' }
            ]
        }
    ];
    // Flatten for search compatibility
    window.wikiPages = window.wikiCategories.flatMap(c => c.pages);

    // --- JOB BOARD LOGIC ---
    window.claimTask = function (id) {
        var task = appState.tasks.find(t => t.id === id || t.quest_id === id);
        if (!task) return alert('Quest not found');

        const questId = task.quest_id || task.id;
        const offerType = task.offer_type || 'FIXED';

        // Show different UI based on offer type
        if (offerType === 'NEGOTIATE') {
            const acceptTerms = confirm(`Quest: ${task.title}\nProposed: ${task.base_at || task.bounty_at} AT\n\nAccept these terms? (Cancel to counter-offer)`);
            if (!acceptTerms) {
                const counter = prompt(`Enter your counter-offer in AT:`);
                if (counter) {
                    apiFetch('/api/quests/claim', {
                        method: 'POST',
                        body: { quest_id: questId, accept_terms: false, counter_offer: parseFloat(counter) }
                    }).then(data => {
                        logToTerminal(`[QUEST] Counter-offer sent for: ${task.title}`);
                        syncWithLedger();
                    });
                }
                return;
            }
        }

        // Claim quest (FIXED, ROLE_MULTIPLIED, BARTER, or accepted NEGOTIATE)
        apiFetch('/api/quests/claim', {
            method: 'POST',
            body: { quest_id: questId, accept_terms: true }
        }).then(data => {
            if (data.status === 'claimed' || data.status === 'claimed_barter') {
                logToTerminal(`[QUEST] Claimed: ${task.title} for ${data.agreed_at || 'TBD'} AT`);
                task.status = 'IN_PROGRESS';
                task.worker = appState.currentUser.name;
                saveState();
                syncWithLedger();
                renderJobBoard();
            } else {
                alert("Claim Failed: " + (data.message || 'Unknown error'));
            }
        }).catch(e => {
            console.error('[QUEST] Claim error:', e);
            alert('Failed to claim quest');
        });
    };

    window.delegateTask = function (id) {
        var name = prompt("Delegate to whom?");
        if (!name) return;
        var task = appState.tasks.find(t => t.id === id || t.quest_id === id);
        if (task) {
            task.status = 'ASSIGNED';
            task.assignee = name;
            saveState(); updateUI();
            logToTerminal(`[JOB] Delegated ${task.title} to ${name}`);
        }
    };

    window.dropTask = function (id) {
        if (!confirm("Abandon this task?")) return;
        var task = appState.tasks.find(t => t.id === id || t.quest_id === id);
        if (task) {
            task.status = 'OPEN';
            task.assignee = null;
            task.party = [];
            saveState(); updateUI();
            logToTerminal(`[JOB] Dropped: ${task.title}`);
        }
    };

    // Validate a completed quest (Owner/Oracle only)
    window.validateQuest = function (questId, approved = true) {
        const feedback = approved ? '' : prompt('Reason for rejection:') || '';

        apiFetch('/api/quests/validate', {
            method: 'POST',
            body: {
                quest_id: questId,
                approved: approved,
                feedback: feedback
            }
        }).then(data => {
            if (data.status === 'completed') {
                logToTerminal(`[ORACLE] Quest validated! ${data.worker} earned ${data.at_minted} AT`);
                alert(`Quest Completed!\n\nWorker: ${data.worker}\nAT Minted: ${data.at_minted}`);
                syncWithLedger();
                renderJobBoard();
            } else if (data.status === 'rejected') {
                logToTerminal(`[ORACLE] Quest rejected: ${feedback}`);
                alert('Quest sent back for revisions.');
                renderJobBoard();
            } else {
                alert('Validation failed: ' + (data.message || 'Unknown error'));
            }
        }).catch(e => {
            console.error('[ORACLE] Validation error:', e);
        });
    };

    function renderJobBoard() {
        var list = document.getElementById('seh7-jobs');
        var myJobsList = document.getElementById('my-jobs-list');

        if (list) {
            // Open Jobs
            // SORT: Highest AT First (use bounty_at from quests or bounty)
            var openTasks = appState.tasks.filter(t => t.status === 'OPEN').sort((a, b) => (b.bounty_at || b.bounty || 0) - (a.bounty_at || a.bounty || 0));

            // FILTER
            var filterEl = document.getElementById('job-filter');
            var filterVal = filterEl ? filterEl.value : 'ALL';
            if (filterVal !== 'ALL') {
                openTasks = openTasks.filter(t => t.category === filterVal);
            }

            list.innerHTML = openTasks.map(t => {
                // Modular Color System
                let borderColor = '#94a3b8'; // Default Slate
                let badgeColor = 'rgba(148, 163, 184, 0.1)';
                let textColor = 'var(--text-main)';

                if (t.category === 'CRITICAL') {
                    borderColor = '#EF4444'; // Red
                    badgeColor = 'rgba(239, 68, 68, 0.2)';
                    textColor = '#FCA5A5';
                } else if (t.category === 'GROWTH') {
                    borderColor = '#10B981'; // Green
                    badgeColor = 'rgba(16, 185, 129, 0.2)';
                    textColor = '#6EE7B7';
                } else if (t.category === 'KNOWLEDGE') {
                    borderColor = '#3B82F6'; // Blue
                    badgeColor = 'rgba(59, 130, 246, 0.2)';
                    textColor = '#93C5FD';
                } else if (t.category === 'EXTREME') {
                    borderColor = '#F59E0B'; // Orange/Gold
                    badgeColor = 'rgba(245, 158, 11, 0.2)';
                    textColor = '#FCD34D';
                }

                return `
                <div class="quest-card" style="background:rgba(16,185,129,0.05); padding:15px; border-radius:12px; border-left: 4px solid ${borderColor}; margin-bottom:15px; display:flex; flex-direction:column; gap:8px;">
                    <!-- Header Row -->
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap: 10px;">
                        <div style="flex: 1;">
                            <h4 style="margin:0; color:#eff6ff; font-size:1.1rem; line-height: 1.2;">${t.icon || '📜'} ${t.title}</h4>
                        </div>
                        <div style="display:flex; gap:5px; flex-shrink: 0; align-items: center;">
                            <span style="font-size:0.75rem; background:${badgeColor}; padding:4px 8px; border-radius:4px; color:${textColor}; font-weight:600; text-transform: uppercase;">${t.category}</span>
                            <div style="background:rgba(255, 215, 0, 0.1); color:#FBBF24; font-weight:bold; padding:4px 8px; border-radius:6px; font-size:0.9rem; border: 1px solid rgba(251, 191, 36, 0.3);">
                                ${t.bounty_at} AT
                            </div>
                        </div>
                    </div>
                    
                    <p style="font-size:0.9rem; color:var(--text-main); margin:0; line-height:1.4;">${t.description}</p>
                    <div style="font-size:0.8rem; color:#64748b; display:flex; gap:10px; align-items:center;">
                         <span>📍 ${t.location || 'Village'}</span>
                         <span>⚡ Req: ${t.requirements ? t.requirements.join(', ') : 'None'}</span>
                    </div>
                    ${t.party && t.party.length > 0 ? `
                    <div style="font-size:0.8rem; color:#A855F7; display:flex; gap:8px; align-items:center; margin-top:5px;">
                         <span>👥 Party (${t.party.length}): ${t.party.join(', ')}</span>
                    </div>
                    ` : ''}

                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:5px; border-top:1px solid rgba(16,185,129,0.05); padding-top:10px;">
                        <div style="font-size:0.8rem; color:#64748b;">⏳ ${t.estimated_time || 'Flexible'}</div>
                        <div style="display:flex; gap:8px;">
                            <button onclick="delegateTask('${t.quest_id}')" style="background:transparent; border:1px solid rgba(16,185,129,0.2); color:var(--text-main); font-size:0.8rem; padding:6px 12px; border-radius:6px; cursor:pointer;">👉 Delegate</button>
                            <button onclick="claimTask('${t.quest_id}')" style="background:${borderColor}; border:none; color:black; font-weight:600; font-size:0.8rem; padding:6px 16px; border-radius:6px; cursor:pointer; box-shadow:0 4px 6px rgba(0,0,0,0.3);">✋ Join Party</button>
                        </div>
                    </div>
                </div>
            `}).join('');
        }

        // My Jobs (Assigned to Me)
        if (myJobsList) {
            var myTasks = appState.tasks.filter(t => t.assignee === appState.currentUser.name && (t.status === 'ASSIGNED' || t.status === 'PENDING_VERIFICATION'));
            myJobsList.innerHTML = myTasks.length ? myTasks.map(t => {
                const isPending = t.status === 'PENDING_VERIFICATION';
                return `
                <div class="quest-card" style="background:${isPending ? 'rgba(139, 92, 246, 0.1)' : 'rgba(59, 130, 246, 0.1)'}; padding:15px; border-radius:12px; border-left: 4px solid ${isPending ? '#8B5CF6' : '#3B82F6'}; margin-bottom:15px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0; color:#eff6ff;">${t.title}</h4>
                        <span style="font-size:0.7rem; background:${isPending ? 'rgba(139, 92, 246, 0.2)' : 'rgba(59, 130, 246, 0.2)'}; color:${isPending ? '#A78BFA' : '#60A5FA'}; padding:2px 8px; border-radius:4px; font-weight:600;">${isPending ? 'PENDING' : 'ACTIVE'}</span>
                    </div>
                     <p style="font-size:0.9rem; color:var(--text-main); margin:0 0 10px 0;">${t.description}</p>
                    <div style="display:flex; justify-content:flex-end; gap:8px;">
                        ${isPending ? `
                             <a href="${t.proof}" target="_blank" style="text-decoration:none; background:rgba(16,185,129,0.05); color:#94a3b8; font-size:0.8rem; padding:6px 12px; border-radius:6px; border:1px solid rgba(16,185,129,0.1);">👁️ View Proof</a>
                        ` : `
                            <button onclick="dropTask('${t.id}')" style="background:transparent; border:1px solid rgba(239, 68, 68, 0.3); color:#F87171; font-size:0.8rem; padding:6px 12px; border-radius:6px; cursor:pointer;">✕ Drop</button>
                            <button onclick="window.uploadProof('${t.quest_id || t.id}')" style="background:rgba(16, 185, 129, 0.2); border:1px solid #10B981; color:#10B981; font-size:0.8rem; padding:6px 12px; border-radius:6px; cursor:pointer;">📤 Upload Proof</button>
                        `}
                        <button onclick="window.location.hash='#mint-section'; document.getElementById('task-select').value='custom'; document.getElementById('custom-desc').value='${t.title}'; document.getElementById('hours').value='${t.standard_time || 0}'; updateTaskInfo();" 
                            style="background:#3B82F6; border:none; color:white; font-weight:600; font-size:0.8rem; padding:6px 16px; border-radius:6px; cursor:pointer; box-shadow:0 4px 6px rgba(59, 130, 246, 0.2);">✅ Mint Work</button>
                    </div>
                </div>
            `;
            }).join('') : '<div style="font-size:0.9rem; color:#64748b; text-align:center; padding:20px; border:1px dashed rgba(16,185,129,0.1); border-radius:8px;">No active tasks. Claim one above!</div>';
        }
    }

    // Add hidden file input for uploads
    if (!document.getElementById('proof-upload-input')) {
        const input = document.createElement('input');
        input.type = 'file';
        input.id = 'proof-upload-input';
        input.style.display = 'none';
        document.body.appendChild(input);

        input.addEventListener('change', function () {
            if (this.files.length > 0 && window.currentUploadQuestId) {
                const file = this.files[0];
                const formData = new FormData();
                formData.append('file', file);
                formData.append('quest_id', window.currentUploadQuestId);

                // Show uploading state
                logToTerminal(`[UPLOAD] Sending ${file.name}...`);

                fetch('/api/quest/upload-proof', {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + appState.token
                    },
                    body: formData
                })
                    .then(r => r.json())
                    .then(data => {
                        if (data.status === 'success') {
                            logToTerminal(`[UPLOAD] Success! Proof hash: ${data.hash.substring(0, 8)}`);
                            alert("Proof Uploaded Successfully! You earned " + data.reward + " AT.");
                            window.syncWithLedger();
                            window.renderJobBoard();
                        } else {
                            alert("Upload failed: " + data.message);
                        }
                    })
                    .catch(e => {
                        console.error(e);
                        alert("Upload error. Check console.");
                    });
            }
        });
    }

    window.uploadProof = function (questId) {
        // Open proof submission modal
        const proofDesc = prompt('Describe your completed work (proof of completion):');
        if (!proofDesc) return;

        apiFetch('/api/quests/submit', {
            method: 'POST',
            body: {
                quest_id: questId,
                proof: {
                    description: proofDesc,
                    submitted_at: Date.now()
                }
            }
        }).then(data => {
            if (data.status === 'submitted') {
                logToTerminal(`[QUEST] Proof submitted for quest ${questId.substring(0, 8)}`);
                alert('Proof submitted! Awaiting validation.');
                syncWithLedger();
                renderJobBoard();
            } else {
                alert('Submission failed: ' + (data.message || 'Unknown error'));
            }
        }).catch(e => {
            console.error('[QUEST] Proof submission error:', e);
        });
    };

    // --- MINTING LOGIC (Connected to Backend) ---
    var mintForm = document.getElementById('log-form');
    if (mintForm) {
        mintForm.addEventListener('submit', function (e) {
            e.preventDefault();

            var taskSelect = document.getElementById('task-select');
            var hoursInput = document.getElementById('hours');

            var payload = {
                task: taskSelect.value,
                hours: parseFloat(hoursInput.value),
                category: "LABOR",
                minter: appState.currentUser.name // Identity Integration
            };

            // Backend API Call
            apiFetch('/api/mint', {
                method: 'POST',
                body: payload
            }).then(data => {
                // Add unverified block to local state for instant feedback
                appState.history.unshift({
                    timestamp: Math.floor(Date.now() / 1000),
                    data: { ...payload, verified: false, queued: data.status === 'queued' },
                    hash: "pending_" + Math.random().toString(36).substring(7)
                });
                saveState();
                syncWithLedger();
                updateUI();

                // Show Success Animation
                var btn = mintForm.querySelector('button');
                var originalText = btn.innerText;

                if (data.status === 'queued') {
                    btn.innerText = "⏳ Queued (Offline)";
                    btn.style.background = "#F59E0B"; // Amber for queued
                } else {
                    btn.innerText = "✅ Minted!";
                    btn.style.background = "#10B981";
                }

                setTimeout(() => {
                    btn.innerText = originalText;
                    btn.style.background = "";
                }, 3000);
            }).catch(err => console.error("Mint Error:", err));
        });
    }

    // --- GAIA v1.0 BOOTLOADER ---
    window.APP_CONFIG = null;

    window.initGaia = function () {
        console.log("[GAIA] Booting v1.0 Kernel...");
        const configUrl = 'ui_config.json?v=' + Date.now();
        fetch(configUrl)
            .then(r => {
                if (!r.ok) throw new Error("HTTP " + r.status);
                return r.json();
            })
            .then(config => {
                window.APP_CONFIG = config;
                console.log(`[GAIA] Loaded Config: ${config.codename} v${config.version}`);
                // 1. Build Sidebar
                renderSidebar(config.modules);
            })
            .catch(e => {
                console.warn("[GAIA] Boot Error (using fallback menu):", e);
                renderSidebar(null); // Force fallback
            });
    };

    function renderSidebar(modules) {
        console.log("[UI] Rendering Sidebar with", modules ? modules.length : 0, "modules");
        var sidebarMenu = document.querySelector('.sidebar-menu');
        if (!sidebarMenu) {
            console.error("[GAIA] Sidebar menu element not found!");
            return;
        }

        sidebarMenu.innerHTML = ''; // Clear static items

        // Fallback if no modules or empty
        if (!modules || modules.length === 0) {
            console.warn("[GAIA] No modules in config, using fallback menu");
            modules = [
                { id: 'dashboard', name: 'Mission Control', icon: '🚀', enabled: true, order: 1 },
                { id: 'jobs', name: 'Job Board', icon: '📋', enabled: true, order: 2 },
                { id: 'bounties', name: 'Bounty Board', icon: '⚔️', enabled: true, order: 2.5 },
                { id: 'wallet', name: 'Sovereign Wallet', icon: '💰', enabled: true, order: 3 },
                { id: 'techtree', name: 'Tech Tree', icon: '🧬', enabled: true, order: 4 },
                { id: 'map', name: 'Mesh Map', icon: '🗺️', enabled: true, order: 7 },
                { id: 'tangle', name: 'Live Tangle', icon: '🕸️', enabled: true, order: 8 },
                { id: 'steward', name: 'Steward AI', icon: '🧠', enabled: true, order: 8.5 }
            ];
        }

        // Sort by order
        modules.sort((a, b) => (a.order || 99) - (b.order || 99));

        var addedCount = 0;
        modules.forEach(mod => {
            if (!mod.enabled) return;
            // Admin check - but don't block if appState isn't ready
            if (mod.role_required === 'ADMIN') {
                if (!window.appState || !window.appState.currentUser || window.appState.currentUser.role !== 'ADMIN') return;
            }

            var btn = document.createElement('button');
            btn.className = 'nav-item';
            btn.id = `btn-${mod.id}`;
            btn.onclick = () => {
                window.switchView(mod.id);
            };
            btn.innerHTML = `<span style="font-size:16px;">${mod.icon}</span> ${mod.name}`;

            sidebarMenu.appendChild(btn);
            addedCount++;
        });

        console.log(`[GAIA] Sidebar rendered with ${addedCount} modules`);

        // If nothing was added, show a fallback message
        if (addedCount === 0) {
            sidebarMenu.innerHTML = '<div style="color:#64748b; padding:15px; font-size:0.8rem;">⚠️ No modules available. Check ui_config.json</div>';
        }
    }

    // --- BOUNTY BOARD (CO-OP) ---
    // Moved to bounty_board.js for modularity.
    // Logic is now handled by window.initBountyBoard() and its associated functions.


    // --- TRAFFIC SIMULATION ---
    window.simulateTraffic = function () {
        var actions = ['MINT', 'TX'];
        var action = actions[Math.floor(Math.random() * actions.length)];

        if (action === 'MINT') {
            window.apiFetch('/api/mint', {
                method: 'POST',
                body: {
                    minter: "Sim_Worker_" + Math.floor(Math.random() * 100),
                    task: "Automated Maintenance",
                    hours: 1,
                    timestamp: Date.now()
                }
            });
        } else {
            window.apiFetch('/api/transfer', {
                method: 'POST',
                body: {
                    sender: "Sim_Wallet_A",
                    receiver: "Sim_Wallet_B",
                    amount: Math.floor(Math.random() * 50),
                    timestamp: Date.now()
                }
            });
        }
    };

    // Expose for console use or button
    window.startSimulation = function (interval = 3000) {
        logToTerminal("[SIM] Traffic Simulation STARTED");
        window.simInterval = setInterval(window.simulateTraffic, interval);
    };

    window.stopSimulation = function () {
        if (window.simInterval) clearInterval(window.simInterval);
        logToTerminal("[SIM] Traffic Simulation STOPPED");
    };

    // --- UI Control for Simulation ---
    window.toggleSimulationUI = function () {
        var toggle = document.getElementById('sim-toggle');
        var badges = document.getElementById('sim-status-badge');

        if (toggle.checked) {
            window.startSimulation(2000); // 2s default
            badges.innerText = "ACTIVE";
            badges.style.color = "#10B981";
            badges.style.background = "rgba(16, 185, 129, 0.2)";
            badges.style.boxShadow = "0 0 10px rgba(16, 185, 129, 0.2)";
        } else {
            window.stopSimulation();
            badges.innerText = "STANDBY";
            badges.style.color = "#94a3b8";
            badges.style.background = "rgba(16,185,129,0.1)";
            badges.style.boxShadow = "none";
        }
    }

    // --- UPDATED UI ELEMENTS FOR CIV OS ---
    var sidebarName = document.getElementById('sidebar-username');
    var sidebarBalance = document.getElementById('sidebar-balance');
    var xpFillSidebar = document.getElementById('xp-fill-sidebar');
    var terminalLog = document.getElementById('terminal-log');

    // --- CHAT SYSTEM (Town Square) ---
    window.switchChannel = function (channel) {
        appState.currentChannel = channel;
        const chatTitle = document.querySelector('#view-dashboard h3');
        if (chatTitle) {
            const icons = { 'general': '🌍', 'squad_alpha': '🛡️', 'squad_beta': '🛠️', 'intel': '🛰️' };
            const names = { 'general': 'Town Square', 'squad_alpha': 'Squad Alpha', 'squad_beta': 'Squad Beta', 'intel': 'Intel Swarm' };
            chatTitle.innerText = `${icons[channel] || '💬'} ${names[channel] || channel}`;
        }
        logToTerminal(`[SYSTEM] Switched to channel: ${channel}`);
        // Clear terminal log and potentially fetch history if we had that logic separated
        const logBox = document.getElementById('terminal-log');
        if (logBox) logBox.innerHTML = `<div style="color:var(--text-muted); font-size:0.7rem;">Synchronizing ${channel}...</div>`;
    };

    window.sendChat = function () {
        var input = document.getElementById('chat-input');
        if (!input || !input.value.trim()) return;
        var msg = input.value.trim();

        apiFetch('/api/messages', {
            method: 'POST',
            body: {
                sender: appState.currentUser.name,
                content: msg,
                channel: appState.currentChannel || 'general'
            }
        }).then(data => {
            if (data.status === 'success') {
                logToTerminal(`[${appState.currentChannel.toUpperCase()}] ${appState.currentUser.name}: ${msg}`);
                input.value = '';
                if (window.renderActivityFeed) window.renderActivityFeed();
            }
        }).catch(e => {
            console.error("[CHAT] Failed to send message:", e);
            logToTerminal("⚠️ Chat service unreachable.");
        });
    };

    window.quickMint = function (hours) {
        if (!confirm(`Mint ${hours * 10} AT for ${hours}h of labor?`)) return;
        apiFetch('/api/mint', {
            method: 'POST',
            body: {
                task: "Quick Mint",
                hours: hours,
                category: "LABOR",
                minter: appState.currentUser.name
            }
        }).then(data => {
            if (data.status === 'success' || data.status === 'queued') {
                logToTerminal(`[MINT] +${hours * 10} AT pending verification.`);
                syncWithLedger();
            } else {
                alert(data.message);
            }
        }).catch(e => {
            console.error("[MINT] Quick Mint Failed:", e);
        });
    };

    window.renderMetabolicDashboard = function (sensorData) {
        const container = document.getElementById('active-missions-list');
        if (!container || !sensorData) return;

        // If we have sensor data, prepend the Metabolic Health view
        let html = `
            <div class="glass-panel" style="margin-bottom:20px; border:1px solid rgba(16,185,129,0.2); background:rgba(16,185,129,0.02); padding:15px;">
                <h4 style="color:#10B981; margin-top:0; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px;">🛰️ Infrastructure Health</h4>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap:10px; margin-top:10px;">
        `;

        Object.entries(sensorData).forEach(([id, s]) => {
            const isOnline = (Date.now() / 1000 - s.last_seen) < 60;
            const color = isOnline ? '#10B981' : '#EF4444';
            html += `
                <div style="text-align:center; padding:8px; background:rgba(0,0,0,0.2); border-radius:8px; border:1px solid ${color}20;">
                    <div style="font-size:0.6rem; color:#94a3b8; margin-bottom:4px;">${id}</div>
                    <div style="font-size:0.9rem; font-weight:bold; color:${color};">${isOnline ? s.last_value : 'OFFLINE'}</div>
                    <div style="width:4px; height:4px; background:${color}; border-radius:50%; margin:4px auto 0; ${isOnline ? 'box-shadow:0 0 5px #10B981; animation: pulse 2s infinite;' : ''}"></div>
                </div>
            `;
        });

        html += `</div></div>`;

        // This prepends to the existing missions list for now
        const missionHtml = Array.isArray(rawState.activeMissions) ? rawState.activeMissions.map(m => `
            <div style="padding:10px; background:rgba(16,185,129,0.05); border-radius:8px; margin-bottom:8px; border-left:3px solid var(--primary);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="color:var(--primary-light); font-size:0.85rem;">${m.title}</strong>
                    <span class="badge" style="font-size:0.6rem;">${m.phase || 'ALPHA'}</span>
                </div>
                <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">${m.description}</div>
            </div>
        `).join('') : '';

        container.innerHTML = html + (missionHtml || '<div style="color:var(--text-muted); font-size:0.8rem; padding:10px; text-align:center;">No active missions.</div>');
    };

    window.updateDashboardStats = function () {
        fetch('/api/evolution')
            .then(r => r.json())
            .then(data => {
                // Core Stats
                const blockCount = document.getElementById('dash-block-count');
                if (blockCount) blockCount.innerText = data.evolution_cycles || 0;

                const mintCount = document.getElementById('dash-mint-count');
                if (mintCount) mintCount.innerText = data.total_mints || 0;

                // Metabolic Yield (Green Protocol)
                const yieldEl = document.getElementById('metabolic-yield-value');
                if (yieldEl) {
                    const yieldVal = ((data.metabolic_yield || 0.85) * 100).toFixed(1) + '%';
                    yieldEl.innerText = yieldVal;
                    const fill = document.getElementById('metabolic-yield-fill');
                    if (fill) fill.style.width = yieldVal;
                }

                // Render Metabolic/Infrastructure Dashboard
                if (data.sensors) {
                    rawState.activeMissions = data.active_missions;
                    window.renderMetabolicDashboard(data.sensors);
                }

                // Lively Traffic
                if (window.renderTrafficGraph) {
                    window.renderTrafficGraph(rawState.ledger.slice(-20)); // Ensure some baseline activity
                }

                logToTerminal(`[SYSTEM] Telemetry Synced. Evolutionary Cycle: ${data.evolution_cycles}`);
            }).catch(e => {
                console.warn("[SYSTEM] Telemetry Fetch Failed:", e);
                logToTerminal("⚠️ System telemetry unavailable.");
            });
    };

    // --- TECH TREE DATA ---
    var TECH_TREE = [
        { id: 'fire', name: 'Prometheus Fire', description: 'Thermal Security & Cooking', cost: 0, icon: '🔥', parents: [] },
        { id: 'ag', name: 'Regenerative Ag', description: 'Soil Health & Food Sovereignty', cost: 100, icon: '🌾', parents: ['fire'] },
        { id: 'power', name: 'Micro-Grid', description: 'Solar, Wind & Battery Ops', cost: 500, icon: '⚡', parents: ['ag'] },
        { id: 'ceb', name: 'CEB Press', description: 'Compressed Earth Block Machine', cost: 1200, icon: '🧱', parents: ['power'] },
        { id: 'seed_home', name: 'Seed Eco-Home', description: 'Modular Bio-Shelter System', cost: 2500, icon: '🏠', parents: ['ceb'] },
        { id: 'power_cube', name: 'Power Cube', description: 'Hydraulic/Solar Energy Unit', cost: 4000, icon: '🟦', parents: ['seed_home'] },
        { id: 'aquaponics', name: 'Metabolic Aquaponics', description: 'Closed-Loop Food Factory', cost: 6000, icon: '🐟', parents: ['power_cube'] },
        { id: 'dunbar_baseline', name: 'Dunbar Baseline', description: '50-Person Resource Stability', cost: 10000, icon: '🏘️', parents: ['aquaponics'] },
        { id: 'fab', name: 'Extreme Manufacturing', description: 'CNC & Iron-Backed Production', cost: 15000, icon: '🛠️', parents: ['dunbar_baseline'] },
        { id: 'ai', name: 'Village Spirit', description: 'Autonomous Governance Oracle', cost: 30000, icon: '🤖', parents: ['fab'] }
    ];

    // --- MAP SYSTEM ---
    window.mapInstance = null;
    window.initMap = function () {
        if (window.mapInstance) {
            setTimeout(() => window.mapInstance.invalidateSize(), 100);
            return;
        }
        if (!document.getElementById('village-map')) return;

        // OSE Campus (Maysville/Cameron MO Area)
        var coords = [39.914, -94.525];

        window.mapInstance = L.map('village-map').setView(coords, 10);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(window.mapInstance);

        // OSE HQ
        L.marker(coords).addTo(window.mapInstance)
            .bindPopup('<b>Factor e Farm (OSE HQ)</b><br>The Seed Eco-Home')
            .openPopup();

        // Fetch Federated Villages from dynamic API
        fetch('/api/federation/villages')
            .then(r => r.json())
            .then(data => {
                data.villages.forEach(v => {
                    if (v.village_id === 'ose-missouri-001') return;
                    L.circleMarker([v.lat, v.lng], {
                        color: '#3B82F6',
                        fillColor: '#3B82F6',
                        fillOpacity: 0.8,
                        radius: 10,
                        weight: 2,
                        className: 'map-marker-pulse'
                    }).addTo(window.mapInstance)
                        .bindPopup(`
                            <div style="background:#0f172a; color:white; padding:15px; border-radius:12px; border:1px solid #3B82F6; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);">
                                <strong style="color:#60A5FA; font-size:1.1rem;">${v.name}</strong><br>
                                <div style="margin-top:5px; padding-top:5px; border-top:1px solid rgba(255,255,255,0.1);">
                                    <span style="font-size:11px; color:#94a3b8;">Status: <span style="color:#10B981;">Online Federation</span></span><br>
                                    <span style="font-size:11px; color:#94a3b8;">Yield: <span style="color:#FBBF24;">88% Metabolic</span></span><br>
                                </div>
                                <button onclick="window.location.hash='#mobility'" style="margin-top:12px; background:#3B82F6; border:none; color:white; font-size:11px; padding:8px 12px; border-radius:6px; width:100%; cursor:pointer; font-weight:600;">Warp to Node</button>
                            </div>
                        `, { className: 'custom-popup-premium', closeButton: false });
                });
            }).catch(e => {
                console.warn("[MAP] Could not load federated villages:", e);
                logToTerminal("⚠️ Federated map nodes unavailable.");
            });

        // Dummy Nodes (Community)
        var dummyNodes = [
            { lat: 39.75, lng: -94.60, name: "St. Jo Logistics Hub" },
            { lat: 39.10, lng: -94.58, name: "KC Innovation Lab" },
            { lat: 40.00, lng: -94.40, name: "Wind Sentinel (North)" },
            { lat: 39.85, lng: -94.65, name: "Solar Array (West)" }
        ];

        dummyNodes.forEach(n => {
            L.circleMarker([n.lat, n.lng], {
                color: '#10B981',
                fillColor: '#10B981',
                fillOpacity: 0.5,
                radius: 6
            }).addTo(window.mapInstance).bindPopup(`<b>${n.name}</b><br>Active Node`);
        });

        // Initial Resize to fix gray box issue
        setTimeout(() => window.mapInstance.invalidateSize(), 500);
    };

    // --- RENDER FUNCTIONS ---
    function renderTechTree(currentXP) {
        var container = document.getElementById('tech-tree-container');
        if (!container) return;

        container.innerHTML = TECH_TREE.map(node => {
            // GUEST UNLOCK: Everyone can view everything.
            var isUnlocked = true; // currentXP >= node.cost; 
            var actualUnlocked = currentXP >= node.cost; // Use this for styling distinction only

            // Check parents
            var parentsUnlocked = node.parents.every(pid => {
                var p = TECH_TREE.find(n => n.id === pid);
                return currentXP >= p.cost;
            });

            // Styling: Even if "viewable", let's show if they actually "own" it text-wise, but keep it bright
            var statusIcon = actualUnlocked ? '✅' : '🔭'; // Telescope for preview
            var border = actualUnlocked ? '2px solid #10B981' : '1px dashed #334155';
            var opacity = '1'; // Always visible

            return `
                <div style="background: rgba(30, 41, 59, 0.8); border: ${border}; padding: 15px; border-radius: 12px; opacity: ${opacity}; display: flex; flex-direction: column; text-align: center;">
                    <div style="font-size: 32px; margin-bottom: 10px;">${node.icon}</div>
                    <h3 style="margin: 0; font-size: 1rem; color: #f1f5f9;">${node.name}</h3>
                    <p style="margin: 5px 0 10px 0; font-size: 0.8rem; color: #94a3b8;">${node.description}</p>
                    <div style="margin-top: auto; font-size: 0.75rem; font-weight: bold; color: ${actualUnlocked ? '#10B981' : '#FBBF24'};">
                        ${statusIcon} Cost: ${node.cost} XP
                    </div>
                </div>
            `;
        }).join('');
    }

    // --- RENDER KNOWLEDGE (Wiki) ---
    function renderKnowledge() {
        var container = document.getElementById('wiki-content');
        if (!container) return;

        // Fetch Master Index
        fetch('../../library/Master_SOP_Index.md')
            .then(r => r.text())
            .then(md => {
                if (window.marked) {
                    container.innerHTML = marked.parse(md);
                } else {
                    container.innerHTML = "<pre>" + md + "</pre>";
                }
            })
            .catch(e => {
                console.error("Wiki Load Error:", e);
                container.innerHTML = `<div style="color:red; padding:20px;">Failed to load Knowledge Base.</div>`;
            });
    }

    window.renderWikiUI = function () {
        var container = document.getElementById('wiki-container');

        // Build categorized sidebar
        const sidebarHTML = window.wikiCategories.map(cat => `
            <div class="wiki-category" style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid rgba(16,185,129,0.1); margin-bottom: 8px;">
                    <span style="font-size: 16px;">${cat.icon}</span>
                    <span style="font-size: 0.85rem; font-weight: 600; color: ${cat.color}; text-transform: uppercase; letter-spacing: 1px;">${cat.name}</span>
                </div>
                ${cat.pages.map(p => `
                    <div class="wiki-link" onclick="loadWikiPage('${p.path}')" 
                        style="padding: 10px 12px; cursor: pointer; background: rgba(16,185,129,0.02); 
                               border-radius: 8px; margin-bottom: 6px; transition: all 0.2s ease;
                               border: 1px solid transparent;">
                        <div style="color: var(--text-main); font-size: 0.9rem; font-weight: 500;">${p.label}</div>
                        <div style="color: #64748b; font-size: 0.75rem; margin-top: 2px;">${p.desc}</div>
                    </div>
                `).join('')}
            </div>
        `).join('');

        // Premium Split View Layout
        container.innerHTML = `
            <style>
                .wiki-link:hover {
                    background: rgba(16, 185, 129, 0.1) !important;
                    border-color: rgba(16, 185, 129, 0.3) !important;
                    transform: translateX(4px);
                }
                .wiki-content-area h1, .wiki-content-area h2, .wiki-content-area h3 {
                    color: var(--primary-light);
                    border-bottom: 1px solid rgba(16,185,129,0.1);
                    padding-bottom: 8px;
                    margin-top: 24px;
                }
                .wiki-content-area h1 { font-size: 1.8rem; color: #10B981; }
                .wiki-content-area h2 { font-size: 1.4rem; }
                .wiki-content-area h3 { font-size: 1.1rem; color: #94a3b8; }
                .wiki-content-area ul { padding-left: 20px; }
                .wiki-content-area li { margin-bottom: 8px; }
                .wiki-content-area code {
                    background: rgba(0,0,0,0.4);
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.85em;
                    color: #10B981;
                }
                .wiki-content-area pre {
                    background: rgba(0,0,0,0.5);
                    padding: 16px;
                    border-radius: 8px;
                    overflow-x: auto;
                    border: 1px solid rgba(16,185,129,0.1);
                }
                .wiki-content-area a {
                    color: #3B82F6;
                    text-decoration: none;
                }
                .wiki-content-area a:hover {
                    text-decoration: underline;
                }
                .wiki-content-area blockquote {
                    border-left: 3px solid #10B981;
                    padding-left: 16px;
                    margin: 16px 0;
                    color: #94a3b8;
                    font-style: italic;
                }
            </style>
            <div style="display: flex; height: calc(100% - 20px); gap: 20px;">
                <!-- Sidebar -->
                <div style="width: 280px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px;">
                    <div style="position: relative;">
                        <input type="text" id="wiki-search" placeholder="Search protocols..." 
                            style="background: rgba(0,0,0,0.4); border: 1px solid rgba(16,185,129,0.1); 
                                   padding: 12px 12px 12px 40px; border-radius: 10px; color: white; width: 100%;
                                   font-size: 0.9rem; transition: all 0.2s;"
                            onkeyup="filterWiki(this.value)"
                            onfocus="this.style.borderColor='rgba(16,185,129,0.5)'; this.style.boxShadow='0 0 0 2px rgba(16,185,129,0.2)';"
                            onblur="this.style.borderColor='rgba(16,185,129,0.1)'; this.style.boxShadow='none';">
                        <span style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #64748b;">🔍</span>
                    </div>
                    <div id="wiki-list" style="flex: 1; overflow-y: auto; padding: 4px;">
                        ${sidebarHTML}
                    </div>
                </div>
                <!-- Content -->
                <div id="wiki-content" class="wiki-content-area" 
                     style="flex: 1; background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.8)); 
                            border-radius: 16px; padding: 30px; overflow-y: auto; 
                            border: 1px solid rgba(16,185,129,0.1); 
                            font-family: 'Inter', sans-serif; line-height: 1.7; color: var(--text-main);
                            box-shadow: inset 0 0 60px rgba(0,0,0,0.3);">
                    <div style="text-align: center; padding-top: 80px;">
                        <div style="font-size: 48px; margin-bottom: 16px;">📚</div>
                        <h3 style="color: var(--primary-light); margin: 0 0 8px 0; font-size: 1.4rem;">Village Library</h3>
                        <p style="color: #64748b; margin: 0; max-width: 300px; margin: 0 auto;">Select a protocol from the sidebar to access the collective intelligence of the Village.</p>
                    </div>
                </div>
            </div>
        `;
    }

    // --- RENDER CHRONICLE ---
    window.renderChronicle = function () {
        const container = document.getElementById('chronicle-timeline');
        if (!container) return;

        const chronologicalBlocks = (rawState.ledger || []).filter(b =>
            ['CHRONICLE', 'QUEST', 'MISSION', 'TECH_UNLOCK'].includes(b.type)
        ).sort((a, b) => b.timestamp - a.timestamp);

        if (chronologicalBlocks.length === 0) {
            container.innerHTML = `<div style="text-align:center; padding:50px; color:var(--text-muted);">The threads of time are silent. No chronicle entries found.</div>`;
            return;
        }

        container.innerHTML = chronologicalBlocks.map((b, idx) => {
            const date = new Date(b.timestamp * 1000).toLocaleString();
            let icon = '📜';
            let color = '#94a3b8';
            let title = 'System Update';
            let msg = b.data.message || 'Ledger event recorded.';

            if (b.type === 'QUEST') { title = 'New Directive'; icon = '🎯'; color = '#3B82F6'; msg = b.data.title; }
            if (b.type === 'MISSION') { title = 'Cosmic Mission'; icon = '🚀'; color = '#10B981'; msg = b.data.title; }
            if (b.data.event === 'TECH_DEBT_ALERT') { icon = '🛡️'; color = '#F59E0B'; title = 'System Audit'; }
            if (b.data.event === 'METABOLIC_FAULT') { icon = '⚠️'; color = '#EF4444'; title = 'Metabolic Fault'; }

            return `
                    <div class="chronicle-entry" style="display:flex; gap:20px; position:relative; animation: slideIn 0.3s ease-out forwards; animation-delay: ${idx * 0.05}s;">
                        <div class="chronicle-dot" style="width:20px; height:20px; border-radius:50%; background:${color}; box-shadow:0 0 10px ${color}; z-index:2; margin-top:5px;"></div>
                        <div class="glass-panel" style="flex:1; padding:15px; border-left:4px solid ${color};">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <span style="font-weight:700; color:${color}; letter-spacing:1px; font-size:0.7rem; text-transform:uppercase;">${icon} ${title}</span>
                                <span style="font-size:0.7rem; color:var(--text-muted); font-family:'JetBrains Mono';">${date}</span>
                            </div>
                            <div style="font-size:0.9rem; color:white; line-height:1.4;">${msg}</div>
                            <div style="font-size:0.6rem; color:var(--text-muted); margin-top:8px; font-family:'JetBrains Mono';">HASH: ${b.hash.substring(0, 16)}...</div>
                        </div>
                    </div>
                    `;
        }).join('');
    };


    // --- WIKI: Load Page Content ---
    window.loadWikiPage = function (path) {
        const contentEl = document.getElementById('wiki-content');
        if (!contentEl) return;

        contentEl.innerHTML = `
            <div style="text-align: center; padding-top: 80px;">
                <div style="font-size: 32px; animation: pulse 1s infinite;">⏳</div>
                <p style="color: #64748b; margin-top: 12px;">Loading Protocol...</p>
            </div>
        `;

        let finalPath = path;
        if (!finalPath.startsWith('library') && !finalPath.startsWith('http')) {
            finalPath = 'library/' + finalPath;
        }

        fetch(finalPath)
            .then(r => {
                if (!r.ok) throw new Error('Protocol not found');
                return r.text();
            })
            .then(md => {
                if (window.marked) {
                    contentEl.innerHTML = marked.parse(md);
                } else {
                    contentEl.innerHTML = `<pre style="white-space:pre-wrap; color: var(--text-main);">${md}</pre>`;
                }
            })
            .catch(e => {
                contentEl.innerHTML = `
                    <div style="text-align: center; padding-top: 80px;">
                        <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
                        <h3 style="color: #EF4444; margin: 0 0 8px 0;">Protocol Unavailable</h3>
                        <p style="color: #64748b; margin: 0;">${e.message}</p>
                    </div>
                `;
            });
    };

    // --- WIKI: Filter/Search ---
    window.filterWiki = function (query) {
        if (!window.wikiPages) return;
        const q = query.toLowerCase();
        const list = document.getElementById('wiki-list');

        if (!q) {
            // Reset to full categorized view
            window.renderWikiUI();
            return;
        }

        // Filter and show flat results
        const filtered = window.wikiPages.filter(p =>
            p.label.toLowerCase().includes(q) ||
            (p.desc && p.desc.toLowerCase().includes(q))
        );

        list.innerHTML = filtered.length ? filtered.map(p => `
            <div class="wiki-link" onclick="loadWikiPage('${p.path}')" 
                style="padding: 10px 12px; cursor: pointer; background: rgba(16,185,129,0.02); 
                       border-radius: 8px; margin-bottom: 6px; transition: all 0.2s ease;
                       border: 1px solid transparent;">
                <div style="color: var(--text-main); font-size: 0.9rem; font-weight: 500;">${p.label}</div>
                <div style="color: #64748b; font-size: 0.75rem; margin-top: 2px;">${p.desc || ''}</div>
            </div>
        `).join('') : '<div style="text-align: center; padding: 20px; color: #64748b;">No protocols found.</div>';
    };

    // --- RENDER LEADERBOARD ---
    function renderLeaderboard() {
        var container = document.getElementById('leaderboard-container');
        if (!container) return;

        // Dummy Data + Current User
        var leaders = [
            { name: "Seeker", xp: 15400, mints: 42, role: "Architect" },
            { name: "Marcin", xp: 12100, mints: 38, role: "Founder" },
            { name: "Gaddafi_Ghost", xp: 8900, mints: 12, role: "Legend" },
            { name: appState.currentUser.name, xp: appState.xp, mints: 0, role: "Guest" }
        ].sort((a, b) => b.xp - a.xp);

        container.innerHTML = `
            <div style="margin-bottom:15px; display:flex; gap:10px;">
                <button class="btn-xs" style="background:#3B82F6; color:white; border:none; padding:4px 8px; border-radius:4px;">Top XP</button>
                <button class="btn-xs" style="background:rgba(16,185,129,0.1); color:#94a3b8; border:none; padding:4px 8px; border-radius:4px;">Most Mints</button>
                <button class="btn-xs" style="background:rgba(16,185,129,0.1); color:#94a3b8; border:none; padding:4px 8px; border-radius:4px;">Verification Score</button>
            </div>
            <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                <tr style="text-align:left; color:#94a3b8;">
                    <th style="padding:10px;">Rank</th>
                    <th>User</th>
                    <th>Role</th>
                    <th>XP</th>
                    <th>Mints</th>
                </tr>
                ${leaders.map((l, i) => `
                    <tr style="border-bottom:1px solid rgba(16,185,129,0.05);">
                        <td style="padding:10px; color:${i === 0 ? '#FBBF24' : 'var(--text-main)'}; font-weight:${i === 0 ? 'bold' : 'normal'}">#${i + 1}</td>
                        <td style="color:#eff6ff;">${l.name} ${l.name === appState.currentUser.name ? '(You)' : ''}</td>
                        <td><span style="background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:4px; font-size:0.75rem;">${l.role}</span></td>
                        <td style="font-family:'JetBrains Mono'; color:#10B981;">${l.xp.toLocaleString()}</td>
                        <td style="font-family:'JetBrains Mono';">${l.mints}</td>
                    </tr>
                `).join('')}
            </table>
        `;
    }

    // --- VERIFY WORK ---
    function verifyWork() {
        var container = document.getElementById('verify-container');
        if (!container) return;

        // Guest Access UNLOCKED (Simulation)
        /* 
        if (appState.currentUser.role !== 'ORACLE') {
            container.innerHTML = '<div style="text-align:center; padding:40px; color:var(--text-main);">🔒 Only Validators (Oracles) can access this terminal.</div>';
            return;
        }
        */

        // Mock Pending Verifications
        var pending = [
            { id: 'v1', user: 'Apprentice_01', task: 'Wired SEH7 Kitchen', proof: 'image_log_404.jpg', time: '10m ago' },
            { id: 'v2', user: 'Plumber_Joe', task: 'Installed Shower Valve', proof: 'vid_proof_22.mp4', time: '1h ago' }
        ];

        container.innerHTML = `
            <div style="background:rgba(245, 158, 11, 0.1); border:1px solid #FBBF24; padding:15px; border-radius:8px; margin-bottom:20px;">
                <h4 style="margin:0 0 5px 0; color:#FBBF24;">⚠️ Guest Mode: Simulation</h4>
                <p style="margin:0; font-size:0.8rem; color:#FDE68A;">You can view and verify tasks, but your validations will be recorded as "Shadow Verifications" (Non-Consensus) until you achieve Level 5.</p>
            </div>
            
            ${pending.length === 0 ? '<div style="text-align:center;">No pending verifications.</div>' : pending.map(p => `
                <div style="background:rgba(16,185,129,0.05); padding:15px; border-radius:12px; margin-bottom:15px; border-left:4px solid #F59E0B;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <strong>${p.task}</strong>
                        <span style="font-size:0.75rem; color:#94a3b8;${p.time}</span>
                    </div>
                    <div style="font-size:0.9rem; margin-bottom:10px;">
                        👤 <strong>${p.user}</strong> submitted proof: <a href="#" style="color:#3B82F6;">${p.proof}</a>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button onclick="alert('Shadow Verified! +5 XP')" style="flex:1; background:#10B981; border:none; padding:8px; border-radius:6px; font-weight:bold; cursor:pointer;">✅ Valid</button>
                        <button onclick="alert('Marked Need Info')" style="flex:1; background:rgba(16,185,129,0.1); border:none; color:white; padding:8px; border-radius:6px; cursor:pointer;">❓ Question</button>
                        <button onclick="alert('Reported!')" style="flex:1; background:rgba(239, 68, 68, 0.2); border:none; color:#EF4444; padding:8px; border-radius:6px; cursor:pointer;">❌ Invalid</button>
                    </div>
                </div>
            `).join('')}
        `;
    }

    // --- LEDGER SYNC (Incremental & Consolidated) ---
    function syncWithLedger() {
        apiFetch(`/api/graph?since=${rawState.lastId || 0}`)
            .then(newBlocks => {
                if (!Array.isArray(newBlocks) || newBlocks.length === 0) return;

                newBlocks.forEach(b => {
                    rawState.ledger.push(b);
                    if (b.id > (rawState.lastId || 0)) rawState.lastId = b.id;

                    const btype = b.type;
                    const bdata = b.data;

                    // Quest Idempotency
                    if (btype === 'QUEST' && !appState.tasks.find(t => t.quest_id === bdata.quest_id)) {
                        appState.tasks.push(bdata);
                    }

                    // Party & Proof Sync
                    let targetQuest = appState.tasks.find(t => t.quest_id === bdata.quest_id);
                    if (targetQuest) {
                        if (btype === 'PARTY_JOIN') {
                            if (!targetQuest.party) targetQuest.party = [];
                            if (!targetQuest.party.includes(bdata.username)) {
                                targetQuest.party.push(bdata.username);
                                targetQuest.status = 'ASSIGNED';
                            }
                        }
                        if (btype === 'PARTY_LEAVE' && targetQuest.party) {
                            targetQuest.party = targetQuest.party.filter(u => u !== bdata.username);
                            if (targetQuest.party.length === 0) targetQuest.status = 'OPEN';
                        }
                        if (btype === 'PROOF') {
                            targetQuest.proof = bdata.proof_url;
                            if (targetQuest.status === 'ASSIGNED') targetQuest.status = 'PENDING_VERIFICATION';
                        }
                    }

                    if (btype === 'MESSAGE') {
                        logToTerminal(`[CHAT] ${bdata.sender}: ${bdata.content}`);
                        if (window.logActivity) window.logActivity('MESSAGE', bdata.sender, bdata);
                    }
                    if (btype === 'MINT' || btype === 'LABOR') {
                        logToTerminal(`[MINT] ${bdata.minter} generated ${bdata.hours}h (${bdata.at_reward} AT)`);
                        if (window.logActivity) window.logActivity('MINT', bdata.minter, bdata);
                    }
                    if (btype === 'TRADE' || btype === 'TX') {
                        logToTerminal(`[TRADE] ${bdata.sender} -> ${bdata.receiver} : ${bdata.amount} AT`);
                        if (window.logActivity) window.logActivity('PURCHASE', bdata.sender, { item: 'Transfer', at: bdata.amount });
                    }
                });

                // Trigger Tangle Update
                if (window.renderTrafficGraph) {
                    window.renderTrafficGraph(newBlocks);
                    // Heartbeat Pulse Trigger
                    window.trafficNodes.forEach(node => {
                        if (newBlocks.find(b => b.hash === node.id)) {
                            node.pulse = 1.0;
                        }
                    });
                }
                if (window.renderTangle) renderTangle();

                // Global Stat Recalculation
                let balance = 0;
                let userXP = 0;
                let userXPs = {};
                const username = rawState.currentUser.name;

                rawState.ledger.forEach(block => {
                    const btype = block.type;
                    const bdata = block.data;
                    const minter = bdata.minter || bdata.username || bdata.sender || 'System';

                    if (!userXPs[minter]) userXPs[minter] = 0;

                    if (['MINT', 'LABOR', 'QUEST_COMPLETION', 'HARDWARE_PROOF', 'PROOF'].includes(btype)) {
                        const amt = parseFloat(bdata.at_reward || (bdata.hours || 0) * 10 || 0);
                        if (minter === username) {
                            balance += amt;
                            userXP += 10;
                        }
                        userXPs[minter] += 10;
                    }
                    if (['TRADE', 'TX'].includes(btype)) {
                        const amt = parseFloat(bdata.amount || 0);
                        if (bdata.sender === username) balance -= amt;
                        if (bdata.receiver === username) balance += amt;
                    }
                });

                appState.balance = balance;
                appState.xp = userXP;

                // Update Leaderboard & UI
                if (window.renderLeaderboard) {
                    let leaderboard = Object.keys(userXPs).map(k => ({ name: k, xp: userXPs[k] }));
                    renderLeaderboard(leaderboard);
                }

                if (window.renderTangle) renderTangle();
                updateUI();
            }).catch(e => console.error("[GAIA] Sync Error:", e));
    }

    // --- TRAFFIC VISUALIZER (Bouncing Box Mode) ---
    window.trafficNodes = [];
    window.trafficLinks = [];

    // Custom "Bouncing Box" Physics Engine
    // "See ALL of the nodes, in a box"

    window.renderTrafficGraph = function (blocks) {
        if (!Array.isArray(blocks)) {
            console.warn("[DEBUG] renderTrafficGraph: blocks is not an array", blocks);
            return;
        }
        const canvas = document.getElementById('traffic-canvas');
        const largeCanvas = document.getElementById('tangle-canvas-large');

        // Helper to update specific canvas with proper dimensions
        function updateCanvas(canv) {
            if (!canv) return;
            const rect = canv.getBoundingClientRect();
            // Ensure internal resolution matches display size (or default/fallback)
            const w = Math.max(rect.width, canv.offsetWidth, 500);
            const h = Math.max(rect.height, canv.offsetHeight, 400);
            if (canv.width !== w) canv.width = w;
            if (canv.height !== h) canv.height = h;
        }

        updateCanvas(canvas);
        updateCanvas(largeCanvas);

        const primaryCanvas = largeCanvas || canvas;
        if (!primaryCanvas) return;

        const width = primaryCanvas.width;
        const height = primaryCanvas.height;
        console.log("[DEBUG] renderTrafficGraph processing " + blocks.length + " blocks. Canvas size: " + width + "x" + height);

        // Process ALL blocks -- NO SLICE LIMIT
        blocks.forEach((b) => {
            if (!window.trafficNodes.find(n => n.id === b.hash)) {
                // Spawn new nodes randomly within the box
                window.trafficNodes.push({
                    id: b.hash,
                    // Spawn safely away from edges
                    x: Math.random() * (width - 100) + 50,
                    y: Math.random() * (height - 100) + 50,
                    vx: (Math.random() - 0.5) * 4, // Faster
                    vy: (Math.random() - 0.5) * 4,
                    type: b.data.block_type || 'default',
                    category: b.data.category || 'LABOR',
                    parents: b.parents || [],
                    pulse: 0 // Initialize heartbeat pulse
                });

                // Track links for "mesh" look
                if (b.parents) {
                    b.parents.forEach(p => {
                        window.trafficLinks.push({ source: p, target: b.hash });
                    });
                }
            }
        });

        const countEl = document.getElementById('tangle-node-count');
        if (countEl) countEl.innerText = window.trafficNodes.length;
    };

    // Main Animation Loop (Self-contained, no D3 dependency)
    (function animateTraffic() {
        requestAnimationFrame(animateTraffic);

        const canvas = document.getElementById('traffic-canvas');
        const largeCanvas = document.getElementById('tangle-canvas-large');

        // Helper to draw to a specific canvas
        function drawTo(canv) {
            if (!canv) return;
            const ctx = canv.getContext('2d');
            const width = canv.width;
            const height = canv.height;

            // Clear
            ctx.clearRect(0, 0, width, height);

            // Debug Draw (Throttle logs)
            if (Math.random() < 0.01) {
                console.log("[DEBUG] Drawing frame. Nodes: " + window.trafficNodes.length + ", Links: " + window.trafficLinks.length);
            }

            // Draw Links
            ctx.strokeStyle = 'rgba(74, 222, 128, 0.15)';
            ctx.lineWidth = 1;
            ctx.beginPath();

            // Use a map for O(1) lookups during link drawing
            const nodeMap = {};
            window.trafficNodes.forEach(n => nodeMap[n.id] = n);

            window.trafficLinks.forEach(link => {
                const s = nodeMap[link.source];
                const t = nodeMap[link.target];
                if (s && t) {
                    ctx.moveTo(s.x, s.y);
                    ctx.lineTo(t.x, t.y);
                }
            });
            ctx.stroke();

            // Draw Nodes
            window.trafficNodes.forEach(node => {
                // Physics: Move
                node.x += node.vx;
                node.y += node.vy;

                // Physics: Wall Bounce ("In a box")
                if (node.x < 10) { node.x = 10; node.vx *= -1; }
                if (node.x > width - 10) { node.x = width - 10; node.vx *= -1; }
                if (node.y < 10) { node.y = 10; node.vy *= -1; }
                if (node.y > height - 10) { node.y = height - 10; node.vy *= -1; }

                // Visuals
                let color = '#9CA3AF';
                if (node.category === 'ECO' || node.type === 'MINT') color = '#10B981';
                else if (node.type === 'TX') color = '#3B82F6';
                else if (node.type === 'WIKI') color = '#8B5CF6';
                else if (node.type === 'GENESIS') color = '#FBBF24';

                // Heartbeat Pulse Effect
                if (node.pulse > 0) {
                    node.pulse -= 0.02; // Fade out
                    if (node.pulse < 0) node.pulse = 0;
                }

                const baseRadius = (canv.id === 'tangle-canvas-large' ? 6 : 4);
                const radius = baseRadius + (node.pulse * 10);

                ctx.shadowBlur = 10 + (node.pulse * 30);
                ctx.shadowColor = color;
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
                ctx.fill();

                if (node.pulse > 0.1) {
                    ctx.strokeStyle = color;
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, radius + (1.0 - node.pulse) * 20, 0, Math.PI * 2);
                    ctx.stroke();
                }

                ctx.shadowBlur = 0;
                ctx.fillStyle = 'rgba(16,185,129,0.7)';
                ctx.beginPath();
                ctx.arc(node.x - 1, node.y - 1, 2, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        drawTo(canvas);
        drawTo(largeCanvas);
    })();


    // --- D3.js LIVE TANGLE VISUALIZATION ---
    window.tangleSimulation = null;

    window.renderTangleD3 = function (blocks) {
        const container = document.getElementById('view-tangle');
        // Only run if view is active or we are initializing for dashboard
        // Actually dashboard uses a canvas, but let's see if we can reuse this logic or keep a mini-version.
        // For 'The Ark' v1.0, we want the "Live Tangle" view to be the primary showpiece.

        const canvas = document.getElementById('tangle-canvas-large');
        if (!canvas) return; // Should exist in view-tangle

        // If we are not visible, maybe pause? For now, run key updates.

        // Transform Blocks to Nodes/Links
        // We want a DAG. 
        // Nodes = Blocks.
        // Links = Block.parents -> Block.

        const nodes = blocks.map(b => ({
            id: b.hash,
            type: b.data.block_type || 'TX',
            minter: b.data.minter,
            val: 5 // Default radius proxy
        }));

        const links = [];
        blocks.forEach(b => {
            if (b.parents && b.parents.length > 0) {
                b.parents.forEach(p => {
                    if (nodes.find(n => n.id === p)) {
                        links.push({ source: b.hash, target: p });
                    }
                });
            }
        });

        // Block Colors Map
        const colors = {
            'GENESIS': '#F59E0B',
            'MINT': '#10B981',
            'QUEST': '#3B82F6',
            'PROOF': '#8B5CF6',
            'PARTY_JOIN': '#F472B6',
            'PARTY_LEAVE': '#94A3B8',
            'TX': '#64748B',
            'GODZILLA': '#EF4444' // Red for the engine
        };

        // ... D3 force simulation will be implemented here
    };

    // --- PERSONAL INVENTORY (Private Ledger) ---
    window.addSovereignSkill = function () {
        const input = document.getElementById('new-skill');
        if (!input || !input.value.trim()) return;

        const skill = input.value.trim();
        if (!appState.privateSkills.includes(skill)) {
            appState.privateSkills.push(skill);
            localStorage.setItem('at_private_skills', JSON.stringify(appState.privateSkills));
            window.renderInventory();
            input.value = '';
            logToTerminal(`[PRIVACY] New Skill added to local sanctuary: ${skill}`);
        }
    };

    window.renderInventory = function () {
        const list = document.getElementById('skills-list');
        if (!list) return;

        list.innerHTML = appState.privateSkills.map(s => `
            <div class="badge" style="background:rgba(96, 165, 250, 0.1); color:#60A5FA; border:1px solid rgba(96, 165, 250, 0.3); padding:5px 12px;">
                ${s} <span onclick="window.removeSkill('${s}')" style="margin-left:8px; cursor:pointer; opacity:0.5;">×</span>
            </div>
        `).join('') || '<div style="color:#64748b; font-size:0.8rem;">No skills archived yet.</div>';
    };

    window.removeSkill = function (skill) {
        appState.privateSkills = appState.privateSkills.filter(s => s !== skill);
        localStorage.setItem('at_private_skills', JSON.stringify(appState.privateSkills));
        window.renderInventory();
    };

    // --- PATTERN INTERRUPTS (PSY_001) ---
    window.triggerPatternInterrupt = function (type) {
        const overlay = document.createElement('div');
        overlay.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(15, 23, 42, 0.95); z-index:10000; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; backdrop-filter:blur(10px); animation: fadeIn 0.5s;";

        let content = '';
        if (type === 'BREATHE') {
            content = `
                <div style="width:100px; height:100px; border:4px solid #10B981; border-radius:50%; animation: breathe 4s infinite alternate;"></div>
                <h2 style="color:var(--primary-light); margin-top:30px; letter-spacing:2px;">INHALE ... EXHALE</h2>
                <p style="color:#94a3b8; margin-top:10px;">Reconnecting with Biological Presence.</p>
            `;
        } else if (type === 'LOOK_UP') {
            content = `
                <div style="font-size:4rem;">🔭</div>
                <h2 style="color:#3B82F6; margin-top:20px;">LOOK UP FROM THE SCREEN</h2>
                <p style="color:#94a3b8; margin-top:10px;">Check a physical sensor or perform a community task.</p>
            `;
        }

        overlay.innerHTML = content;
        document.body.appendChild(overlay);

        setTimeout(() => {
            overlay.style.opacity = '0';
            setTimeout(() => document.body.removeChild(overlay), 500);
        }, 5000);
    };

    // --- SWARM LEADERBOARD (FBCC 8) ---
    function renderSwarmLeaderboard(blocks) {
        // 1. Calculate Swarm Scores
        // We scan ledger for PROOF blocks. If the quest_id belongs to a swarm, add points.
        // Since we might not have the full quest DB loaded in memory for every block if it's old, 
        // we rely on appState.tasks which has the loaded truck quests.

        const scores = {
            'CHASSIS': 0,
            'DRIVETRAIN': 0,
            'SYSTEMS': 0,
            'BODY': 0
        };

        const questMap = {};
        appState.tasks.forEach(t => {
            if (t.swarm) questMap[t.quest_id] = t.swarm;
        });

        blocks.forEach(b => {
            if (b.data.block_type === 'PROOF') {
                const qId = b.data.quest_id;
                const swarm = questMap[qId];
                if (swarm) {
                    // Estimated value: 500 points per proof? 
                    // Ideally we'd look up the bounty_at, but for now we count completions.
                    scores[swarm] += 100;
                }
            }
        });

        // 2. Render
        const container = document.getElementById('swarm-leaderboard');
        if (!container) return; // Only if we create this element in HTML or dynamically inject it

        // Auto-inject if missing (e.g. in the dashboard or contest view)
        // For now, let's assume we want to inject it into the Dashboard sidebar or main view
        // We'll skip if specific container isn't found, but maybe we should add it to 'renderLeaderboard'?
        return scores;
    }

    // Extended Render Leaderboard to include Swarms
    function renderLeaderboardWithSwarms(userLeaderboard, swarms) {
        const container = document.getElementById('leaderboard-container');
        if (!container) return;

        // Render Swarm Section
        let swarmHTML = `
            <div style="margin-bottom: 30px; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; border: 1px solid rgba(16,185,129,0.05);">
                <h3 style="color: #FBBF24; margin-top: 0;">🏆 GodZilla Cup Standings</h3>
                <div style="display: flex; gap: 10px; height: 100px; align-items: flex-end;">
        `;

        const maxScore = Math.max(...Object.values(swarms), 1);

        for (const [swarm, score] of Object.entries(swarms)) {
            const h = Math.max(10, (score / maxScore) * 80);
            const color = swarm === 'DRIVETRAIN' ? '#EF4444' : (swarm === 'CHASSIS' ? '#3B82F6' : '#10B981');
            swarmHTML += `
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center;">
                    <div style="font-weight: bold; color: white; margin-bottom: 5px;">${score}</div>
                    <div style="width: 100%; background: ${color}; height: ${h}%; border-radius: 4px 4px 0 0; opacity: 0.8;"></div>
                    <div style="margin-top: 5px; font-size: 0.7rem; color: #94a3b8;">${swarm}</div>
                </div>
            `;
        }
        swarmHTML += `</div></div>`;

        // Render standard user table...
        // ... (Rest of existing renderLeaderboard logic)

        // Dummy Data + Current User
        var leaders = [
            { name: "Seeker", xp: 15400, mints: 42, role: "Architect" },
            { name: "Marcin", xp: 12100, mints: 38, role: "Founder" },
            { name: "Gaddafi_Ghost", xp: 8900, mints: 12, role: "Legend" },
            { name: appState.currentUser.name, xp: appState.xp, mints: 0, role: "Guest" }
        ].sort((a, b) => b.xp - a.xp);

        container.innerHTML = swarmHTML + `
            <div style="margin-bottom:15px; display:flex; gap:10px;">
                <button class="btn-xs" style="background:#3B82F6; color:white; border:none; padding:4px 8px; border-radius:4px;">Top XP</button>
            </div>
            <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                <!-- ... existing header ... -->
                <tr style="text-align:left; color:#94a3b8;">
                    <th style="padding:10px;">Rank</th>
                    <th>User</th>
                    <th>Role</th>
                    <th>XP</th>
                    <th>Mints</th>
                </tr>
                ${leaders.map((l, i) => `
                    <tr style="border-bottom:1px solid rgba(16,185,129,0.05);">
                        <td style="padding:10px; color:${i === 0 ? '#FBBF24' : 'var(--text-main)'}; font-weight:${i === 0 ? 'bold' : 'normal'}">#${i + 1}</td>
                        <td style="color:#eff6ff;">${l.name} ${l.name === appState.currentUser.name ? '(You)' : ''}</td>
                        <td><span style="background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:4px; font-size:0.75rem;">${l.role}</span></td>
                        <td style="font-family:'JetBrains Mono'; color:#10B981;">${l.xp.toLocaleString()}</td>
                        <td style="font-family:'JetBrains Mono';">${l.mints}</td>
                    </tr>
                `).join('')}
            </table>
        `;
    }


    // --- COSMIC MAP (MISSION CONTROL) ---
    window.renderCosmicMap = function () {
        const list = document.getElementById('mission-status-list');
        if (!list) return;
        list.innerHTML = '<div style="padding:20px; text-align:center; color:#64748b;">Scanning Mission Space...</div>';

        fetch('/api/evolution')
            .then(r => r.json())
            .then(data => {
                list.innerHTML = '';

                // 1. Show Active Missions (Proposed by AI)
                if (data.active_missions && data.active_missions.length > 0) {
                    const header = document.createElement('div');
                    header.style = "padding:10px; font-size:0.75rem; color:#FBBF24; font-weight:bold; letter-spacing:1px; background:rgba(251, 191, 36, 0.05);";
                    header.innerText = "🌌 AI PROPOSED UPGRADES";
                    list.appendChild(header);

                    data.active_missions.forEach(m => {
                        const li = document.createElement('li');
                        li.style.cssText = "padding:10px; border-bottom:1px solid rgba(16,185,129,0.1); display:flex; flex-direction:column; gap:5px;";
                        li.innerHTML = `
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-weight:700; color:var(--primary-light);">${m.title}</span>
                                <span class="badge" style="background:rgba(59,130,246,0.1); color:#3B82F6; border:1px solid #3B82F6;">PROPOSED</span>
                            </div>
                            <div style="font-size:0.8rem; color:#94a3b8;">${m.description}</div>
                        `;
                        list.appendChild(li);
                    });
                }

                // 2. Show Core System Tasks
                const systemTasks = [
                    { name: "Mycelium Economic Engine", status: "ONLINE", color: "#10B981" },
                    { name: "Terminal Console", status: "ONLINE", color: "#10B981" },
                    { name: "P2P Bounty Board", status: "ONLINE", color: "#10B981" },
                    { name: "Steward AI Evolution", status: "ONLINE", color: "#10B981" },
                    { name: "Cross-Node Federation", status: "PARTIAL", color: "#F59E0B" }
                ];

                const sHeader = document.createElement('div');
                sHeader.style = "padding:10px; font-size:0.75rem; color:#10B981; font-weight:bold; letter-spacing:1px; background:rgba(16, 185, 129, 0.05); margin-top:10px;";
                sHeader.innerText = "🛰️ CORE SYSTEM STATE";
                list.appendChild(sHeader);

                systemTasks.forEach(t => {
                    const li = document.createElement('li');
                    li.style.cssText = "padding:10px; border-bottom:1px solid rgba(16,185,129,0.1); display:flex; justify-content:space-between;";
                    li.innerHTML = `
                        <span>${t.name}</span>
                        <span class="badge" style="background:${t.color}20; color:${t.color}; border:1px solid ${t.color};">${t.status}</span>
                    `;
                    list.appendChild(li);
                });

                // Update Active Task (Parse from task.md - Hardcoded for now)
                document.getElementById('current-task-name').innerText = "Evolutionary Loop v2";
                document.getElementById('current-task-status').innerText = "Autonomous Idea Capture Active";
            }).catch(e => {
                console.warn("[MAP] Cosmic Map Fetch Failed:", e);
                list.innerHTML = '<div style="padding:20px; text-align:center; color:#EF4444;">⚠️ Intelligence scan failed.</div>';
            });
    }


    async function loadState() {
        console.log("[GAIA] Loading State...");
        try {
            const fetchJson = async (url) => {
                try {
                    const r = await fetch(url + "?v=" + Date.now()); // Bust cache
                    if (!r.ok) return [];
                    return await r.json();
                } catch (e) {
                    console.warn(`[GAIA] Failed to load ${url}:`, e);
                    return [];
                }
            };

            const [seedQuests, seh7Data, truckQuests] = await Promise.all([
                fetchJson('quests_seed.json'),
                fetchJson('seh7_quests.json'),
                fetchJson('truck_quests.json')
            ]);

            // Clear current tasks to avoid duplicates on re-init
            appState.tasks = [];
            const currentIds = new Set();

            // 1. Process Seeds
            if (Array.isArray(seedQuests)) {
                seedQuests.forEach(q => {
                    if (!currentIds.has(q.quest_id)) {
                        appState.tasks.push(q);
                        currentIds.add(q.quest_id);
                    }
                });
            }

            // 2. Process SEH7
            if (seh7Data && seh7Data.phases) {
                seh7Data.phases.forEach(phase => {
                    phase.quests.forEach(q => {
                        if (!currentIds.has(q.id)) {
                            appState.tasks.push({
                                quest_id: q.id,
                                title: q.title,
                                description: `SEH7 ${phase.phase}: ${q.description || q.title}`,
                                category: q.category || 'CONSTRUCTION',
                                bounty_at: q.at || q.bounty_at,
                                estimated_time: q.hours ? `${q.hours}h` : 'Unknown',
                                status: 'OPEN',
                                icon: '🏗️'
                            });
                            currentIds.add(q.id);
                        }
                    });
                });
            }

            // 3. Process Truck
            if (Array.isArray(truckQuests)) {
                truckQuests.forEach(q => {
                    if (!currentIds.has(q.quest_id)) {
                        if (!q.status) q.status = 'OPEN';
                        appState.tasks.push(q);
                        currentIds.add(q.quest_id);
                    }
                });
            }

            console.log(`[GAIA] State Loaded. Total Tasks: ${appState.tasks.length}`);

            // Persistence: Load balance/XP
            const saved = localStorage.getItem('abundanceState');
            const savedUser = localStorage.getItem('at_username');
            const savedRole = localStorage.getItem('at_role');

            if (savedUser) {
                appState.currentUser.name = savedUser;
                appState.currentUser.role = savedRole || 'worker';
            }

            if (saved) {
                const parsed = JSON.parse(saved);
                appState.balance = parsed.balance || appState.balance;
                appState.xp = parsed.xp || appState.xp;
            }

            updateUI();
        } catch (err) {
            console.error("[GAIA] loadState failed:", err);
            updateUI();
        }
    }

    function saveState() {
        localStorage.setItem('abundanceState', JSON.stringify({
            balance: appState.balance,
            history: appState.history,
            xp: appState.xp
        }));
        // User info is saved during login, but we ensure role is kept
        localStorage.setItem('at_role', appState.currentUser.role);
    }

    // Note: The primary updateUI is defined in the window scope above. 
    // This section consolidates all refresh triggers to that function.
    window.forceUIRefresh = function () {
        if (window.updateUI) window.updateUI();
    };

    function checkRoleAssignment() {
        if (!appState.currentUser || appState.currentUser.name === 'Guest') return;
        if (!appState.currentUser.role_name) {
            showRolePickerModal();
        }
    }

    window.showRolePickerModal = function () {
        if (document.getElementById('role-modal')) return;
        const modal = document.createElement('div');
        modal.id = 'role-modal';
        modal.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:10000; display:flex; align-items:center; justify-content:center; backdrop-filter:blur(10px);";
        modal.innerHTML = `
            <div style="background:var(--surface); padding:40px; border-radius:24px; width:95%; max-width:900px; max-height:90vh; overflow-y:auto; border:1px solid var(--border);">
                <div style="text-align:center; margin-bottom:30px;"><h1 style="color:#10B981;">Choose Your Path</h1></div>
                <div id="roles-grid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap:20px;"></div>
            </div>
        `;
        document.body.appendChild(modal);
        fetch('/api/roles').then(r => r.json()).then(data => {
            const grid = document.getElementById('roles-grid');
            grid.innerHTML = data.roles.map(r => `
                <div class="glass-panel" onclick="window.confirmRoleSelection('${r.id}', '${r.name}')" style="padding:20px; border-radius:12px; cursor:pointer; text-align:center;">
                    <div style="font-size:3rem; margin-bottom:10px;">${r.icon}</div>
                    <h3 style="margin:5px 0;">${r.name}</h3>
                    <p style="font-size:0.8rem; color:#94a3b8;">${r.description}</p>
                </div>
        `).join('');
        }).catch(e => {
            console.error("[ROLES] Failed to load role config:", e);
            const grid = document.getElementById('roles-grid');
            if (grid) grid.innerHTML = '<div style="color:#EF4444; text-align:center; padding:20px;">⚠️ Role dispatcher offline.</div>';
        });
    }

    window.confirmRoleSelection = function (roleId, roleName) {
        if (!confirm(`Serve as ${roleName}?`)) return;
        window.apiFetch('/api/assign-role', { method: 'POST', body: { username: appState.currentUser.name, role_id: roleId } })
            .then(res => {
                if (res.status === 'success') {
                    appState.currentUser.role_name = roleName;
                    document.getElementById('role-modal').remove();
                    // FBCC 8: Pick Swarm
                    if (!appState.currentUser.swarm) window.showSwarmPickerModal();
                    else updateUI();
                }

                // --- SWARM REGISTRATION (FBCC 8) ---
                window.showSwarmPickerModal = function () {
                    if (document.getElementById('swarm-modal')) return;
                    const modal = document.createElement('div');
                    modal.id = 'swarm-modal';
                    modal.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:10001; display:flex; align-items:center; justify-content:center; backdrop-filter:blur(10px);";
                    modal.innerHTML = `
            <div style="background:var(--surface); padding:40px; border-radius:24px; width:95%; max-width:800px; border:2px solid #F59E0B;">
                <div style="text-align:center; margin-bottom:30px;">
                    <h1 style="color:#F59E0B;">Join Your Swarm</h1>
                    <p style="color:#bfdbfe;">The Truck Build requires synchronization. Choose your unit.</p>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap:20px;">
                    <div onclick="window.confirmSwarm('CHASSIS')" class="glass-panel" style="cursor:pointer; text-align:center; padding:20px; border-left:4px solid #3B82F6;">
                        <div style="font-size:3rem;">🏗️</div>
                        <h3>Chassis</h3>
                    </div>
                    <div onclick="window.confirmSwarm('DRIVETRAIN')" class="glass-panel" style="cursor:pointer; text-align:center; padding:20px; border-left:4px solid #EF4444;">
                        <div style="font-size:3rem;">⚙️</div>
                        <h3>Drivetrain</h3>
                    </div>
                    <div onclick="window.confirmSwarm('SYSTEMS')" class="glass-panel" style="cursor:pointer; text-align:center; padding:20px; border-left:4px solid #10B981;">
                        <div style="font-size:3rem;">⚡</div>
                        <h3>Systems</h3>
                    </div>
                    <div onclick="window.confirmSwarm('BODY')" class="glass-panel" style="cursor:pointer; text-align:center; padding:20px; border-left:4px solid #8B5CF6;">
                        <div style="font-size:3rem;">🛡️</div>
                        <h3>Body/Interior</h3>
                    </div>
                </div>
            `;
                    document.body.appendChild(modal);
                }

                window.confirmSwarm = function (swarmName) {
                    if (!confirm(`Join ${swarmName} Swarm ? `)) return;
                    appState.currentUser.swarm = swarmName;
                    document.getElementById('swarm-modal').remove();
                    alert(`Reporting for duty: ${swarmName} Swarm.`);
                    updateUI();
                }
            }).catch(e => {
                console.error("[ROLES] Role assignment failed:", e);
                alert("⚠️ Failed to assign role. Connection error.");
            });
    }

    function renderWalletUI() {
        // Generate address if needed
        if (!appState.currentUser.mnemonic) {
            appState.currentUser.mnemonic = Wallet.generateMnemonic();
            appState.currentUser.address = Wallet.deriveAddress(appState.currentUser.mnemonic);
        }

        var walletAddress = document.getElementById('wallet-address');
        var walletBalance = document.getElementById('wallet-balance');
        var walletXP = document.getElementById('wallet-xp');
        var walletTier = document.getElementById('wallet-tier');
        var walletHM = document.getElementById('wallet-hm');

        if (walletAddress) walletAddress.textContent = appState.currentUser.address;
        if (walletBalance) walletBalance.textContent = appState.balance.toFixed(2);
        if (walletXP) walletXP.textContent = Math.floor(appState.xp).toLocaleString();

        const hours = appState.currentUser.verified_hours || 0;
        const tier = hours >= 500 ? '🏛️ Master' : (hours >= 100 ? '🛠️ Journeyman' : '🌱 Apprentice');
        if (walletTier) walletTier.textContent = tier;
        if (walletHM) walletHM.textContent = `${(appState.currentUser.hm || 1.0).toFixed(2)}x`;


        // ART WALK MODE: Enhanced Mobile Actions
        const walletView = document.getElementById('view-wallet');
        const isArtWalk = document.body.classList.contains('art-walk-mode');

        // Remove existing art walk containers if re-rendering
        const existingArtWalk = document.getElementById('art-walk-mobile-actions');
        if (existingArtWalk) existingArtWalk.remove();

        if (isArtWalk && walletView) {
            const artWalkGroup = document.createElement('div');
            artWalkGroup.id = 'art-walk-mobile-actions';
            artWalkGroup.style.marginTop = '20px';
            artWalkGroup.innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    <button class="btn-primary mobile-one-hand-btn" onclick="switchView('mint')">⚡ QUICK MINT LABOR</button>
                    <button class="btn-secondary mobile-one-hand-btn" style="background:var(--secondary-glow); border:1px solid var(--secondary);" onclick="renderExchangeUI()">⚡ BUY AT (SWAP BTC)</button>
                    <button class="btn-secondary mobile-one-hand-btn" onclick="window.renderSendModal()">↗ SEND AT TO PEER</button>
                </div>
            `;
            walletView.prepend(artWalkGroup);
        }

        // ADD WIKI SYNC BUTTON
        if (walletView && !document.getElementById('wiki-sync-btn-container')) {
            const btnGroup = document.createElement('div');
            btnGroup.id = 'wiki-sync-btn-container';
            btnGroup.style.marginTop = '20px';
            btnGroup.innerHTML = `
                <button class="btn-primary" onclick="showWikiImportModal()" style="font-size:0.9rem; background: var(--secondary); border: 1px solid rgba(16,185,129,0.1);">
                    🔄 Sync from Wiki
                </button>
        `;
            walletView.appendChild(btnGroup);
        }

        // --- RENDER HISTORY ---
        renderWalletHistory();
    }

    function renderWalletHistory() {
        const container = document.getElementById('wallet-history');
        if (!container) return;

        // Filter ledger for blocks relevant to current user
        const username = appState.currentUser.name;
        const myActions = rawState.ledger.filter(b => {
            const d = b.data || {};
            return (d.minter === username || d.sender === username || d.receiver === username || d.worker === username);
        }).reverse();

        if (myActions.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 30px; color: var(--text-muted);">
                    <div style="font-size: 2rem; margin-bottom: 10px;">📭</div>
                    <p>No transactions yet.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = myActions.slice(0, 10).map(b => {
            const d = b.data || {};
            const isMint = ['MINT', 'LABOR', 'CODE_MINT'].includes(b.type);
            const amt = d.reward || d.at || d.at_reward || (d.hours ? d.hours * 10 : 0);
            const status = d.verified === false ? 'PENDING' : 'VERIFIED';

            return `
                <div class="glass-panel" style="padding: 12px; font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center; border-left: 2px solid ${isMint ? '#10B981' : '#60A5FA'};">
                    <div>
                        <div style="font-weight: 600;">${b.type}: ${d.task || d.description || 'Transfer'}</div>
                        <div style="font-size: 0.75rem; opacity: 0.6;">${new Date(b.timestamp * 1000).toLocaleString()}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 700; color: ${isMint ? '#10B981' : '#F1F5F9'};">${isMint ? '+' : ''}${amt.toFixed(2)} AT</div>
                        <div style="display: flex; gap: 8px; margin-top: 5px; justify-content: flex-end;">
                            <span style="font-size: 0.65rem; padding: 2px 6px; background: rgba(0,0,0,0.3); border-radius: 4px;">${status}</span>
                            <button onclick="window.openDisputeModal('${b.hash}')" style="background: none; border: none; font-size: 0.9rem; cursor: pointer; color: #EF4444; title: 'Flag/Dispute'">🚩</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    window.openDisputeModal = function (blockHash) {
        const reason = prompt("Describe the issue (e.g. Fraudulent claim, Incorrect hours, Math error):");
        if (!reason) return;

        apiFetch('/api/justice/dispute', {
            method: 'POST',
            body: { block_hash: blockHash, reason: reason }
        }).then(res => {
            if (res.status === 'disputed') {
                logToTerminal(`[JUSTICE] Block ${blockHash.substring(0, 8)} flagged for review.`);
                alert(res.message);
            } else {
                alert("Flagging failed: " + res.message);
            }
        });
    };


    window.showWikiImportModal = function () {
        const modal = document.createElement('div');
        modal.id = 'wiki-modal';
        modal.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; display:flex; align-items:center; justify-content:center; backdrop-filter:blur(5px);";
        modal.innerHTML = `
            <div style="background:var(--surface); padding:30px; border-radius:16px; width:90%; max-width:600px; border:1px solid var(--border); box-shadow:0 25px 50px -12px rgba(0,0,0,0.5);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h2 style="margin:0;">Wiki Log Importer</h2>
                    <button onclick="document.getElementById('wiki-modal').remove()" style="background:none; border:none; color:#64748b; font-size:1.5rem; cursor:pointer;">&times;</button>
                </div>
                <p style="color:#94a3b8; margin-bottom:15px; font-size:0.9rem;">Paste your OSE Wiki work log table. The system will automatically parse and mint your labor tokens.</p>
                <textarea id="wiki-import-text" placeholder="| Date | Hours | Task | ..." style="width:100%; height:200px; background:#0f172a; border:1px solid var(--border); border-radius:8px; color:var(--primary-light); padding:15px; font-family:'JetBrains Mono', monospace; font-size:0.85rem;"></textarea>
                <div style="margin-top:20px; display:flex; justify-content:flex-end; gap:12px;">
                    <button class="btn-secondary" onclick="document.getElementById('wiki-modal').remove()">Cancel</button>
                    <button class="btn-primary" onclick="window.runWikiImport()">🚀 Import & Mint</button>
                </div>
            </div >
        `;
        document.body.appendChild(modal);
    }

    window.runWikiImport = function () {
        const text = document.getElementById('wiki-import-text').value;
        if (!text) return alert("Please paste wiki content first.");

        const btn = event.target;
        btn.innerText = "Processing...";
        btn.disabled = true;

        window.apiFetch('/api/wiki/import', {
            method: 'POST',
            body: { raw_markdown: text }
        }).then(res => {
            if (res.status === 'success') {
                logToTerminal(`[WIKI] ${res.message} `);
                alert(res.message);
                document.getElementById('wiki-modal').remove();
                syncWithLedger();
            } else {
                alert("Import failed: " + res.message);
                btn.innerText = "🚀 Import & Mint";
                btn.disabled = false;
            }
        }).catch(err => {
            alert("Error: " + err);
            btn.innerText = "🚀 Import & Mint";
            btn.disabled = false;
        });
    }

    // --- TREASURY BOT LOGIC ---
    function renderTreasuryUI() {
        const container = document.getElementById('treasury-balances');
        if (!container) return;

        apiFetch('/api/treasury/status')
            .then(data => {
                // Update Simulation Badge
                const simBadge = document.getElementById('bot-simulation-badge');
                if (simBadge) {
                    simBadge.innerText = data.simulation ? 'SIMULATION MODE' : 'PRODUCTION MODE';
                    simBadge.style.color = data.simulation ? '#F59E0B' : '#10B981';
                    simBadge.style.borderColor = data.simulation ? '#F59E0B' : '#10B981';
                }

                // Update Balances
                container.innerHTML = data.accounts.map(acc => `
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(0,0,0,0.2); border-radius:8px;">
                        <span style="font-size:0.9rem; font-weight:600;">${acc.name}</span>
                        <span style="color:${acc.balance.currency === 'AT' ? 'var(--primary-light)' : '#f1f5f9'}; font-weight:700;">
                            ${acc.balance.amount} ${acc.balance.currency}
                        </span>
                    </div>
                `).join('');

                // Update Strategies
                const stratList = document.getElementById('bot-strategies-list');
                if (stratList) {
                    stratList.innerHTML = data.active_strategies.map(s => `
                        <div class="badge" style="background:rgba(59,130,246,0.1); color:#60A5FA; border:1px solid #60A5FA;">${s}</div>
                    `).join('');
                }

                // Update Status
                const statusEl = document.getElementById('bot-status-indicator');
                if (statusEl) {
                    statusEl.innerText = data.status;
                    statusEl.style.color = data.status === 'ONLINE' ? '#10B981' : '#EF4444';
                }
            })
            .catch(e => {
                container.innerHTML = `<div style="color:#EF4444; padding:20px;">Failed to fetch treasury data.</div>`;
            });
    }

    window.toggleTreasuryBot = function () {
        const confirmMsg = "Emergency Stop will pause all autonomous trading. Proceed?";
        if (confirm(confirmMsg)) {
            logToTerminal("[TREASURY] Manual override: Emergency Stop engaged.");
            // In a real setup, we'd call a POST endpoint to stop it
        }
    }

    window.pollTreasury = function () {
        if (document.getElementById('view-treasury').style.display !== 'none') {
            renderTreasuryUI();
        }
    }
    setInterval(window.pollTreasury, 5000);


    // --- STEWARD AI CHAT (Unified) ---
    window.stewardHistory = [];

    window.renderStewardChat = function () {
        var container = document.getElementById('view-steward');
        if (!container) return;

        container.innerHTML = `
        <div style="display:flex; flex-direction:column; height:100%; max-height:85vh; gap:20px;">
            <div class="glass-panel" style="flex:1; display:flex; flex-direction:column; padding:0; overflow:hidden; border-radius:16px;">
                <div style="padding:15px; background:rgba(139, 92, 246, 0.1); border-bottom:1px solid rgba(139, 92, 246, 0.2); display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:10px; height:10px; background:#10B981; border-radius:50%; box-shadow:0 0 10px #10B981;"></div>
                        <span style="font-weight:bold; letter-spacing:1px; color:var(--primary-light);">STEWARD NEXUS</span>
                    </div>
                    <span style="font-size:0.7rem; color:#64748b; font-family:'JetBrains Mono';">v1.1.0-ALPHA</span>
                </div>
                
                <div id="steward-chat-log" style="flex:1; overflow-y:auto; background:rgba(15,23,42,0.4); padding:20px; display:flex; flex-direction:column; gap:15px; min-height:300px;">
                    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(139, 92, 246, 0.2); color:#94a3b8; padding:12px 16px; border-radius:12px; align-self:center; font-size:0.8rem; font-family:'JetBrains Mono'; max-width:80%; text-align:center;">
                        SYSTEM IDENTIFIED. GREETING SEED USER. THE MISSION CONTINUES. HOW MAY THE STEWARD ASSIST?
                    </div>
                </div>
            </div>
            
            <div style="display:flex; gap:12px;">
                <input type="text" id="steward-input" placeholder="Ask the Steward..." 
                    style="flex:1; background:#1e293b; border:1px solid rgba(139,92,246,0.3); border-radius:12px; padding:14px 16px; color:#e2e8f0; font-size:1rem; outline:none;"
                    onkeypress="if(event.key==='Enter') window.sendStewardMessage();">
                <button onclick="window.sendStewardMessage()" 
                    style="background:#8B5CF6; color:white; border:none; padding:14px 24px; border-radius:12px; font-weight:600; cursor:pointer; transition:all 0.2s; box-shadow:0 0 15px rgba(139, 92, 246, 0.3);">
                    EXECUTE
                </button>
            </div>
            
            <div style="margin-top:4px; display:flex; gap:8px; flex-wrap:wrap;">
                <button onclick="window.quickSteward('What quests are available?')" class="btn-xs" style="background:rgba(139,92,246,0.1); color:#e2e8f0; border:1px solid rgba(139,92,246,0.2); padding:6px 12px; border-radius:6px; cursor:pointer; font-size:0.75rem;">📋 Quests</button>
                <button onclick="window.quickSteward('How do I earn AT?')" class="btn-xs" style="background:rgba(139,92,246,0.1); color:#e2e8f0; border:1px solid rgba(139,92,246,0.2); padding:6px 12px; border-radius:6px; cursor:pointer; font-size:0.75rem;">💰 Earn AT</button>
                <button onclick="window.quickSteward('What is the current system status?')" class="btn-xs" style="background:rgba(139,92,246,0.1); color:#e2e8f0; border:1px solid rgba(139,92,246,0.2); padding:6px 12px; border-radius:6px; cursor:pointer; font-size:0.75rem;">📊 Status</button>
                <button onclick="window.clearStewardHistory()" class="btn-xs" style="background:rgba(239,68,68,0.1); color:#fecaca; border:1px solid rgba(239,68,68,0.2); padding:6px 12px; border-radius:6px; cursor:pointer; font-size:0.75rem;">🗑️ Clear</button>
            </div>
        </div>
        `;

        // Render existing messages if any
        if (window.stewardHistory.length > 0) {
            renderStewardMessages();
        }
    };

    window.quickSteward = function (message) {
        const inp = document.getElementById('steward-input');
        if (inp) {
            inp.value = message;
            window.sendStewardMessage();
        }
    };

    window.clearStewardHistory = function () {
        window.stewardHistory = [];
        window.renderStewardChat();
    };

    function renderStewardMessages() {
        const container = document.getElementById('steward-chat-log');
        if (!container || window.stewardHistory.length === 0) return;

        container.innerHTML = window.stewardHistory.map(msg => `
        <div style="margin-bottom:10px; display:flex; flex-direction:column; ${msg.role === 'user' ? 'align-items:flex-end;' : 'align-items:flex-start;'}">
            <div style="background:${msg.role === 'user' ? 'var(--primary)' : 'rgba(30, 41, 59, 0.8)'}; 
                        border:${msg.role === 'user' ? 'none' : '1px solid #8B5CF6'};
                        color:${msg.role === 'user' ? 'black' : 'var(--text-main)'}; 
                        padding:12px 18px; 
                        border-radius:${msg.role === 'user' ? '15px 15px 0 15px' : '15px 15px 15px 0'}; 
                        font-size:0.95rem; line-height:1.4; max-width:85%;
                        font-weight:${msg.role === 'user' ? '600' : 'normal'};">
                ${msg.content.replace(/\n/g, '<br>')}
            </div>
        </div>
        `).join('');

        container.scrollTop = container.scrollHeight;
    }

    window.sendStewardMessage = async function () {
        const input = document.getElementById('steward-input');
        const message = input.value.trim();
        if (!message) return;

        // Add user message to history
        window.stewardHistory.push({ role: 'user', content: message });
        input.value = '';
        renderStewardMessages();

        // Show typing indicator
        const container = document.getElementById('steward-chat-log');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'steward-typing';
        typingDiv.innerHTML = `
            <div style="align-self:flex-start; background:rgba(30, 41, 59, 0.8); border:1px solid #8B5CF6; color:#64748b; padding:12px 16px; border-radius:15px 15px 15px 0; font-size:0.9rem;">
                <span class="typing-dots">Steward is analyzing<span>.</span><span>.</span><span>.</span></span>
            </div>
        `;
        container.appendChild(typingDiv);
        container.scrollTop = container.scrollHeight;

        try {
            const data = await apiFetch('/api/steward/chat', {
                method: 'POST',
                body: {
                    message: message,
                    history: window.stewardHistory.slice(0, -1)
                }
            });

            // Remove typing indicator
            document.getElementById('steward-typing')?.remove();

            // Backend returns data.output based on h_steward_chat
            const reply = data.output || data.response || "Intelligence received. The mission expands.";
            window.stewardHistory.push({ role: 'assistant', content: reply });
            renderStewardMessages();
            if (window.playSound) window.playSound('steward');

        } catch (e) {
            document.getElementById('steward-typing')?.remove();
            window.stewardHistory.push({
                role: 'assistant',
                content: '⚠️ **Connection Error**: Steward communication link unstable. Retrying synchronization...'
            });
            renderStewardMessages();
        }
    };

    // --- THE MYCELIUM STORE (Unified Rendering) ---
    window.renderMyceliumStore = function () {
        var container = document.getElementById('view-store');
        if (!container) return;
        container.innerHTML = '<div style="text-align:center; color:#94a3b8; padding:40px;">Loading Mycelium...</div>';

        apiFetch('/api/store/list').then(data => {
            var items = data || [];
            var html = `
                <div class="section-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 25px;">
                    <div>
                        <h2 style="font-size: 1.8rem; letter-spacing:-0.5px;">🌿 The Mycelium</h2>
                        <p style="color:#94a3b8; font-size:0.95rem;">Peer-to-Peer Sovereign Marketplace. Trade for AT.</p>
                    </div>
                    <button onclick="window.toggleListingForm()" class="btn-primary" style="font-size:0.9rem; padding:10px 20px;">+ List Asset</button>
                </div>

                <div id="listing-form-container" class="glass-panel" style="display:none; margin-bottom: 30px; border: 1px solid var(--primary-light);">
                    <h3 style="color:var(--primary-light); margin-bottom:20px;">📦 Registry of Local Abundance</h3>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                        <input type="text" id="list-title" placeholder="Item Name" class="input-dark">
                        <input type="number" id="list-price" placeholder="Price (AT)" class="input-dark">
                        <textarea id="list-desc" placeholder="Manifest description..." class="input-dark" style="grid-column: span 2; height:80px;"></textarea>
                        <select id="list-image" class="input-dark">
                            <option value="🌱">🌱 Seed Pack</option>
                            <option value="🔋">🔋 Energy Module</option>
                            <option value="🛠️">🛠️ Tools</option>
                            <option value="🍎">🍎 Food</option>
                        </select>
                        <button onclick="window.submitListing()" class="btn-primary">PUBLISH LISTING</button>
                    </div>
                </div>

                <div class="grid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap:20px;">
            `;

            if (items.length === 0) {
                html += '<div style="grid-column: 1 / -1; text-align:center; padding:40px; color:var(--text-muted);">No assets available in the mesh. Be the first to list!</div>';
            } else {
                items.forEach(item => {
                    html += `
                        <div class="glass-panel" style="padding:0; overflow:hidden; display:flex; flex-direction:column; transition: transform 0.2s;">
                            <div style="height:140px; background:rgba(16,185,129,0.03); display:flex; align-items:center; justify-content:center; font-size:4rem; border-bottom:1px solid rgba(16,185,129,0.1);">
                                ${item.icon || item.image_emoji || '📦'}
                            </div>
                            <div style="padding:20px; flex:1; display:flex; flex-direction:column;">
                                <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:12px;">
                                    <h4 style="margin:0; font-size:1.15rem; color:#f8fafc; font-weight:700;">${item.name || item.title}</h4>
                                    <span style="background:rgba(16,185,129,0.1); color:#10B981; padding:4px 10px; border-radius:6px; font-weight:bold; font-family:'JetBrains Mono';">${item.price || item.price_at} AT</span>
                                </div>
                                <p style="font-size:0.85rem; color:#94a3b8; flex:1; margin-bottom:20px; line-height:1.5;">${item.desc || item.description}</p>
                                <button onclick="window.buyItem('${item.id}')" class="btn-primary" style="width:100%; letter-spacing:1px; font-weight:700;">ACQUIRE</button>
                            </div>
                        </div>`;
                });
            }

            html += `</div>`;
            container.innerHTML = html;
        }).catch(e => {
            console.error("[MARKET] Fetch Failed:", e);
            container.innerHTML = `<div class="glass-panel" style="color:#EF4444; text-align:center; padding:40px;">⚠️ Mycelium Connection Lost. Verify Node Status.</div>`;
        });
    };

    window.showListItemForm = function () {
        document.getElementById('store-list-form').style.display = 'block';
    };

    window.submitListing = function () {
        var payload = {
            seller: appState.currentUser.name,
            title: document.getElementById('list-title').value,
            description: document.getElementById('list-desc').value,
            price_at: parseFloat(document.getElementById('list-price').value) || 0,
            category: document.getElementById('list-category').value,
            image_emoji: document.getElementById('list-emoji').value
        };

        fetch('/api/store/list', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Item Listed Successfully!');
                    document.getElementById('store-list-form').style.display = 'none';
                    window.renderMyceliumStore(); // Refresh
                } else {
                    alert('Error: ' + data.message);
                }
            }).catch(e => {
                console.error("[MARKET] Listing failed:", e);
                alert("⚠️ Marketplace listing failed. No connection.");
            });
    };

    window.buyItem = function (itemId) {
        if (!confirm('Confirm purchase? This will deduct AT from your balance.')) return;

        fetch('/api/store/buy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId, buyer: appState.currentUser.name })
        })
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                window.renderMyceliumStore(); // Refresh
            }).catch(e => {
                console.error("[MARKET] Purchase failed:", e);
                alert("⚠️ Purchase failed. Backend unreachable.");
            });
    };

    function logToTerminal(msg) {
        if (!terminalLog) return;
        var line = document.createElement('div');
        line.className = 'log-line';
        line.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
        terminalLog.appendChild(line);
        terminalLog.scrollTop = terminalLog.scrollHeight;
    }

    // --- FEEDBACK SYSTEM ---
    window.openFeedbackForm = function () {
        if (document.getElementById('feedback-modal')) return;

        const userRole = (appState.currentUser && appState.currentUser.role_name) ? appState.currentUser.role_name : 'No Role';
        const userSwarm = (appState.currentUser && appState.currentUser.swarm) ? appState.currentUser.swarm : 'No Swarm';

        const modal = document.createElement('div');
        modal.id = 'feedback-modal';
        modal.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:10000; display:flex; align-items:center; justify-content:center; backdrop-filter:blur(10px);";
        modal.innerHTML = `
                <div style="background:var(--surface); padding:30px; border-radius:16px; width:90%; max-width:500px; border:1px solid var(--border); box-shadow: 0 0 30px rgba(239, 68, 68, 0.2);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                        <div>
                            <h2 style="margin:0; color:#F87171;">🐞 High-Signal Feedback</h2>
                            <p style="font-size: 0.75rem; color: #94a3b8; margin:0;">Context: ${userRole} | ${userSwarm}</p>
                        </div>
                        <button onclick="document.getElementById('feedback-modal').remove()" style="background:none; border:none; color:#94a3b8; font-size:1.5rem; cursor:pointer;">&times;</button>
                    </div>

                    <div style="margin-bottom:15px;">
                        <label style="display:block; margin-bottom:5px; color:#94a3b8; font-size:0.9rem;">Intelligence Category</label>
                        <div id="feedback-type-selector" style="display:flex; gap:10px;">
                            <button onclick="selectFeedbackType(this, 'BUG')" class="feedback-type-btn active" style="flex:1; padding:10px; border-radius:8px; border:1px solid #EF4444; background:rgba(239,68,68,0.2); color:#EF4444; cursor:pointer; font-weight:bold;">🐞 BUG</button>
                            <button onclick="selectFeedbackType(this, 'SOP')" class="feedback-type-btn" style="flex:1; padding:10px; border-radius:8px; border:1px solid #3B82F6; background:transparent; color:#3B82F6; cursor:pointer; font-weight:bold;">📜 SOP</button>
                            <button onclick="selectFeedbackType(this, 'UX')" class="feedback-type-btn" style="flex:1; padding:10px; border-radius:8px; border:1px solid #10B981; background:transparent; color:#10B981; cursor:pointer; font-weight:bold;">✨ UX</button>
                        </div>
                        <input type="hidden" id="feedback-type" value="BUG">
                    </div>

                    <div style="margin-bottom:15px;">
                        <label style="display:block; margin-bottom:5px; color:#94a3b8; font-size:0.9rem;">The Intelligence (Markdown Supported)</label>
                        <textarea id="feedback-message" rows="5" placeholder="What is the friction? How can we optimize it?" style="width:100%; background:rgba(0,0,0,0.3); border:1px solid rgba(16,185,129,0.1); border-radius:8px; padding:10px; color:white; resize:vertical; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;"></textarea>
                    </div>

                    <div style="background: rgba(16, 185, 129, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 20px; border: 1px dashed #10B981;">
                        <p style="margin: 0; font-size: 0.75rem; color: #10B981; text-align: center;">💎 High-signal reports earn <strong>+10 AT</strong> after verification.</p>
                    </div>

                    <button onclick="submitFeedback()" style="width:100%; padding:14px; background:linear-gradient(135deg, #EF4444, #DC2626); border:none; border-radius:8px; color:white; font-weight:bold; cursor:pointer; text-transform: uppercase; letter-spacing: 1px;">
                        🚀 Dispatch Intelligence
                    </button>
                </div>
                `;
        document.body.appendChild(modal);
    };

    window.selectFeedbackType = function (btn, type) {
        document.querySelectorAll('.feedback-type-btn').forEach(b => {
            b.style.background = 'transparent';
            b.classList.remove('active');
        });
        btn.style.background = type === 'BUG' ? 'rgba(239,68,68,0.2)' : (type === 'FEATURE' ? 'rgba(59,130,246,0.2)' : 'rgba(16,185,129,0.2)');
        btn.classList.add('active');
        document.getElementById('feedback-type').value = type;
    };

    window.submitFeedback = function () {
        const type = document.getElementById('feedback-type').value;
        const msg = document.getElementById('feedback-message').value;

        if (!msg.trim()) {
            alert('Please enter a message.');
            return;
        }

        fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: appState.currentUser.name,
                type: type,
                message: msg
            })
        })
            .then(r => r.json())
            .then(data => {
                alert('✅ Feedback submitted! Thank you.');
                document.getElementById('feedback-modal').remove();
            })
            .catch(e => alert("Error sending feedback. Try later."));
    };

    window.uploadProof = function (questId) {
        if (!appState.currentUser || appState.currentUser.name === 'Guest') {
            alert("🔒 Sovereign Identity required to claim quest bounties. Please login first.");
            return;
        }

        let input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*,video/*,application/pdf';
        input.onchange = e => {
            let file = e.target.files[0];
            if (!file) return;

            let formData = new FormData();
            formData.append('file', file);
            formData.append('quest_id', questId);
            formData.append('username', appState.currentUser.name);

            logToTerminal(`[UPLINK] Uploading proof for quest: ${questId}`);

            fetch('/api/quest/upload-proof', {
                method: 'POST',
                headers: { 'Authorization': 'Bearer ' + (appState.token || '') },
                body: formData
            }).then(r => r.json()).then(data => {
                if (data.status === 'success') {
                    const xpGain = 150;
                    const atReward = data.reward || 0;

                    showCelebration(`PROOFS ACCEPTED! +${atReward} AT earned!`);
                    showXPFloat(xpGain);

                    appState.xp += xpGain;
                    appState.balance += atReward;

                    saveState();
                    updateUI();
                    syncWithLedger();

                    logToTerminal(`[SUCCESS] Quest verified. Bounty: ${atReward} AT. Hash: ${data.hash.substring(0, 10)}`);
                } else {
                    alert("Upload Failed: " + data.message);
                }
            }).catch(err => alert("Upload Error: " + err));
        };
        input.click();
    };

    // --- SYSTEM DIAGNOSTIC (LOGO CLICK) ---
    window.runDiagnostic = function () {
        const logo = document.getElementById('main-logo');
        if (logo) {
            logo.classList.add('pulse-active');
            setTimeout(() => logo.classList.remove('pulse-active'), 500);
        }

        logToTerminal("[SYSTEM] Initiating sovereign health audit...");

        // Play diagnostic sound
        if (window.playSound) window.playSound('boot');

        setTimeout(() => {
            const health = {
                ledger: appState.ledger.length > 0 ? "STABLE" : "INIT",
                network: navigator.onLine ? "CONNECTED" : "OFFLINE",
                identity: appState.token ? "SECURE" : "UNSET",
                steward: "ACTIVE"
            };

            logToTerminal(`[DIAGNOSTIC] ${health.ledger} | 🌐 ${health.network} | 🔑 ${health.identity} | 🤖 ${health.steward}`);

            if (health.identity === 'UNSET') {
                logToTerminal("⚠️ WARNING: Identity not set. Sovereignty at risk.");
            } else {
                logToTerminal("✅ SYSTEM OPTIMAL. Advance the Mission.");
            }
        }, 1000);
    };

    // --- GAIA MISSION GUIDE (Animated Helper) ---
    window.onboardingSteps = [
        { id: 'auth', title: '🔐 Establish Identity', desc: 'Create your sovereign wallet', view: 'auth', check: () => appState.token != null },
        { id: 'jobs', title: '📋 Claim your first Quest', desc: 'Accept a task from the board', view: 'jobs', check: () => appState.tasks && appState.tasks.some(t => t.worker === appState.currentUser?.name || t.assignee === appState.currentUser?.name) },
        { id: 'submit', title: '📤 Submit Proof of Work', desc: 'Upload evidence of completion', view: 'jobs', check: () => appState.history && appState.history.some(h => h.type === 'QUEST_UPDATE' && h.data?.status === 'PENDING_VALIDATION') },
        { id: 'mint', title: '⚡ Earn your first AT', desc: 'Get validated and receive tokens', view: 'wallet', check: () => appState.balance > 0 },
        { id: 'techtree', title: '🧬 Unlock Technology', desc: 'Spend XP on the Tech Tree', view: 'techtree', check: () => appState.xp > 50 }
    ];

    window.openOnboarding = function () {
        const overlay = document.getElementById('onboarding-overlay');
        const modal = document.getElementById('onboarding-modal');
        const container = document.getElementById('onboarding-steps-container');

        if (!overlay || !modal || !container) return;

        overlay.style.display = 'block';
        modal.style.display = 'block';

        let completeCount = 0;
        container.innerHTML = window.onboardingSteps.map(step => {
            const isComplete = step.check();
            if (isComplete) completeCount++;
            return `
                <div class="onboarding-step ${isComplete ? 'complete' : ''}" onclick="window.switchView('${step.view}'); window.closeOnboarding();">
                    <div class="step-check">${isComplete ? '✅' : '○'}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: ${isComplete ? 'var(--primary-light)' : 'var(--text-main)'}">${step.title}</div>
                    </div>
                    <div style="font-size: 1rem; opacity: 0.5;">→</div>
                </div>
            `;
        }).join('');

        const progressPct = (completeCount / window.onboardingSteps.length) * 100;
        const progressFill = document.getElementById('onboarding-progress-fill');
        if (progressFill) progressFill.style.width = progressPct + '%';
    };

    window.closeOnboarding = function () {
        const overlay = document.getElementById('onboarding-overlay');
        const modal = document.getElementById('onboarding-modal');
        if (overlay) overlay.style.display = 'none';
        if (modal) modal.style.display = 'none';
    };

    // --- WIKI SYNC LOGIC ---
    window.triggerWikiSync = function () {
        const btn = document.getElementById('wiki-sync-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '⏳ Syncing...';
        btn.disabled = true;

        apiFetch('/api/wiki/sync', { method: 'POST' })
            .then(data => {
                logToTerminal(`[WIKI] ${data.message}`);
                // Refresh status after a short delay
                setTimeout(updateWikiStatus, 2000);
            })
            .catch(e => {
                logToTerminal(`[WIKI] Error: ${e.message}`, 'error');
                btn.innerHTML = originalText;
                btn.disabled = false;
            });
    };

    function updateWikiStatus() {
        const statusEl = document.getElementById('wiki-sync-status');
        const btn = document.getElementById('wiki-sync-btn');
        if (!statusEl) return;

        apiFetch('/api/wiki/status')
            .then(data => {
                if (data.status === 'ONLINE' || data.status === 'SYNCED') {
                    statusEl.innerHTML = `Last sync: ${data.timestamp} (${data.message})`;
                    if (btn) {
                        btn.innerHTML = '🔄 Force Wiki Sync';
                        btn.disabled = false;
                    }
                } else if (data.status === 'SYNCING') {
                    statusEl.innerHTML = `Sync in progress...`;
                    if (btn) btn.innerHTML = '⏳ Syncing...';
                } else if (data.status === 'ERROR') {
                    statusEl.innerHTML = `⚠️ Sync Failed: ${data.message}`;
                    if (btn) {
                        btn.innerHTML = '🔄 Retry Wiki Sync';
                        btn.disabled = false;
                    }
                }
            })
            .catch(e => console.warn('Failed to fetch wiki status:', e));
    }

    // Set up polling for wiki status every 30 seconds
    setInterval(updateWikiStatus, 30000);
    setTimeout(updateWikiStatus, 5000); // Initial check

    function initGaiaGuide() {
        if (document.getElementById('gaia-guide')) return;
        const guide = document.createElement('div');
        guide.id = 'gaia-guide';
        guide.style = `
            position: fixed; bottom: 20px; right: 20px; z-index: 1000;
            width: 50px; height: 50px; background: var(--primary);
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            cursor: pointer; box-shadow: 0 0 20px var(--primary_glow);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            font-size: 24px; animation: pulse 2s infinite;
            `;
        guide.innerHTML = '🌍';
        guide.title = "Mission Guide";
        guide.onclick = (e) => {
            window.openOnboarding();
            e.stopPropagation();
        };

        document.body.appendChild(guide);
    }

    // --- EXPOSE TO WINDOW SCOPE FOR CROSS-FILE ACCESS ---
    window.appState = appState;
    window.updateUI = updateUI;
    window.renderWalletUI = renderWalletUI;
    window.updateWallet = renderWalletUI;
    window.renderJobBoard = renderJobBoard;
    window.renderTechTree = renderTechTree;
    window.renderLeaderboard = renderLeaderboard;
    window.initGaiaGuide = initGaiaGuide; // FIX: Ensure it's reachable

    // --- EVOLUTION VIEW ---
    window.renderEvolutionUI = function () {
        const container = document.getElementById('achievements-container');
        if (!container) return;

        const userAchievements = appState.achievements || [];

        container.innerHTML = Object.entries(ACHIEVEMENTS).map(([id, ach]) => {
            const unlocked = userAchievements.includes(id);
            return `
                <div class="glass-panel" style="opacity: ${unlocked ? 1 : 0.4}; border-color: ${unlocked ? 'var(--primary)' : 'var(--glass-border)'}; filter: ${unlocked ? 'none' : 'grayscale(100%)'}; position: relative;">
                    ${unlocked ? '' : '<div style="position:absolute; top:10px; right:15px; font-size: 0.7rem; color:var(--text-muted);">🔒 LOCKED</div>'}
                    <div style="font-size: 32px; margin-bottom: 15px;">${ach.name.split(' ')[0]}</div>
                    <div style="font-weight: 800; color: var(--primary-light);">${ach.name}</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 5px;">${ach.desc}</div>
                    <div style="margin-top: 15px; display: flex; gap: 8px;">
                        <span class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--primary);">+${ach.at_reward} AT</span>
                        <span class="badge" style="background: rgba(139, 92, 246, 0.1); color: var(--secondary);">+${ach.xp_reward} XP</span>
                    </div>
                </div>
                `;
        }).join('');

        if (window.renderDailyQuests) window.renderDailyQuests();
    };

    window.renderBuildDeckUI = function () {
        const swarmsContainer = document.getElementById('truck-swarms-container');
        const criticalTasksContainer = document.getElementById('truck-critical-tasks');
        if (!swarmsContainer || !criticalTasksContainer) return;

        const truckQuests = appState.tasks.filter(t => t.quest_id && t.quest_id.startsWith('xm_'));
        const swarms = ["CHASSIS", "DRIVETRAIN", "SYSTEMS", "BODY"];

        // Calculate Completion
        const completedQuests = appState.history.filter(h => h.task.startsWith('QUEST: xm_')).length;
        const totalQuests = truckQuests.length || 1;
        const pct = Math.round((completedQuests / totalQuests) * 100);

        const pctEl = document.getElementById('truck-completion-pct');
        const barEl = document.getElementById('truck-completion-bar');
        if (pctEl) pctEl.innerText = pct + '%';
        if (barEl) barEl.style.width = pct + '%';

        // Render Swarm Cards
        swarmsContainer.innerHTML = swarms.map(swarm => {
            const swarmQuests = truckQuests.filter(q => q.swarm === swarm);
            const done = swarmQuests.filter(q => appState.history.some(h => h.task.includes(q.title))).length;
            const total = swarmQuests.length || 1;
            const swarmPct = Math.round((done / total) * 100);

            return `
                <div class="glass-panel" style="padding: 20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin: 0; color: var(--primary-light);">${swarm}</h3>
                        <span style="color:var(--primary); font-weight:bold;">${swarmPct}%</span>
                    </div>
                    <div style="height: 4px; background: rgba(16,185,129,0.05); border-radius: 2px; margin: 10px 0;">
                        <div style="width: ${swarmPct}%; height:100%; background: var(--primary); box-shadow: 0 0 10px var(--primary_glow);"></div>
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">${done} / ${total} Tasks Complete</div>
                </div>
                `;
        }).join('');

        // Render Critical Path
        const openCritical = truckQuests.filter(t => t.status === 'OPEN').slice(0, 5);
        criticalTasksContainer.innerHTML = openCritical.map(t => `
                <div class="glass-panel" style="margin-bottom: 10px; display:flex; justify-content:space-between; align-items:center; border-left: 3px solid #F59E0B;">
                    <div>
                        <div style="font-weight: bold; color: var(--primary-light);">${t.icon} ${t.title}</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">${t.description}</div>
                    </div>
                    <button onclick="window.uploadProof('${t.quest_id}')" class="btn btn-primary" style="padding: 8px 16px;">UPLOAD PROOF</button>
                </div>
                `).join('') || '<div style="color:var(--text-muted); text-align:center;">All critical paths cleared! 🏁</div>';

        // Render FBCC Team Leaderboard
        renderFBCCLeaderboard();
        renderFBCCMilestones();
    };

    // FBCC Team Leaderboard Renderer
    window.renderFBCCLeaderboard = function () {
        const container = document.getElementById('fbcc-leaderboard');
        const totalAtEl = document.getElementById('leaderboard-total-at');
        const updateTimeEl = document.getElementById('leaderboard-update-time');
        if (!container) return;

        const swarms = ["CHASSIS", "DRIVETRAIN", "SYSTEMS", "BODY"];
        const swarmIcons = { CHASSIS: "🛠️", DRIVETRAIN: "⚙️", SYSTEMS: "⚡", BODY: "🎨" };
        const swarmColors = { CHASSIS: "#F59E0B", DRIVETRAIN: "#10B981", SYSTEMS: "#3B82F6", BODY: "#8B5CF6" };

        // Calculate AT per swarm from ledger
        const swarmData = swarms.map(swarm => {
            const swarmLabor = appState.history.filter(h =>
                h.task.includes(swarm) && (h.type === 'LABOR' || h.type === 'XP')
            );
            const totalAT = swarmLabor.reduce((sum, h) => sum + (h.at || h.xp || 0), 0);
            const memberCount = new Set(swarmLabor.map(h => h.user)).size || 1;
            const hourlyRate = swarmLabor.length > 0 ? Math.round(totalAT / Math.max(memberCount, 1)) : 0;

            return {
                name: swarm,
                icon: swarmIcons[swarm],
                color: swarmColors[swarm],
                totalAT: totalAT,
                members: memberCount,
                hourlyRate: hourlyRate
            };
        });

        // Sort by total AT
        swarmData.sort((a, b) => b.totalAT - a.totalAT);

        // Add rank
        swarmData.forEach((team, i) => team.rank = i + 1);

        // Calculate grand total
        const grandTotal = swarmData.reduce((sum, t) => sum + t.totalAT, 0);
        if (totalAtEl) totalAtEl.textContent = grandTotal.toLocaleString();
        if (updateTimeEl) updateTimeEl.textContent = 'Updated ' + new Date().toLocaleTimeString();

        // Render
        container.innerHTML = swarmData.map((team, i) => `
            <div style="display: flex; align-items: center; gap: 15px; padding: 12px 16px; background: ${i === 0 ? 'rgba(245,158,11,0.08)' : 'rgba(16,185,129,0.03)'}; border-radius: 10px; border-left: 4px solid ${team.color}; transition: transform 0.2s;">
                <div style="width: 32px; height: 32px; background: ${team.color}20; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">
                    ${i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : team.icon}
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: bold; color: var(--primary-light);">${team.icon} ${team.name}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">${team.members} member${team.members > 1 ? 's' : ''} • ~${team.hourlyRate} AT/member</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.3rem; font-weight: bold; color: ${team.color};">${team.totalAT.toLocaleString()}</div>
                    <div style="font-size: 0.7rem; color: var(--text-muted);">AT</div>
                </div>
            </div>
        `).join('');
    };

    // FBCC Milestones Renderer
    window.renderFBCCMilestones = function () {
        const container = document.getElementById('fbcc-milestones');
        if (!container) return;

        const milestones = [
            { id: 'frame', name: 'Frame Complete', icon: '🏗️', targetDate: 'Day 3', completed: false },
            { id: 'drivetrain', name: 'Drivetrain Installed', icon: '⚙️', targetDate: 'Day 7', completed: false },
            { id: 'electrical', name: 'Electrical Done', icon: '⚡', targetDate: 'Day 12', completed: false },
            { id: 'body', name: 'Body Mounted', icon: '🚗', targetDate: 'Day 16', completed: false },
            { id: 'paint', name: 'Paint & Finish', icon: '🎨', targetDate: 'Day 19', completed: false },
            { id: 'qc', name: 'QC Passed', icon: '✅', targetDate: 'Day 21', completed: false }
        ];

        // Check completion from history
        milestones.forEach(m => {
            m.completed = appState.history.some(h =>
                h.task && h.task.toLowerCase().includes(m.id)
            );
        });

        container.innerHTML = milestones.map((m, i) => {
            const status = m.completed ? 'completed' : (i === 0 || milestones[i - 1]?.completed) ? 'active' : 'locked';
            const bgColor = status === 'completed' ? 'rgba(16,185,129,0.15)' :
                status === 'active' ? 'rgba(245,158,11,0.15)' : 'rgba(100,116,139,0.1)';
            const borderColor = status === 'completed' ? '#10B981' :
                status === 'active' ? '#F59E0B' : '#64748b';
            const textColor = status === 'locked' ? 'var(--text-muted)' : 'var(--primary-light)';

            return `
                <div style="padding: 10px 16px; background: ${bgColor}; border: 1px solid ${borderColor}; border-radius: 20px; display: flex; align-items: center; gap: 8px; opacity: ${status === 'locked' ? '0.5' : '1'};">
                    <span style="font-size: 1.1rem;">${status === 'completed' ? '✅' : status === 'active' ? '⏳' : '🔒'}</span>
                    <span style="color: ${textColor}; font-size: 0.85rem; font-weight: ${status === 'active' ? 'bold' : 'normal'};">${m.name}</span>
                    <span style="font-size: 0.7rem; color: var(--text-muted);">${m.targetDate}</span>
                </div>
            `;
        }).join('');
    };

    window.refreshLeaderboard = function () {
        renderFBCCLeaderboard();
        renderFBCCMilestones();
        const btn = event?.target;
        if (btn) {
            btn.textContent = '✓ Refreshed';
            setTimeout(() => btn.textContent = '🔄 Refresh', 1500);
        }
    };

    window.syncWithLedger = syncWithLedger;
    window.saveState = saveState;
    window.logToTerminal = logToTerminal;

    // Hook for switchView to refresh data
    window.onViewSwitch = function (viewName) {
        if (viewName === 'wallet') {
            updateWallet();
        }
        if (viewName === 'jobs') {
            renderJobBoard();
        }
        if (viewName === 'techtree') {
            renderTechTree(appState.xp);
        }
        if (viewName === 'leaderboard') {
            renderLeaderboard();
        }
        if (viewName === 'evolution') {
            renderEvolutionUI();
        }
        if (viewName === 'builddeck') {
            renderBuildDeckUI();
        }
        if (viewName === 'treasury') {
            renderTreasuryUI();
        }
        if (viewName === 'oracle_deck') {
            window.switchOracleTab('queue');
        }



        if (viewName === 'store' && window.renderMyceliumStore) {
            window.renderMyceliumStore();
        }
        if (viewName === 'map' && window.renderCosmicMap) {
            window.renderCosmicMap();
        }
        if (viewName === 'bounties' && window.renderBountyBoard) {
            window.renderBountyBoard();
        }
        if (viewName === 'steward' && window.renderStewardChat) {
            window.renderStewardChat();
        }
        if (viewName === 'hardware' && window.initHardwareMonitor) {
            window.initHardwareMonitor();
        }
    };

    // --- NAVIGATION & ROUTING ---
    window.toggleSidebar = function () {
        const sidebar = document.querySelector('.civ-sidebar');
        if (sidebar) sidebar.classList.toggle('open');
    };

    window.switchView = function (viewName) {
        console.log("[NAV] Switching to:", viewName);

        // Update hash
        if (window.location.hash !== '#view-' + viewName) {
            window.location.hash = 'view-' + viewName;
        }

        // Hide all views
        document.querySelectorAll('.app-view').forEach(el => el.style.display = 'none');

        // Show target container
        const target = document.getElementById('view-' + viewName);
        if (target) {
            target.style.display = (viewName === 'tangle') ? 'flex' : 'block';

            // Zen Flow: Trigger fade-in animation
            target.classList.remove('view-fade-in');
            void target.offsetWidth; // Force reflow
            target.classList.add('view-fade-in');

            // Human-Centric Scroll: Reset to top on switch
            const mainContent = document.querySelector('.civ-content');
            if (mainContent) mainContent.scrollTop = 0;
        } else {
            console.warn(`[NAV] View container 'view-${viewName}' not found in DOM.`);
        }

        // --- MODULE SPECIFIC INITIALIZATION ---

        switch (viewName) {
            case 'dashboard':
                if (window.updateDashboardStats) window.updateDashboardStats();
                break;
            case 'jobs':
                if (window.renderJobBoard) window.renderJobBoard();
                break;
            case 'bounties':
                if (window.renderBountyBoard) window.renderBountyBoard();
                break;
            case 'wallet':
                if (window.renderWalletUI) window.renderWalletUI();
                break;
            case 'techtree':
                if (window.renderTechTree) window.renderTechTree(appState.xp);
                break;
            case 'evolution':
                if (window.renderEvolutionUI) window.renderEvolutionUI();
                break;
            case 'builddeck':
                if (window.renderBuildDeckUI) window.renderBuildDeckUI();
                break;
            case 'wiki':
                if (window.renderWikiUI) window.renderWikiUI();
                break;
            case 'chronicle':
                if (window.renderChronicle) window.renderChronicle();
                break;
            case 'leaderboard':
                if (window.renderLeaderboard) window.renderLeaderboard();
                break;
            case 'map':
                if (window.initMap) window.initMap();
                setTimeout(() => {
                    if (window.mapInstance) window.mapInstance.invalidateSize();
                }, 200);
                break;
            case 'hardware':
                if (window.initHardwareMonitor) window.initHardwareMonitor();
                break;
            case 'tangle':
                if (window.renderTrafficGraph) window.renderTrafficGraph(rawState.ledger);
                break;
            case 'steward':
                if (window.renderStewardChat) window.renderStewardChat();
                break;
            case 'store':
                if (window.renderMyceliumStore) window.renderMyceliumStore();
                break;
            case 'mobility':
                if (window.initMobilityUI) window.initMobilityUI();
                setTimeout(() => {
                    if (window.mobilityState && window.mobilityState.map) {
                        window.mobilityState.map.invalidateSize();
                    }
                }, 300);
                break;
            case 'cosmos':
                if (window.renderCosmicMesh) window.renderCosmicMesh();
                break;
            // Admin and others handled via app-view show/hide
            case 'admin':
                if (window.renderAdminDashboard) window.renderAdminDashboard();
                break;
        }

        // Call generic refresh hook if exists
        if (window.onViewSwitch) {
            window.onViewSwitch(viewName);
        }

        // Update Active Nav State
        document.querySelectorAll('.nav-item').forEach(btn => {
            if (btn.id === `btn-${viewName}`) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Close sidebar on mobile
        const sidebar = document.querySelector('.civ-sidebar');
        if (window.innerWidth < 768 && sidebar) sidebar.classList.remove('open');
    };

    // --- TOWN SQUARE MESSAGING SYNC ---
    window.syncMessages = async function () {
        try {
            const channel = appState.currentChannel || 'general';
            const r = await fetch(`/api/messages?channel=${channel}`);
            const msgs = await r.json();
            const logEl = document.getElementById('terminal-log');
            if (logEl && Array.isArray(msgs)) {
                logEl.innerHTML = msgs.map(m => `
                    <div style="margin-bottom:8px; border-left: 2px solid ${m.channel === 'general' ? '#10B981' : '#8B5CF6'}; padding-left: 8px;">
                        <span style="color:#64748b; font-size:0.7rem;">[${new Date(m.timestamp * 1000).toLocaleTimeString()}]</span>
                        <strong style="color:var(--primary-light);">${m.sender}:</strong>
                        <span style="color:var(--text-main);">${m.content}</span>
                    </div>
                `).join('');
                logEl.scrollTop = logEl.scrollHeight;
            }
        } catch (e) {
            console.warn("[MESSAGES] Sync failed:", e);
        }
    };

    window.sendChat = async function () {
        const input = document.getElementById('chat-input');
        const content = input.value.trim();
        if (!content) return;

        try {
            const r = await fetch('/api/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + (window.appState.token || '')
                },
                body: JSON.stringify({
                    content,
                    channel: appState.currentChannel || 'general'
                })
            });
            const data = await r.json();
            if (data.status === 'success') {
                input.value = '';
                window.syncMessages();
            }
        } catch (e) {
            console.error("[CHAT] Failed to send:", e);
        }
    };

    // --- COSMOS MESH VISUALIZER (D3.js) ---
    window.renderCosmosMesh = function () {
        const container = document.getElementById('project-tree');
        if (!container) return;

        // Clear previous
        container.innerHTML = '';
        const width = container.clientWidth;
        const height = container.clientHeight || 500;

        const svg = d3.select("#project-tree")
            .append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", `0 0 ${width} ${height}`);

        // Mock data for federation nodes
        const nodes = [
            { id: "Ark-01 (Local)", group: 1, val: 20 },
            { id: "Factor e Farm", group: 2, val: 15 },
            { id: "OSE Europe", group: 2, val: 12 },
            { id: "Luna-Core", group: 3, val: 8 },
            { id: "Mars-Sovereign", group: 3, val: 10 }
        ];

        const links = [
            { source: "Ark-01 (Local)", target: "Factor e Farm" },
            { source: "Ark-01 (Local)", target: "OSE Europe" },
            { source: "Factor e Farm", target: "OSE Europe" },
            { source: "Ark-01 (Local)", target: "Luna-Core" },
            { source: "Luna-Core", target: "Mars-Sovereign" }
        ];

        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
            .attr("stroke", "rgba(16, 185, 129, 0.2)")
            .selectAll("line")
            .data(links)
            .join("line");

        const node = svg.append("g")
            .selectAll("g")
            .data(nodes)
            .join("g");

        node.append("circle")
            .attr("r", d => d.val)
            .attr("fill", d => d.group === 1 ? "var(--primary)" : "rgba(16, 185, 129, 0.3)")
            .attr("stroke", "var(--primary)")
            .attr("stroke-width", 2)
            .style("filter", "drop-shadow(0 0 10px var(--primary-glow))");

        node.append("text")
            .text(d => d.id)
            .attr("x", 0)
            .attr("y", d => d.val + 15)
            .attr("text-anchor", "middle")
            .attr("fill", "var(--text-main)")
            .style("font-size", "10px")
            .style("font-family", "JetBrains Mono");

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("transform", d => `translate(${d.x},${d.y})`);
        });

        // Add pulse animation
        svg.selectAll("circle")
            .append("animate")
            .attr("attributeName", "r")
            .attr("values", d => `${d.val};${d.val + 2};${d.val}`)
            .attr("dur", "2s")
            .attr("repeatCount", "indefinite");
    };

    // Initialize block counter interval for Town Square
    setInterval(() => {
        fetch('/api/graph').then(r => r.json()).then(d => {
            const el = document.getElementById('dash-block-count');
            if (el) el.innerText = d.length;
        }).catch(e => {
            console.warn("[TEL] Heartbeat sync failed.");
        });

        window.syncMessages(); // Also sync messages
    }, 5000);

    // --- MYCELIUM STORE LOGIC ---

    // --- WIKI UI ---
    window.renderWikiUI = function () {
        const container = document.getElementById('wiki-container');
        if (!container) return;

        container.innerHTML = `
            <div style="display:flex; flex-direction:column; height:100%;">
                <div style="margin-bottom:20px;">
                    <input type="text" id="wiki-search" class="input-dark" placeholder="Search knowledge..." style="width:100%; border:1px solid rgba(16,185,129,0.2);" oninput="window.searchWiki(this.value)">
                </div>
                <div id="wiki-results" style="flex:1; overflow-y:auto; display:grid; grid-template-columns:1fr 1fr; gap:15px;">
                    ${window.wikiCategories.map(cat => `
                        <div class="glass-panel" style="border-top: 3px solid ${cat.color};">
                            <h3 style="color:${cat.color}; display:flex; gap:10px; align-items:center;">${cat.icon} ${cat.name}</h3>
                            <div style="margin-top:10px; display:flex; flex-direction:column; gap:8px;">
                                ${cat.pages.map(page => `
                                    <div onclick="window.openWiki('${page.path}')" style="cursor:pointer; padding:8px; border-radius:6px; background:rgba(255,255,255,0.03); transition:all 0.2s;" onmouseover="this.style.background='rgba(16,185,129,0.05)'" onmouseout="this.style.background='rgba(255,255,255,0.03)'">
                                        <div style="font-weight:bold; font-size:0.9rem; color:var(--text-main);">${page.label}</div>
                                        <div style="font-size:0.75rem; color:#94a3b8;">${page.desc}</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    window.searchWiki = function (q) {
        if (!q) return renderWikiUI();
        const resultsEl = document.getElementById('wiki-results');
        apiFetch('/api/wiki/search?q=' + encodeURIComponent(q)).then(data => {
            resultsEl.innerHTML = data.map(res => `
                <div class="glass-panel" style="cursor:pointer;" onclick="window.openWiki('${res.path}')">
                    <div style="font-weight:bold; color:var(--primary-light);">${res.label}</div>
                    <div style="font-size:0.75rem; color:#64748b;">${res.path}</div>
                </div>
            `).join('') || '<div style="grid-column: 1/-1; text-align:center; color:#64748b;">No matching documents found.</div>';
        });
    }

    window.openWiki = function (path) {
        window.open('https://wiki.opensourceecology.org/wiki/User:Seeker/Abundance_Token/SOPs', '_blank');
        logToTerminal(`[WIKI] Accessing document: ${path}`);
    }

    // --- STEWARD CHAT (Modularized) ---

    // --- HARDWARE TELEMETRY VIEW ---
    window.initHardwareMonitor = function () {
        const container = document.getElementById('hardware-monitor-container');
        if (!container) return;

        apiFetch('/api/evolution').then(data => {
            const sensors = data.sensors || {};
            container.innerHTML = `
                <div class="grid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap:20px;">
                    ${Object.entries(sensors).map(([id, s]) => `
                        <div class="glass-panel" style="position:relative;">
                            <div style="position:absolute; top:15px; right:15px; color:${s.status === 'ONLINE' ? '#10B981' : '#EF4444'}; font-size:0.6rem; letter-spacing:1px; font-weight:bold;">${s.status}</div>
                            <h4 style="margin:0 0 15px 0; color:var(--text-muted); font-size:0.8rem; letter-spacing:1px;">${s.type.toUpperCase()} NODE</h4>
                            <div style="font-size:2rem; font-weight:bold; color:var(--text-main); font-family:'JetBrains Mono';">${s.last_value}</div>
                            <div style="font-size:0.7rem; color:#64748b; margin-top:10px;">UID: ${id}</div>
                            <div style="margin-top:15px; height:4px; background:rgba(255,255,255,0.05); border-radius:2px; overflow:hidden;">
                                <div style="height:100%; background:var(--primary); width:70%; opacity:0.3; animation:pulse 2s infinite;"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        });
    }

    window.toggleListingForm = function () {
        var el = document.getElementById('listing-form-container');
        if (el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
    };

    window.submitListing = function () {
        var title = document.getElementById('list-title').value;
        var desc = document.getElementById('list-desc').value;
        var price = document.getElementById('list-price').value;
        var image = document.getElementById('list-image').value;

        if (!title || !price) return alert("Title & Price required.");

        apiFetch('/api/store/create', { // h_store_create maps to /api/store/create
            method: 'POST',
            body: { title, description: desc, price_at: price, image_emoji: image }
        }).then(r => {
            logToTerminal(`[MARKET] Listed: ${title}`);
            window.renderMyceliumStore();
            window.toggleListingForm();
        }).catch(e => {
            console.error("[MARKET] Listing failed:", e);
            alert("⚠️ Asset publishing failed.");
        });
    };

    window.buyItem = function (id) {
        if (!confirm("Confirm acquisition. Release AT?")) return;

        apiFetch('/api/store/buy', {
            method: 'POST',
            body: { item_id: id }
        }).then(r => {
            showCelebration("CORE SECURED");
            logToTerminal(`[STORE] Purchased item ${id}`);
            syncWithLedger();
            renderMyceliumStore();
        }).catch(e => alert(e.message));
    };


    // --- INITIALIZATION SEQUENCE ---
    async function initializeSystem() {
        console.log('[GAIA] Civilization OS Initializing...');
        try {
            // 1. Core Data
            initGaia();
            await loadState();

            // 2. Network Sync
            syncWithLedger();

            // 3. UI Modules
            updateUI();
            initGaiaGuide();

            // 4. Restore Pending Swap
            if (appState.pendingSwap) {
                const now = Date.now();
                const timeout = 3600 * 1000; // 1 hour timeout
                if (now - appState.pendingSwap.timestamp < timeout) {
                    console.log("[EXCHANGE] Restoring pending swap...");
                    renderExchangeUI();
                    showLightningInvoice(appState.pendingSwap.invoice, appState.pendingSwap.hash, appState.pendingSwap.amount);
                } else {
                    console.log("[EXCHANGE] Pending swap expired.");
                    appState.pendingSwap = null;
                    localStorage.removeItem('at_pending_swap');
                }
            }

            // Engagement System Init
            if (window.renderDailyQuests) renderDailyQuests();
            if (window.updateStreak) updateStreak();

            logToTerminal('System Online. Welcome to The Village.');

            // Update Sidebar Health
            const stewardLed = document.getElementById('steward-status-led');
            if (stewardLed) {
                stewardLed.innerText = 'ACTIVE';
                stewardLed.style.color = '#10B981';
            }

            // Polling
            setInterval(syncWithLedger, 5000);

            // --- HASH ROUTING FOR PWA SHORTCUTS ---
            window.handleHash = function () {
                const hash = window.location.hash;
                if (hash) {
                    const viewName = hash.replace('#view-', '');
                    if (viewName) window.switchView(viewName);
                }
            };
            window.addEventListener('hashchange', window.handleHash);
            window.handleHash(); // Initial check
        } catch (e) {
            console.error("[GAIA] Initialization Failed:", e);
            logToTerminal("⚠️ Critical Boot Failure. Check Console.");
            updateUI(); // Try to show at least something
        }
    }

    // --- SEND AT (P2P TRANFERS) ---
    window.renderSendModal = function () {
        const container = document.getElementById('send-modal-container');
        if (!container) return;

        container.style.pointerEvents = 'auto';
        container.innerHTML = `
            <div class="exchange-modal glass-panel" style="border-color: var(--primary);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h2 style="margin:0; color:var(--primary-light);">↗ Send AT</h2>
                    <button onclick="window.closeSendModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.5rem; cursor:pointer;">&times;</button>
                </div>
                
                <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:20px;">Transfer Abundance Tokens to another villager.</p>
                
                <div class="form-group">
                    <label>Recipient Username</label>
                    <input type="text" id="send-recipient" placeholder="Enter username..." class="input-dark">
                </div>
                
                <div class="form-group">
                    <label>Amount (AT)</label>
                    <input type="number" id="send-amount" value="1.0" min="0.01" step="0.01" class="input-dark">
                </div>
                
                <div style="margin-top:20px;">
                    <button onclick="window.sendAT()" class="btn-primary" style="width:100%;">
                        CONFIRM TRANSFER
                    </button>
                </div>
            </div>
        `;
    };

    window.closeSendModal = function () {
        const container = document.getElementById('send-modal-container');
        if (container) {
            container.innerHTML = '';
            container.style.pointerEvents = 'none';
        }
    };

    // --- CODE MINT MODAL ---
    window.renderCodeMintModal = function () {
        const container = document.getElementById('send-modal-container'); // Reuse same container
        if (!container) return;

        container.style.pointerEvents = 'auto';
        container.innerHTML = `
            <div class="exchange-modal glass-panel" style="border-color: #6366F1; max-width: 500px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h2 style="margin:0; color:#818CF8;">💻 Code Contribution</h2>
                    <button onclick="window.closeSendModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.5rem; cursor:pointer;">&times;</button>
                </div>
                
                <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:20px;">
                    Manually claim AT for local code work, architectural designs, or documentation.
                </p>
                
                <div class="form-group">
                    <label>Task / Description</label>
                    <input type="text" id="mint-code-desc" placeholder="e.g. Optimized ledger indexing" class="input-dark">
                </div>
                
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                    <div class="form-group">
                        <label>Lines Changed (Est.)</label>
                        <input type="number" id="mint-code-lines" value="50" min="1" class="input-dark">
                    </div>
                    <div class="form-group">
                        <label>Complexity</label>
                        <select id="mint-code-complexity" class="input-dark" style="width:100%; padding:8px; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:var(--primary-light);">
                            <option value="trivial">Trivial (0.5x)</option>
                            <option value="standard" selected>Standard (1.0x)</option>
                            <option value="complex">Complex (2.0x)</option>
                            <option value="expert">Expert (3.0x)</option>
                        </select>
                    </div>
                </div>

                <div class="form-group" style="margin-top:10px;">
                    <label>Proof URL / Commit (Optional)</label>
                    <input type="text" id="mint-code-proof" placeholder="https://github.com/... or commit hash" class="input-dark">
                </div>
                
                <div style="margin-top:20px;">
                    <button id="btn-submit-code-mint" onclick="window.submitCodeMint()" class="btn-primary" style="width:100%; background:#6366F1;">
                        SUBMIT CONTRIBUTION
                    </button>
                </div>
            </div>
        `;
    };

    window.submitCodeMint = async function () {
        const desc = document.getElementById('mint-code-desc').value.trim();
        const lines = parseInt(document.getElementById('mint-code-lines').value);
        const complexity = document.getElementById('mint-code-complexity').value;
        const proof = document.getElementById('mint-code-proof').value.trim();

        if (!desc) return alert("Task description required.");
        if (isNaN(lines) || lines <= 0) return alert("Valid lines count required.");

        const btn = document.getElementById('btn-submit-code-mint');
        btn.disabled = true;
        btn.innerText = "MINTING...";

        try {
            const res = await apiFetch('/api/mint/code', {
                method: 'POST',
                body: {
                    description: desc,
                    lines_changed: lines,
                    complexity: complexity,
                    commit_hash: proof.length === 40 ? proof : "", // Crude commit vs URL check
                    pr_url: proof.startsWith('http') ? proof : ""
                }
            });

            if (res.hash) {
                logToTerminal(`[CODE] Successfully minted contribution. Reward: ${res.reward.toFixed(2)} AT`);
                window.closeSendModal();
                if (window.syncWithLedger) await window.syncWithLedger();
                alert(`Contribution Recorded! You earned ${res.reward.toFixed(2)} AT.`);
            } else {
                alert("Minting failed: " + res.message);
                btn.disabled = false;
                btn.innerText = "SUBMIT CONTRIBUTION";
            }
        } catch (e) {
            alert("Error: " + e.message);
            btn.disabled = false;
            btn.innerText = "SUBMIT CONTRIBUTION";
        }
    };

    // --- ORACLE DECK LOGIC ---
    // --- ORACLE DECK LOGIC ---
    window.switchOracleTab = function (tab) {
        document.querySelectorAll('.oracle-tab').forEach(t => t.style.display = 'none');
        document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));

        const target = document.getElementById(`oracle-tab-${tab}`);
        if (target) target.style.display = 'block';

        const btn = document.getElementById(`tab-btn-${tab}`);
        if (btn) btn.classList.add('active');

        if (tab === 'queue') renderOracleDeck();
        if (tab === 'citizens') renderCitizenList();
    };

    function renderOracleDeck() {
        const container = document.getElementById('oracle-pending-list');
        if (!container) return;

        apiFetch('/api/quests?status=PENDING_VALIDATION')
            .then(quests => {
                if (quests.length === 0) {
                    container.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">Reality is in sync. No pending tasks.</div>`;
                    return;
                }

                container.innerHTML = quests.map(q => {
                    const auditScore = q.proof?.audit_score || 0;
                    const isHighQuality = auditScore > 0.8;

                    return `
                        <div class="glass-panel" style="border-left:4px solid ${isHighQuality ? '#10B981' : '#FBBF24'}; padding:20px;">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                                <div>
                                    <h4 style="margin:0;">${q.title}</h4>
                                    <p style="font-size:0.8rem; color:var(--text-muted); margin-top:5px;">
                                        Worker: <strong>${q.worker}</strong> | 
                                        Reward: <strong>${q.agreed_at || q.base_at} AT</strong>
                                    </p>
                                </div>
                                <div style="text-align:right;">
                                    <div class="badge" style="background:rgba(251,191,36,0.1); color:#FBBF24; border:1px solid #FBBF24;">PENDING</div>
                                    ${auditScore ? `<div style="font-size:0.75rem; color:#10B981; margin-top:5px;">Audit: ${Math.round(auditScore * 100)}%</div>` : ''}
                                </div>
                            </div>
                            <div style="margin-top:15px; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px; font-size:0.85rem;">
                                <strong>Proof:</strong> ${JSON.stringify(q.proof || q.description)}
                            </div>
                            <div style="margin-top:20px; display:flex; gap:10px;">
                                <button class="btn-primary" onclick="window.validateProof('${q.quest_id}', true)" style="flex:1; background:#10B981;">✅ VALIDATE</button>
                                <button class="btn-secondary" onclick="window.validateProof('${q.quest_id}', false)" style="flex:1; border-color:#EF4444; color:#EF4444;">❌ REJECT</button>
                            </div>
                        </div>
                    `;
                }).join('');
            });
    }

    window.batchValidate = function () {
        if (!confirm("Approve all high-quality (Audit Score > 80%) pending proofs?")) return;
        apiFetch('/api/quests?status=PENDING_VALIDATION').then(quests => {
            const targets = quests.filter(q => (q.proof?.audit_score || 0) > 0.8);
            if (targets.length === 0) {
                alert("No high-quality items found in queue.");
                return;
            }
            Promise.all(targets.map(q =>
                apiFetch('/api/quests/validate', { method: 'POST', body: { quest_id: q.quest_id, approved: true, feedback: "Batch approved by Oracle high-trust flow." } })
            )).then(() => {
                logToTerminal(`[ORACLE] Batch validated ${targets.length} items.`);
                renderOracleDeck();
            });
        });
    };

    window.defineRole = function () {
        const role = document.getElementById('new-role-name').value.trim().toUpperCase();
        const mult = document.getElementById('new-role-mult').value;
        if (!role) return alert("Role name required");

        apiFetch('/api/roles/define', {
            method: 'POST',
            body: { role: role, multiplier: mult }
        }).then(res => {
            if (res.status === 'defined') {
                logToTerminal(`[ORACLE] New role ${role} (${mult}x) minted on ledger.`);
                alert(`Role ${role} defined! Citizens can now be certified for this role.`);
                document.getElementById('new-role-name').value = '';
            }
        });
    };

    window.renderCitizenList = function () {
        const container = document.getElementById('citizen-list');
        if (!container) return;

        apiFetch('/api/users').then(users => {
            container.innerHTML = Object.entries(users).map(([username, data]) => {
                const hours = data.verified_hours || 0;
                const tier = hours >= 500 ? '🏛️ Master' : (hours >= 100 ? '🛠️ Journeyman' : '🌱 Apprentice');
                const grade = data.safety_grade || 100;

                return `
                    <div class="glass-panel" style="padding:15px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="font-weight:700;">${username}</div>
                            <div style="font-size:0.7rem; padding:2px 6px; background:rgba(0,0,0,0.3); border-radius:4px;">${tier}</div>
                        </div>
                        <div style="margin-top:10px; font-size:0.85rem;">
                            <div style="display:flex; justify-content:space-between; color:var(--text-muted);">
                                <span>Verified Hours:</span>
                                <span>${hours.toFixed(1)}h</span>
                            </div>
                            <div style="display:flex; justify-content:space-between; margin-top:5px;">
                                <span>Safety Grade:</span>
                                <span style="color:${grade > 80 ? '#10B981' : '#FBBF24'}">${grade}%</span>
                            </div>
                        </div>
                        <div style="margin-top:10px; display:flex; flex-wrap:wrap; gap:5px;">
                            ${(data.roles || ['WORKER']).map(r => `<span style="font-size:0.6rem; padding:2px 5px; background:rgba(255,255,255,0.05); border-radius:3px;">${r}</span>`).join('')}
                        </div>
                    </div>
                `;
            }).join('');
        });
    };


    window.validateProof = function (questId, approved) {
        const feedback = prompt(approved ? "Feedback for worker (optional):" : "Reason for rejection:");
        if (!approved && !feedback) return;

        apiFetch('/api/quests/validate', {
            method: 'POST',
            body: { quest_id: questId, approved: approved, feedback: feedback }
        }).then(res => {
            if (res.status === 'completed' || res.status === 'rejected') {
                logToTerminal(`[ORACLE] Quest ${questId} ${approved ? 'Validated' : 'Rejected'}.`);
                renderOracleDeck();
            } else {
                alert("Validation failed: " + res.message);
            }
        });
    };

    window.certifyUser = function () {
        const username = document.getElementById('certify-username').value.trim();
        const role = document.getElementById('certify-role').value;
        if (!username) return alert("Username required.");

        apiFetch('/api/roles/certify', {
            method: 'POST',
            body: { username: username, role: role, level: 1 }
        }).then(res => {
            if (res.status === 'certified') {
                logToTerminal(`[ORACLE] Certified ${username} as ${role}.`);
                alert(`${username} is now a certified ${role}!`);
                document.getElementById('certify-username').value = '';
            } else {
                alert("Certification failed: " + res.message);
            }
        });
    };



    window.sendAT = async function () {
        const recipient = document.getElementById('send-recipient').value.trim();
        const amount = parseFloat(document.getElementById('send-amount').value);

        if (!recipient) return alert("Recipient required.");
        if (isNaN(amount) || amount <= 0) return alert("Invalid amount.");
        if (amount > appState.balance) return alert("Insufficient balance.");

        try {
            const res = await apiFetch('/api/wallet/send', {
                method: 'POST',
                body: { recipient: recipient, amount: amount }
            });

            if (res.status === 'success') {
                window.notifyUser(`Sent ${amount} AT to ${recipient}`, 'success');
                window.closeSendModal();
                syncWithLedger();
                if (window.playSound) window.playSound('success');
            } else {
                alert(res.message || "Transfer failed.");
            }
        } catch (e) {
            console.error("[WALLET] Send failed:", e);
            alert("Network error. Is the server online?");
        }
    };

    // --- LIGHTNING BRIDGE (BTC ↔ AT EXCHANGE) ---
    window.renderExchangeUI = async function () {
        const container = document.getElementById('exchange-modal-container');
        if (!container) return;

        container.style.pointerEvents = 'auto';

        // If we have a pending swap, show it instead of the quote form
        if (appState.pendingSwap) {
            container.innerHTML = `
                <div class="exchange-modal glass-panel" style="border-color: var(--secondary);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                        <h2 style="margin:0; color:var(--secondary-light);">⚡ Active Swap</h2>
                        <button onclick="window.closeExchangeModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.5rem; cursor:pointer;">&times;</button>
                    </div>
                    <div id="exchange-flow-step"></div>
                    <div style="margin-top:15px; text-align:center;">
                        <button class="btn-xs" style="background:rgba(239, 68, 68, 0.1); color:#EF4444; border:1px solid rgba(239, 68, 68, 0.2);" onclick="window.cancelPendingSwap()">Cancel Swap</button>
                    </div>
                </div>
            `;
            window.showLightningInvoice(appState.pendingSwap.invoice, appState.pendingSwap.hash, appState.pendingSwap.amount);
            return;
        }

        container.innerHTML = `
            <div class="exchange-modal glass-panel" style="border-color: var(--secondary);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h2 style="margin:0; color:var(--secondary-light);">⚡ Lightning Bridge</h2>
                    <button onclick="window.closeExchangeModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.5rem; cursor:pointer;">&times;</button>
                </div>
                
                <div id="exchange-flow-step">
                    <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:20px;">Convert Bitcoin (Lightning) to Abundance Tokens.</p>
                    
                    <div class="form-group">
                        <label>Buy Amount (AT)</label>
                        <input type="number" id="buy-amount" value="10" min="1" class="input-dark" oninput="window.updateExchangeQuote()">
                    </div>
                    
                    <div id="exchange-quote" style="background:rgba(139, 92, 246, 0.05); padding:15px; border-radius:12px; border:1px solid rgba(139, 92, 246, 0.1); margin-bottom:20px; transition: all 0.3s ease;">
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:var(--text-muted);">
                            <span>Current Rate:</span>
                            <span id="quote-rate-display">Fetching...</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:10px; font-weight:bold;">
                            <span>Total Due:</span>
                            <span id="quote-total" style="color:var(--secondary-light);">-- Sats</span>
                        </div>
                    </div>
                    
                    <button id="btn-generate-invoice" onclick="window.initiateLightningPurchase()" class="btn-primary" style="width:100%; background:var(--secondary); color:white; border:none; box-shadow:0 0 15px var(--secondary-glow); transition:all 0.3s;">
                        GENERATE INVOICE
                    </button>
                    
                    <div style="margin-top:15px; font-size:0.7rem; color:var(--text-dim); text-align:center;">
                        Rates update every 30s. Bridge powered by LND REST.
                    </div>
                </div>
            </div>
        `;

        // Start Price Polling
        window.updateExchangeQuote();
        if (window.pricePollingInterval) clearInterval(window.pricePollingInterval);
        window.pricePollingInterval = setInterval(window.updateExchangeQuote, 30000);
    };

    window.closeExchangeModal = function () {
        const container = document.getElementById('exchange-modal-container');
        if (container) {
            container.innerHTML = '';
            container.style.pointerEvents = 'none';
        }
        if (window.exchangePollingInterval) clearInterval(window.exchangePollingInterval);
        if (window.pricePollingInterval) clearInterval(window.pricePollingInterval);
    };

    window.cancelPendingSwap = function () {
        if (!confirm("Stop tracking this payment? This will NOT refund any sent BTC.")) return;
        appState.pendingSwap = null;
        localStorage.removeItem('at_pending_swap');
        if (window.exchangePollingInterval) clearInterval(window.exchangePollingInterval);
        window.renderExchangeUI();
    };

    window.updateExchangeQuote = async function () {
        const input = document.getElementById('buy-amount');
        if (!input) return;
        const amt = parseFloat(input.value) || 0;
        const quoteEl = document.getElementById('quote-total');
        const rateEl = document.getElementById('quote-rate-display');
        const quoteBox = document.getElementById('exchange-quote');

        if (amt <= 0) {
            if (quoteEl) quoteEl.innerText = "0 Sats";
            return;
        }

        try {
            // Subtle flash to show update
            if (quoteBox) quoteBox.style.borderColor = 'var(--secondary)';

            const res = await apiFetch(`/api/exchange/quote?amount=${amt}`);

            setTimeout(() => {
                if (quoteBox) quoteBox.style.borderColor = 'rgba(139, 92, 246, 0.1)';
            }, 500);

            if (res.sats_amount) {
                if (quoteEl) quoteEl.innerText = `${res.sats_amount.toLocaleString()} Sats`;
                if (rateEl) rateEl.innerText = `1 AT = ${Math.round(res.sats_amount / amt).toLocaleString()} Sats`;

                // Show floating preview on the button
                const btn = document.getElementById('btn-generate-invoice');
                if (btn) btn.innerHTML = `GENERATE INVOICE <span style="font-size:0.7rem; opacity:0.7; margin-left:8px;">(${res.sats_amount.toLocaleString()} Sats)</span>`;
            }
        } catch (e) {
            console.warn("[EXCHANGE] Quote failed:", e);
            if (rateEl) rateEl.innerText = "Error fetching rate";
        }
    };

    window.initiateLightningPurchase = async function () {
        const amount = parseFloat(document.getElementById('buy-amount').value);
        if (isNaN(amount) || amount <= 0) return alert("Invalid amount.");

        if (window.pricePollingInterval) clearInterval(window.pricePollingInterval);

        const flow = document.getElementById('exchange-flow-step');
        flow.innerHTML = `
            <div style="text-align:center; padding:40px;">
                <div class="logo-icon pulse-active" style="margin: 0 auto 20px; width:60px; height:60px;"></div>
                <div class="payment-status-pulse">ENGAGING LIGHTNING NODE...</div>
            </div>
        `;

        try {
            const res = await apiFetch('/api/exchange/buy', {
                method: 'POST',
                body: { amount: amount }
            });

            if (res.payment_request) {
                // Save to persistent state
                appState.pendingSwap = {
                    invoice: res.payment_request,
                    hash: res.payment_hash,
                    amount: amount,
                    timestamp: Date.now()
                };
                localStorage.setItem('at_pending_swap', JSON.stringify(appState.pendingSwap));

                window.showLightningInvoice(res.payment_request, res.payment_hash, amount);
            } else {
                alert("Failed to generate invoice. Is the node online?");
                window.renderExchangeUI();
            }
        } catch (e) {
            console.error("[EXCHANGE] Error:", e);
            alert("Bridge Communication Error.");
            window.renderExchangeUI();
        }
    };

    window.showLightningInvoice = function (invoice, hash, amount) {
        const flow = document.getElementById('exchange-flow-step');
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(invoice)}`;

        flow.innerHTML = `
            <div style="text-align:center;">
                <div class="qr-container" style="box-shadow: 0 0 30px var(--secondary-glow);">
                    <img src="${qrUrl}" alt="Lightning Invoice">
                </div>
                <div style="margin-bottom:15px; padding: 0 20px;">
                    <code style="display:block; font-size:0.6rem; color:var(--text-muted); background:rgba(0,0,0,0.4); padding:10px; border-radius:8px; max-height:45px; overflow:hidden; text-overflow:ellipsis; border: 1px solid var(--glass-border);">${invoice}</code>
                    <button class="btn-xs" style="margin-top:8px; width:100%; height:32px;" onclick="navigator.clipboard.writeText('${invoice}'); window.notifyUser('Invoice Copied', 'info')">📋 Copy Raw Invoice</button>
                </div>
                <div class="payment-status-pulse" style="margin-bottom:10px;">WAITING FOR BTC SETTLEMENT...</div>
                <div style="font-size:0.75rem; color:var(--text-muted); background:rgba(16,185,129,0.05); padding:8px; border-radius:8px; margin:0 20px;">
                    Bridge will mint <strong>${amount} AT</strong> upon confirmation.
                </div>
            </div>
        `;

        // Start Polling
        if (window.exchangePollingInterval) clearInterval(window.exchangePollingInterval);
        window.exchangePollingInterval = setInterval(() => {
            window.checkInvoiceStatus(hash, amount);
        }, 3000);
    };

    window.checkInvoiceStatus = async function (hash, amount) {
        try {
            const res = await apiFetch(`/api/exchange/status?hash=${hash}&amount=${amount}`);
            if (res.status === 'complete' || res.status === 'success') {
                clearInterval(window.exchangePollingInterval);

                // Clear pending swap
                appState.pendingSwap = null;
                localStorage.removeItem('at_pending_swap');

                window.showExchangeSuccess(amount);
                if (window.syncWithLedger) syncWithLedger();
                if (window.notifyUser) window.notifyUser(`Bridge Verified: +${amount} AT Minted`, "success", "Exchange");
            } else if (res.status === 'CANCELED' || res.status === 'EXPIRED') {
                clearInterval(window.exchangePollingInterval);
                appState.pendingSwap = null;
                localStorage.removeItem('at_pending_swap');
                alert("Lightning Invoice Expired or Canceled.");
                window.renderExchangeUI();
            }
        } catch (e) {
            console.warn("[EXCHANGE] Status sync failed:", e);
        }
    };
    window.showExchangeSuccess = function (amount) {
        const flow = document.getElementById('exchange-flow-step');
        flow.innerHTML = `
            <div style="text-align:center; padding:20px;">
                <div style="font-size:4rem; margin-bottom:20px;">✅</div>
                <h3 style="color:var(--primary);">PAYMENT SETTLED</h3>
                <p style="color:var(--text-main); font-weight:bold;">+${amount} AT Minted to your account.</p>
                <div style="margin-top:20px;">
                    <button class="btn-primary" onclick="window.closeExchangeModal()" style="width:100%;">CONTINUE</button>
                </div>
            </div>
        `;
        if (window.playSound) window.playSound('success');
    };

    initializeSystem();
} // end main

// Initialize App
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
} else {
    main();
}

/**
 * --- Ark OS Native Notifications ---
 * Displays a transient notification in the Ark UI.
 * @param {string} message - The content of the alert.
 * @param {string} type - info, warn, error, mission.
 * @param {string} title - Optional title (defaults to Antigravity).
 */
window.notifyUser = function (message, type = 'info', title = 'Antigravity') {
    const container = document.getElementById('ark-notifications');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `ark-notification ${type}`;

    notification.innerHTML = `
        <div class="ark-notification-title">${title}</div>
        <div class="ark-notification-body">${message}</div>
    `;

    container.appendChild(notification);

    // Auto-remove after animation completes
    setTimeout(() => {
        notification.remove();
    }, 5000);
};

// Log greeting to native alerts on load
window.addEventListener('load', () => {
    setTimeout(() => {
        window.notifyUser("Sovereign Protocol Active. Welcome to the Ark.", "mission", "Antigravity");
    }, 2000);
});

// ART WALK MODE TOGGLE
window.toggleArtWalkMode = function () {
    const isEnabled = document.body.classList.toggle('art-walk-mode');
    localStorage.setItem('ark_art_walk_mode', isEnabled);

    const statusEl = document.getElementById('art-walk-status');
    if (statusEl) {
        statusEl.textContent = isEnabled ? 'ON' : 'OFF';
        statusEl.style.color = isEnabled ? '#10B981' : 'rgba(255,255,255,0.6)';
    }

    // Refresh UI if in relevant views
    if (appState.currentView === 'wallet') renderWalletUI();
    if (appState.currentView === 'dashboard') updateDashboardStats();

    if (isEnabled) {
        if (window.showNotification) showNotification("ART WALK MODE: ACTIVE", "UI Optimized for mobile efficiency.", "info");
    }
};

// INITIALIZE ART WALK MODE
(function initArtWalk() {
    const saved = localStorage.getItem('ark_art_walk_mode') === 'true';
    if (saved) {
        document.body.classList.add('art-walk-mode');
        // Small delay to ensure DOM items like #art-walk-status are parsed
        setTimeout(() => {
            const statusEl = document.getElementById('art-walk-status');
            if (statusEl) {
                statusEl.textContent = 'ON';
                statusEl.style.color = '#10B981';
            }
        }, 500);
    }
})();
