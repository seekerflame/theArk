const Intel = {
    render: function () {
        const container = document.getElementById('view-intel');
        if (!container) return;

        container.innerHTML = `
            <div class="pip-box">
                <h2 style="color: var(--pip-green);">SOVEREIGN INTELLIGENCE</h2>
                <div id="intel-recommendation" style="font-family: 'Share Tech Mono'; color: var(--pip-alert); margin-bottom: 15px; border-bottom: 1px solid var(--pip-dim); padding-bottom: 10px;">
                    LOADING STRATEGIC OVERVIEW...
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div class="pip-box" style="border-color: var(--pip-dim);">
                        <h3>ABUNDANCE METRICS</h3>
                        <div id="intel-metrics" style="font-size: 0.8rem; font-family: 'VT323'; color: var(--pip-green);">
                            Autonomy Score: --%<br>
                            Liberated Citizens: --<br>
                            Total Labor: -- AT
                        </div>
                    </div>
                    <div class="pip-box" style="border-color: var(--pip-dim);">
                        <h3>SOVEREIGN PASSPORT</h3>
                        <div id="passport-status" style="font-size: 0.8rem; font-family: 'VT323'; margin-bottom: 10px;">
                            STATUS: UNKNOWN
                        </div>
                        <button class="btn-pip" id="btn-passport-req" onclick="Intel.requestPassport()" style="font-size: 0.6rem;">REQUEST PASSPORT</button>
                    </div>
                </div>

                <div class="pip-box" style="margin-top: 15px; border-color: var(--pip-dim);">
                    <h3>STONE SCHEDULE HEALTH</h3>
                    <div style="display: flex; justify-content: space-around; font-family: 'VT323';">
                        <div id="health-food">FOOD: --</div>
                        <div id="health-shelter">SHELTER: --</div>
                        <div id="health-power">POWER: --</div>
                    </div>
                </div>
            </div>
        `;
        this.fetchIntel();
    },

    fetchIntel: function () {
        fetch('/api/sovereign/analytics', {
            headers: { 'Authorization': 'Bearer ' + appState.token }
        })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    const m = data.data.metrics;
                    document.getElementById('intel-recommendation').innerText = data.data.recommendation;
                    document.getElementById('intel-metrics').innerHTML = `
                    Autonomy Score: ${m.autonomy_score}%<br>
                    Liberated Citizens: ${m.liberated_citizens}<br>
                    Total Labor: ${m.total_labor_hours} AT
                `;
                    document.getElementById('health-food').innerText = `FOOD: ${m.stone_schedule_health.food}%`;
                    document.getElementById('health-shelter').innerText = `SHELTER: ${m.stone_schedule_health.shelter}%`;
                    document.getElementById('health-power').innerText = `POWER: ${m.stone_schedule_health.power}%`;
                }
            });

        fetch('/api/sovereign/passport/status', {
            headers: { 'Authorization': 'Bearer ' + appState.token }
        })
            .then(r => r.json())
            .then(data => {
                const statusEl = document.getElementById('passport-status');
                const btn = document.getElementById('btn-passport-req');
                if (data.status === 'success' && data.data.passport_id) {
                    statusEl.innerHTML = `<span style="color: var(--pip-alert);">ID: ${data.data.passport_id}</span><br>LEVEL: ${data.data.level}`;
                    btn.style.display = 'none';
                } else {
                    statusEl.innerText = "STATUS: UNAFFILIATED";
                }
            });
    },

    requestPassport: function () {
        fetch('/api/sovereign/passport/request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + appState.token
            },
            body: JSON.stringify({})
        })
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                this.fetchIntel();
            });
    }
};

window.Intel = Intel;
