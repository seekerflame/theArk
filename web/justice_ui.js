// Justice Hub Interface
window.Justice = {
    render: function (targetId) {
        const container = document.getElementById(targetId || 'justice-content');
        if (!container) return;

        container.innerHTML = `
            <div class="justice-header">
                <h3 style="border:none; margin:0;">Justice <span class="highlight">Hub</span></h3>
                <div style="font-size:0.8rem; color:var(--pip-dim);">[PROTOCOL: SOVEREIGN_COURT]</div>
            </div>

            <nav class="sub-nav" style="margin-bottom:15px;">
                <div class="sub-tab active" onclick="Justice.switchTab('oracle-inbox')">INBOX</div>
                <div class="sub-tab" onclick="Justice.switchTab('report-center')">REPORT</div>
                <div class="sub-tab" onclick="Justice.switchTab('transparency-log')">LOGS</div>
            </nav>

            <!-- Oracle Inbox -->
            <div id="oracle-inbox" class="justice-tab-content active">
                <div id="verification-queue">
                    <div style="padding:15px; border:1px solid var(--pip-dim); background:rgba(16,249,111,0.05);">Scanning neural mesh for pending blocks...</div>
                </div>
                <h4 style="margin-top:20px; color:var(--pip-dim);">Moderation Queue</h4>
                <div id="moderation-queue">
                    <div style="padding:15px; border:1px solid var(--pip-dim);">No active safety violations detected.</div>
                </div>
            </div>

            <!-- Report Center -->
            <div id="report-center" class="justice-tab-content" style="display:none;">
                <div class="pip-box">
                    <p style="font-size:0.8rem; margin-bottom:15px; color:var(--pip-alert);">⚠️ Reporting deposit: 0.10 AT (Refunded if valid)</p>
                    <input type="text" id="report-content-id" placeholder="Content Hash or User ID" class="input-dark">
                    <select id="report-category" class="input-dark">
                        <option value="violence">Violence / Harm</option>
                        <option value="fraud">Fraud / Scam</option>
                        <option value="spam">Spam / Noise</option>
                        <option value="other">Other</option>
                    </select>
                    <textarea id="report-reason" placeholder="Explain the violation..." rows="3" class="input-dark" style="margin-top:5px;"></textarea>
                    <button class="btn-pip" onclick="Justice.submitReport()" style="margin-top:10px; width:100%;">Submit to Oracles</button>
                </div>
            </div>

            <!-- Transparency Log -->
            <div id="transparency-log" class="justice-tab-content" style="display:none;">
                <div id="log-list" style="max-height:300px; overflow-y:auto;">
                    <!-- Entries load here -->
                </div>
                <button class="btn-pip" onclick="Justice.loadLogs()" style="width:100%; margin-top:10px;">Refresh Logs</button>
            </div>
        `;

        this.loadQueues();
    },

    switchTab: function (tabId) {
        document.querySelectorAll('.justice-tab-content').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.sub-tab').forEach(el => el.classList.remove('active')); // Note: This might conflict with global sub-tabs if not scoped carefully.

        // Simpler activation for internal tabs
        document.getElementById(tabId).style.display = 'block';

        // Re-load data based on tab
        if (tabId === 'transparency-log') this.loadLogs();
        if (tabId === 'oracle-inbox') this.loadQueues();
    },

    loadLogs: async function () {
        const list = document.getElementById('log-list');
        if (!list) return;
        list.innerHTML = '<div class="blink">SYNCHRONIZING WITH LEDGER...</div>';
        try {
            const data = await window.apiFetch('/api/moderation/log');
            const logs = data.logs || [];
            if (logs.length === 0) {
                list.innerHTML = '<div style="opacity:0.5; padding:10px;">No governance events recorded.</div>';
                return;
            }
            list.innerHTML = logs.map(log => `
                <div style="border-left:2px solid var(--pip-dim); padding-left:10px; margin-bottom:10px;">
                    <div style="font-size:0.8rem; color:var(--pip-dim);">[${new Date(log.timestamp * 1000).toLocaleTimeString()}] ID: ${log.id}</div>
                    <div style="font-weight:bold; color:var(--pip-warning);">${log.type}</div>
                    <div style="opacity:0.8; font-family:'VT323'; font-size:0.9rem;">${JSON.stringify(log.data)}</div>
                </div>
            `).join('');
        } catch (e) {
            list.innerHTML = '<div style="color:var(--pip-alert);">⚠️ SYNC ERROR: ' + e.message + '</div>';
        }
    },

    loadQueues: async function () {
        const vQueue = document.getElementById('verification-queue');
        const mQueue = document.getElementById('moderation-queue');
        if (!vQueue || !mQueue) return;

        // 1. Verification Queue
        try {
            const vTasks = await window.apiFetch('/api/verification/pending');
            vQueue.innerHTML = vTasks && vTasks.length ? vTasks.map(task => `
                <div style="background:rgba(16,249,111,0.05); padding:10px; margin-bottom:5px; border:1px solid var(--pip-dim);">
                    <div style="font-size:0.8rem; margin-bottom:5px;">QUEST: ${task.quest_id} | DOER: ${task.doer}</div>
                    <div style="display:flex; gap:5px;">
                        <button class="btn-pip" style="flex:1; font-size:0.8rem;" onclick="Justice.verify('${task.verification_id}', true)">APPROVE</button>
                        <button class="btn-pip" style="flex:1; font-size:0.8rem; border-color:var(--pip-alert); color:var(--pip-alert);" onclick="Justice.verify('${task.verification_id}', false)">REJECT</button>
                    </div>
                </div>
            `).join('') : '<div style="opacity:0.5; padding:10px;">INBOX EMPTY. NEURAL MESH IS CLEAN.</div>';
        } catch (e) { console.warn(e); }

        // 2. Moderation Queue
        try {
            const data = await window.apiFetch('/api/moderation/queue');
            const reports = data.queue || [];
            mQueue.innerHTML = reports.length ? reports.map(task => `
                <div style="padding:10px; margin-bottom:5px; border:1px solid var(--pip-dim);">
                    <div style="font-size:0.8rem;">REPORT ID: ${task.report_id} | ${task.category}</div>
                    <div style="margin-bottom:5px;">${task.reason}</div>
                    <div style="display:flex; gap:5px;">
                        <button class="btn-pip" style="flex:1; font-size:0.8rem;" onclick="Justice.resolveReport('${task.report_id}', 'ALLOW')">ALLOW</button>
                        <button class="btn-pip" style="flex:1; font-size:0.8rem; border-color:var(--pip-alert); color:var(--pip-alert);" onclick="Justice.resolveReport('${task.report_id}', 'BLOCK')">BLOCK</button>
                    </div>
                </div>
            `).join('') : '<div style="opacity:0.5; padding:10px;">NO OUTSTANDING SAFETY REPORTS.</div>';
        } catch (e) { console.warn(e); }
    },

    verify: async function (id, approved) {
        try {
            await window.apiFetch('/api/verification/submit', {
                method: 'POST',
                body: { request_id: id, decision: approved ? 'approve' : 'reject' }
            });
            alert('VERIFICATION SUBMITTED.');
            this.loadQueues();
        } catch (e) { alert('ERROR: ' + e.message); }
    },

    submitReport: async function () {
        const content_id = document.getElementById('report-content-id').value;
        const reason = document.getElementById('report-reason').value;
        const category = document.getElementById('report-category').value;

        if (!content_id || !reason) return alert('CONTENT ID AND REASON REQUIRED.');

        try {
            await window.apiFetch('/api/moderation/report', {
                method: 'POST',
                body: { content_id, reason, category }
            });
            alert('REPORT FILED. 0.10 AT STAKED.');
            this.switchTab('transparency-log');
        } catch (e) { alert('ERROR: ' + e.message); }
    }
};

window.renderJusticeUI = function () {
    Justice.render();
};
