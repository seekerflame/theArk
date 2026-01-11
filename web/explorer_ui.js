// Explorer (Ledger) Interface
window.Explorer = {
    render: function (targetId) {
        const container = document.getElementById(targetId || 'ledger-content');
        if (!container) return;

        container.innerHTML = `
            <div class="pip-box">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0;">LIVING LEDGER</h3>
                    <div style="font-size:0.8rem; color:var(--pip-dim);" id="explorer-stats">Loading...</div>
                </div>
                <div style="margin-top:10px; max-height:400px; overflow-y:auto;">
                    <table style="width:100%; border-collapse:collapse; font-size:0.8rem;">
                        <thead style="text-align:left; border-bottom:1px solid var(--pip-green); color:var(--pip-green);">
                            <tr>
                                <th style="padding:5px;">TYPE</th>
                                <th style="padding:5px;">HASH</th>
                                <th style="padding:5px;">FROM/TASK</th>
                                <th style="padding:5px;">VALUE</th>
                            </tr>
                        </thead>
                        <tbody id="explorer-body">
                            <tr><td colspan="4" style="text-align:center; padding:20px;">Scanning Blockchain...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <!-- Future Graph Viz Placeholder -->
            <div id="dag-viz" style="height:200px; border:1px solid var(--pip-dim); margin-top:10px; opacity:0.5; display:flex; align-items:center; justify-content:center;">
                [DAG VISUALIZATION MODULE]
            </div>
        `;

        this.loadData();
    },

    loadData: function () {
        const apiBase = ''; // Relative path
        fetch(apiBase + '/api/graph')
            .then(res => res.json())
            .then(data => {
                const blocks = Array.isArray(data) ? data.reverse() : (data.nodes || []).reverse();

                // Update Stats
                const stats = document.getElementById('explorer-stats');
                if (stats) stats.innerText = `BLOCK HEIGHT: ${blocks.length} | LATEST: ${new Date().toLocaleTimeString()}`;

                // Update Table
                const tbody = document.getElementById('explorer-body');
                if (!tbody) return;
                tbody.innerHTML = '';

                blocks.forEach(block => {
                    const tr = document.createElement('tr');
                    const data = block.data || {};
                    const type = data.block_type || 'UNKNOWN';
                    let sender = data.sender || data.task || '-';
                    // Truncate sender if too long
                    if (sender.length > 20) sender = sender.substring(0, 18) + '..';

                    let amount = data.amount ? data.amount + ' AT' : (data.hours ? data.hours + ' hrs' : '-');

                    const hashShort = block.hash.substring(0, 8);

                    const colorMap = {
                        'MINT': '#10B981',
                        'TX': '#8B5CF6',
                        'QUEST': '#F59E0B',
                        'WIKI': '#EF4444'
                    };
                    const color = colorMap[type] || '#64748B';

                    tr.innerHTML = `
                        <td style="padding:5px;"><span style="color:${color}; font-weight:bold;">${type}</span></td>
                        <td style="padding:5px; font-family:'VT323'; opacity:0.8;" title="${block.hash}">${hashShort}</td>
                        <td style="padding:5px;">${sender}</td>
                        <td style="padding:5px;">${amount}</td>
                    `;
                    // Simple click alert for now
                    tr.onclick = () => alert(JSON.stringify(block, null, 2));
                    tr.style.cursor = 'pointer';
                    tr.onmouseover = function () { this.style.background = 'rgba(255,255,255,0.1)'; };
                    tr.onmouseout = function () { this.style.background = 'transparent'; };

                    tbody.appendChild(tr);
                });
            })
            .catch(err => {
                const tbody = document.getElementById('explorer-body');
                if (tbody) tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#EF4444;">CONNECTION FAILED</td></tr>`;
            });
    }
};

window.renderExplorerUI = function () {
    Explorer.render();
};
