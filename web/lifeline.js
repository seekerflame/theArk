/* Lifeline Module - Managing the Dull Moments */
const Lifeline = {
    state: {
        currentSubView: 'ops',
        data: null,
        zenActive: false,
        zenTimeLeft: 0
    },

    init: function () {
        console.log("[LIFELINE] Initializing...");
        this.fetchData();
        // Setup periodic fetch
        setInterval(() => {
            if (window.appState && window.appState.currentTab === 'life') {
                this.fetchData();
            }
        }, 5000);
    },

    fetchData: function () {
        if (!window.apiFetch) return;
        window.apiFetch('/api/lifeline/data')
            .then(data => {
                this.state.data = data;
                if (window.appState && window.appState.currentTab === 'life') {
                    this.render();
                }
            })
            .catch(e => console.error("[LIFELINE] Data fetch failed:", e));
    },

    render: function () {
        const container = document.getElementById('view-life');
        if (!container) return;

        if (!this.state.data) {
            container.innerHTML = '<div class="pip-box">Synchronizing Life Stream...</div>';
            return;
        }

        container.innerHTML = `
            <div class="life-container">
                <div class="life-tabs">
                    <div class="life-tab ${this.state.currentSubView === 'ops' ? 'active' : ''}" onclick="Lifeline.setSubView('ops')">DAILY_OPS</div>
                    <div class="life-tab ${this.state.currentSubView === 'memories' ? 'active' : ''}" onclick="Lifeline.setSubView('memories')">MEMORY_VAULT</div>
                    <div class="life-tab ${this.state.currentSubView === 'zen' ? 'active' : ''}" onclick="Lifeline.setSubView('zen')">ZEN_CYCLE</div>
                    <div class="life-tab ${this.state.currentSubView === 'favors' ? 'active' : ''}" onclick="Lifeline.setSubView('favors')">FUTURE_SELF</div>
                </div>
                <div class="life-content">
                    ${this.renderSubView()}
                </div>
            </div>
        `;
    },

    setSubView: function (view) {
        this.state.currentSubView = view;
        this.render();
    },

    renderSubView: function () {
        switch (this.state.currentSubView) {
            case 'ops': return this.renderOps();
            case 'memories': return this.renderMemories();
            case 'zen': return this.renderZen();
            case 'favors': return this.renderFavors();
            default: return this.renderOps();
        }
    },

    renderOps: function () {
        const ops = this.state.data.ops || { cleaning: [], meals: [], bills: [] };
        return `
            <div class="pip-grid-2">
                <div>
                    <h3>CLEANING_OPS</h3>
                    <div class="terminal-list">
                        ${(ops.cleaning || []).map(o => this.renderOpItem(o, 'cleaning')).join('') || '<div class="pip-stat-row">NO PENDING TASKS</div>'}
                    </div>
                </div>
                <div>
                    <h3>MEAL_PLAN</h3>
                    <div class="terminal-list">
                        ${(ops.meals || []).map(o => this.renderOpItem(o, 'meals')).join('') || '<div class="pip-stat-row">NO PENDING MEALS</div>'}
                    </div>
                </div>
            </div>
            <div style="margin-top:20px;">
                <input type="text" id="new-op-content" placeholder="DESCRIBE TASK / MEAL..." class="pip-input">
                <div class="pip-grid-2">
                    <button class="btn-pip" onclick="Lifeline.addOp('cleaning')">+ ADD_CLEANING</button>
                    <button class="btn-pip" onclick="Lifeline.addOp('meals')">+ ADD_MEAL</button>
                </div>
            </div>
        `;
    },

    renderOpItem: function (op, type) {
        return `
            <div class="life-op-item ${op.status === 'done' ? 'done' : ''}" onclick="Lifeline.toggleOp('${op.id}', '${type}')">
                <span>${op.content}</span>
                <span style="font-size:0.8rem;">[${op.status.toUpperCase()}]</span>
            </div>
        `;
    },

    renderMemories: function () {
        const memories = this.state.data.memories || [];
        const reversedMemories = [...memories].reverse();
        return `
            <h3>MEMORY_VAULT</h3>
            <div class="memory-vault">
                ${reversedMemories.map(m => `
                    <div class="pip-box" style="margin-bottom:10px; font-size:0.9rem; background:rgba(0,0,0,0.4);">
                        <div style="color:var(--pip-dim); font-size:0.7rem;">TIMESTAMP: ${new Date(m.timestamp * 1000).toLocaleString()}</div>
                        <div style="margin-top:5px;">${m.content}</div>
                    </div>
                `).join('') || '<div class="pip-box">VAULT IS EMPTY. COMMIT YOUR VICTORIES.</div>'}
            </div>
            <div style="margin-top:20px;">
                <textarea id="new-memory-content" placeholder="WHAT WAS CONQUERED TODAY?" class="pip-input"></textarea>
                <button class="btn-pip" style="width:100%; margin-top:10px;" onclick="Lifeline.addMemory()">COMMIT_TO_VAULT</button>
            </div>
        `;
    },

    renderZen: function () {
        const cycles = this.state.data.zen_cycles || 0;
        return `
            <h3>ZEN_CYCLE</h3>
            <div class="zen-display">
                <div style="font-size:0.8rem; color:var(--pip-dim); margin-bottom:10px;">STRESS_BUFFER_ACTIVE / TOTAL_CYCLES: ${cycles}</div>
                <div class="zen-timer" id="zen-timer-display">${this.formatTime(this.state.zenTimeLeft || 300)}</div>
                <div style="margin-top:20px;">
                    <button class="btn-pip" id="btn-start-zen" onclick="Lifeline.startZen()" ${this.state.zenActive ? 'disabled' : ''}>
                        ${this.state.zenActive ? 'BUFFERING...' : 'ENGAGE 5-MIN BUFFER'}
                    </button>
                </div>
            </div>
            <div class="pip-box" style="font-size:0.8rem; border-color:var(--pip-dim); color:var(--pip-dim);">
                Take 5 minutes. Decelerate. Breathe. Plan one favor for your future self. 
                Completion reinforces entropic resistance.
            </div>
        `;
    },

    renderFavors: function () {
        const favors = this.state.data.favors || [];
        return `
            <h3>FUTURE_SELF_DECKS</h3>
            <div class="favors-list">
                ${favors.map(f => `
                    <div class="favor-card">
                        <span class="favor-status">${f.status.toUpperCase()}</span>
                        <div style="font-weight:bold;">${f.content}</div>
                        <div style="font-size:0.6rem; color:var(--pip-dim); margin-top:5px;">PLANNED_ON: ${new Date(f.timestamp * 1000).toLocaleDateString()}</div>
                    </div>
                `).join('') || '<div class="pip-box">NO PENDING FAVORS. GIFT YOUR FUTURE SELF WITH ACTION.</div>'}
            </div>
            <div style="margin-top:20px;">
                <input type="text" id="new-favor-content" placeholder="A GIFT FOR YOUR FUTURE PERSONA..." class="pip-input">
                <button class="btn-pip" style="width:100%; margin-top:10px;" onclick="Lifeline.addFavor()">SCHEDULE_FAVOR</button>
            </div>
        `;
    },

    // Handlers
    addMemory: function () {
        const content = document.getElementById('new-memory-content').value;
        if (!content) return;
        window.apiFetch('/api/lifeline/memories/add', { method: 'POST', body: { content } })
            .then(() => {
                document.getElementById('new-memory-content').value = '';
                this.fetchData();
            });
    },

    addOp: function (type) {
        const content = document.getElementById('new-op-content').value;
        if (!content) return;
        window.apiFetch('/api/lifeline/ops/add', { method: 'POST', body: { type, content } })
            .then(() => {
                document.getElementById('new-op-content').value = '';
                this.fetchData();
            });
    },

    toggleOp: function (id, type) {
        window.apiFetch('/api/lifeline/ops/toggle', { method: 'POST', body: { id, type } })
            .then(() => this.fetchData());
    },

    addFavor: function () {
        const content = document.getElementById('new-favor-content').value;
        if (!content) return;
        window.apiFetch('/api/lifeline/favors/add', { method: 'POST', body: { content } })
            .then(() => {
                document.getElementById('new-favor-content').value = '';
                this.fetchData();
            });
    },

    startZen: function () {
        if (this.state.zenActive) return;
        this.state.zenActive = true;
        this.state.zenTimeLeft = 300; // 5 mins

        const btn = document.getElementById('btn-start-zen');
        if (btn) {
            btn.disabled = true;
            btn.innerText = 'BUFFERING...';
        }

        this.runZenTimer();
    },

    runZenTimer: function () {
        const timer = setInterval(() => {
            if (this.state.zenTimeLeft <= 0) {
                clearInterval(timer);
                this.state.zenActive = false;
                window.apiFetch('/api/lifeline/zen/complete', { method: 'POST' })
                    .then(() => {
                        if (window.showCelebration) window.showCelebration("🧘 ZEN CYCLE COMPLETE +XP");
                        this.fetchData();
                    });
                return;
            }

            this.state.zenTimeLeft--;
            const display = document.getElementById('zen-timer-display');
            if (display) display.innerText = this.formatTime(this.state.zenTimeLeft);
        }, 1000);
    },

    formatTime: function (s) {
        const m = Math.floor(s / 60);
        const sec = s % 60;
        return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    }
};

window.Lifeline = Lifeline;

// Chained hook for tab switching
const oldTabHook = window.switchPipTabHook;
window.switchPipTabHook = (tab) => {
    if (oldTabHook) oldTabHook(tab);
    if (tab === 'life') {
        Lifeline.render();
        Lifeline.fetchData();
    }
};

// Auto-init when script loads
Lifeline.init();
