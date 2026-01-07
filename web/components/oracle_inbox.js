window.loadOracleInbox = function() {
    const container = document.getElementById('oracle-inbox-container');
    if(!container) return;

    container.innerHTML = '<div class="loading-spinner">Scanning Ledger...</div>';

    window.apiFetch('/api/verification/pending')
        .then(items => {
            if(!items || items.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding:40px; color:#64748b;">All clear. No pending actions.</div>';
                return;
            }

            container.innerHTML = items.map(item => `
                <div class="inbox-card">
                    <div>
                        <div style="font-weight:bold; color:var(--primary-light); font-size:1.1rem;">${item.data.task || 'Unnamed Task'}</div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:5px;">
                            <span>👤 ${item.data.minter}</span>
                            <span style="margin:0 10px;">•</span>
                            <span>⏳ ${item.data.hours} hrs</span>
                            <span style="margin:0 10px;">•</span>
                            <span style="font-family:'JetBrains Mono';">${item.hash.substring(0, 8)}...</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button onclick="window.verifyBlock('${item.hash}', 'VALID')" class="btn-primary" style="padding:8px 20px;">✅ APPROVE</button>
                        <button onclick="window.verifyBlock('${item.hash}', 'INVALID')" class="btn-secondary" style="padding:8px 20px; color:#EF4444; border-color:rgba(239,68,68,0.3);">❌ REJECT</button>
                    </div>
                </div>
            `).join('');
        })
        .catch(e => {
            container.innerHTML = `<div style="color:#EF4444;">Error loading inbox: ${e.message}</div>`;
        });
};

window.verifyBlock = function(hash, verdict) {
    if(!confirm(`Mark block ${hash.substring(0,8)} as ${verdict}?`)) return;

    window.apiFetch('/api/verification/submit', {
        method: 'POST',
        body: { hash: hash, verdict: verdict }
    }).then(() => {
        // Refresh
        window.loadOracleInbox();
    }).catch(e => alert(e.message));
};
