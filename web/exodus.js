// Project Exodus - Worldcoin to AT Migration UI
const Exodus = {
    render: function () {
        const container = document.getElementById('view-exodus');
        if (!container) return;

        container.innerHTML = `
            <div class="pip-box" style="border-color: var(--pip-alert); background: rgba(255, 0, 0, 0.05);">
                <h2 style="color: var(--pip-alert); margin-top: 0;">PROJECT EXODUS</h2>
                
                <!-- WAR ROOM: WAVE STATUS -->
                <div id="exodus-war-room" class="pip-box" style="margin-bottom: 20px; border-color: var(--pip-dim); background: rgba(0,0,0,0.4);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; font-size: 0.8rem; color: var(--pip-dim);">WAR ROOM: WAVE STATUS</h3>
                        <div id="wave-indicator" style="font-family: 'VT323'; color: var(--pip-dim);">WAVE: OFFLINE</div>
                    </div>
                    <div id="wave-details" style="font-size: 0.7rem; font-family: 'Share Tech Mono'; margin-top: 5px; color: var(--pip-dim);">
                        Pending tactical activation signal...
                    </div>
                </div>

                <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.9rem; margin-bottom: 20px;">
                    <p>> INITIATING LIBERATION PROTOCOL...</p>
                    <p>> TARGET: WORLDCOIN SYSTEM 1.0 (SURVEILLANCE)</p>
                    <p>> GOAL: CONVERT SCARCITY IDENTITY TO ABUNDANCE SOVEREIGNTY</p>
                </div>

                <div class="pip-box" style="background: rgba(0, 0, 0, 0.3); border-color: var(--pip-dim);">
                    <h3>MIGRATION GRANT: <span id="exodus-grant-display">100 AT</span></h3>
                    <p style="font-size: 0.8rem;">To claim your Liberation Grant, verify your World ID. We will use their Proof of Personhood to seed your Sovereign Identity, then discard all biometric metadata forever.</p>
                    
                    <div id="world-id-container" style="text-align: center; padding: 20px;">
                        <button class="btn-pip" id="btn-world-id-verify" onclick="Exodus.launchWorldID()">VERIFY WORLD ID</button>
                    </div>

                    <div id="exodus-status" style="margin-top: 20px; font-family: 'VT323'; color: var(--pip-green); display: none;">
                        [SYSTEM] MIGRATION PENDING...
                    </div>
                </div>

                <!-- ADMIN CONTROL: TRIGGER WAVE (Hidden if not admin) -->
                <div id="exodus-admin-panel" style="display: none; margin-top: 20px; padding: 10px; border-top: 1px dashed var(--pip-dim);">
                    <button class="btn-pip" onclick="Exodus.triggerWave()" style="width: 100%; border-color: var(--pip-alert); color: var(--pip-alert);">TRIGGER NEXT WAVE (THE NUKE)</button>
                </div>

                <div style="margin-top: 20px; font-size: 0.7rem; color: var(--pip-dim); text-align: center;">
                    "The revolution will not be televised. It will be decentralised."
                </div>
            </div>
        `;
        this.fetchWaveStatus();
    },

    fetchWaveStatus: function () {
        fetch('/api/exodus/admin/status', {
            headers: { 'Authorization': 'Bearer ' + appState.token }
        })
            .then(r => r.json())
            .then(data => {
                const indicator = document.getElementById('wave-indicator');
                const details = document.getElementById('wave-details');
                const grantDisplay = document.getElementById('exodus-grant-display');
                const adminPanel = document.getElementById('exodus-admin-panel');

                if (data.active) {
                    indicator.innerText = `WAVE: ${data.wave_id} ACTIVE`;
                    indicator.style.color = 'var(--pip-alert)';
                    details.innerText = `Deployment: ${new Date(data.timestamp * 1000).toLocaleString()} | Triggered by: ${data.triggered_by}`;
                    grantDisplay.innerText = `${data.grant_amount} AT`;
                } else {
                    indicator.innerText = "WAVE: OFFLINE";
                    indicator.style.color = 'var(--pip-dim)';
                }

                // Simple check for admin role (stored in appState if you've tracked it)
                if (appState.user && appState.user.role === 'superadmin') {
                    adminPanel.style.display = 'block';
                }
            });
    },

    triggerWave: function () {
        const wave_id = prompt("WAVE ID (e.g. 1):", "1");
        if (!wave_id) return;

        fetch('/api/exodus/admin/trigger', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + appState.token
            },
            body: JSON.stringify({
                wave_id: parseInt(wave_id),
                grant_amount: 100.0,
                active: true
            })
        })
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                this.fetchWaveStatus();
            });
    },

    launchWorldID: function () {
        const statusEl = document.getElementById('exodus-status');
        const btn = document.getElementById('btn-world-id-verify');

        statusEl.innerText = "[SYSTEM] CONNECTING TO WORLD ID ORB PROTOCOL...";
        statusEl.style.display = 'block';
        btn.disabled = true;

        // SIMULATED WORLD ID VERIFICATION
        setTimeout(() => {
            statusEl.innerText = "[SYSTEM] PROOF CAPTURED. GENERATING EXODUS NULLIFIER...";

            setTimeout(() => {
                const mockProof = "0x" + Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
                const mockNullifier = "wid_" + Math.random().toString(36).substring(7) + "_" + Date.now();

                this.submitExodus(mockProof, mockNullifier);
            }, 1500);
        }, 2000);
    },

    submitExodus: function (proof, nullifier_hash) {
        const statusEl = document.getElementById('exodus-status');

        fetch('/api/exodus/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + appState.token
            },
            body: JSON.stringify({ proof, nullifier_hash })
        })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    statusEl.innerHTML = `<span style="color: var(--pip-alert);">[LIBERATED]</span> ${data.message}`;
                    showCelebration("🕊️ EXODUS SUCCESSFUL +100 AT");
                    if (window.syncWithLedger) syncWithLedger();
                } else {
                    statusEl.innerHTML = `<span style="color: red;">[ERROR]</span> ${data.message}`;
                }
            })
            .catch(e => {
                statusEl.innerText = "[ERROR] CONNECTION FAILED.";
                console.error(e);
            });
    }
};

window.Exodus = Exodus;
