window.loadTransparencyLog = function() {
    const container = document.getElementById('transparency-log-container');
    if(!container) return;

    window.apiFetch('/api/moderation/log')
        .then(logs => {
            if(!logs || logs.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding:40px; color:#64748b;">The slate is clean.</div>';
                return;
            }

            container.innerHTML = logs.map(l => `
                <div class="log-entry">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="color:#FBBF24; font-weight:bold; font-size:0.8rem;">${l.resolution}</span>
                        <span style="font-family:'JetBrains Mono'; font-size:0.7rem; color:#64748b;">${new Date(l.resolved_at * 1000).toLocaleString()}</span>
                    </div>
                    <div style="font-size:0.9rem;">
                        Target: <strong style="color:white;">${l.target_id}</strong>
                    </div>
                    <div style="font-size:0.8rem; color:#94a3b8; margin-top:5px;">
                        Reason: ${l.reason} <br>
                        Notes: ${l.notes || 'None'}
                    </div>
                </div>
            `).join('');
        });
};
