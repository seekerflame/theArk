
// Evolution UI - Visualizing Autopoiesis

window.renderEvolution = function () {
    console.log("[UI] Rendering Evolution...");
    const container = document.getElementById('evolution-feed');
    if (!container) return;

    container.innerHTML = '<div class="terminal-item">Scanning neural pathways...</div>';

    window.apiFetch('/api/evolution/proposals')
        .then(data => {
            const proposals = data.proposals || [];
            if (proposals.length === 0) {
                container.innerHTML = '<div class="terminal-item">No active evolution vectors. System stable.</div>';
                return;
            }

            let html = '';
            proposals.reverse().forEach(p => {
                const statusColor = p.status === 'approved' ? 'var(--pip-green)' : 'var(--pip-dim)';
                const icon = p.source === 'right_brain_ollama' ? '🧠' : '👤';

                html += `
                <div class="terminal-item" style="border-left: 3px solid ${statusColor}; padding-left: 10px; margin-bottom: 10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color: ${statusColor}; font-weight:bold;">${icon} ${p.title}</span>
                        <span style="font-size:0.8rem;">${new Date(p.timestamp * 1000).toLocaleTimeString()}</span>
                    </div>
                    <div style="color: var(--pip-dim); font-size: 0.9rem; margin-top: 5px;">${p.description}</div>
                    <div style="font-size: 0.8rem; margin-top: 5px;">
                        TYPE: [${p.type.toUpperCase()}] :: IMPACT: ${p.impact}/10
                    </div>
                    ${p.logic_proof ? `<div style="font-family:'VT323'; font-size:0.8rem; margin-top:5px; color:#a855f7;">LOGIC: ${p.logic_proof}</div>` : ''}
                </div>
                `;
            });

            container.innerHTML = html;
        })
        .catch(err => {
            container.innerHTML = `<div class="terminal-item" style="color:red;">Error syncing neural link: ${err.message}</div>`;
        });
};

// Hook into tab switching
// We rely on switchPipTabHook in index.html, but let's just expose the init
window.initEvoUI = function () {
    renderEvolution();
};
