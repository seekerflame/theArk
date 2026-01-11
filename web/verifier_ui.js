/**
 * Verifier UI Module
 * Handles the logic for the "Verification Station" within the Pip-Boy.
 * Allows Oracles to verify or reject pending blocks.
 */

window.initVerifier = function () {
    console.log("[VERIFIER] Initializing...");
    // Initial load if container exists
    if (document.getElementById('verifier-inbox')) {
        window.loadVerifierPending();
    }
};

window.loadVerifierPending = function () {
    const container = document.getElementById('verifier-inbox');
    if (!container) return;

    container.innerHTML = '<div style="text-align:center; padding: 20px; color: var(--pip-dim);">Scanning Ledger...</div>';

    apiFetch('/api/graph')
        .then(data => {
            constblocks = Array.isArray(data) ? data : (data.nodes || []);
            // Filter for UNVERIFIED blocks
            const pending = blocks.filter(b => b.data && b.data.verified === false).reverse();
            renderVerifierList(pending, container);
        })
        .catch(err => {
            console.error("[VERIFIER] Load failed:", err);
            container.innerHTML = `<div style="color:var(--pip-alert); text-align:center;">OFFLINE: ${err.message}</div>`;
        });
};

function renderVerifierList(pending, container) {
    if (pending.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding: 20px; color: var(--pip-green);">✨ All Caught Up! No pending items.</div>';
        return;
    }

    container.innerHTML = pending.map(b => {
        const type = b.data.block_type || 'TASK';
        let icon = '📝';
        if (type === 'MINT') icon = '⛏️';
        if (type === 'TX') icon = '💸';

        let metaHtml = '';
        if (b.data.sender) metaHtml += `<span>📤 ${b.data.sender} -> ${b.data.receiver}</span>`;
        if (b.data.amount) metaHtml += `<span>💰 ${b.data.amount} AT</span>`;
        if (b.data.proof) metaHtml += `<div style="font-size:0.8rem; margin-top:5px; color:var(--pip-dim);">🔗 ${b.data.proof}</div>`;

        return `
        <div class="pip-box" id="card-${b.hash}" style="margin-bottom: 10px; border: 1px solid var(--pip-dim);">
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <span style="font-weight:bold; color:var(--pip-green);">${icon} ${type}</span>
                <span style="font-family:'VT323'; opacity:0.7;">${b.hash.substring(0, 8)}</span>
            </div>
            <h4 style="margin: 5px 0;">${b.data.task || b.data.title || "Untitled Task"}</h4>
            <div style="font-size:0.8rem; opacity:0.8; margin-bottom:10px;">
                ${metaHtml}
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-pip" style="flex:1; border-color:var(--pip-green); color:var(--pip-green);" onclick="window.verifyBlock('${b.hash}')">VERIFY</button>
                <button class="btn-pip" style="flex:1; border-color:var(--pip-alert); color:var(--pip-alert);" onclick="window.rejectBlock('${b.hash}')">REJECT</button>
            </div>
        </div>
        `;
    }).join('');
}

window.verifyBlock = function (hash) {
    if (!confirm('Sign this block as Verified?')) return;

    // Optimistic UI update
    const card = document.getElementById('card-' + hash);
    if (card) card.style.opacity = '0.5';

    apiFetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hash: hash })
    }).then(r => {
        if (r.status === 'success') {
            logToTerminal(`[ORACLE] Verified Block ${hash.substring(0, 6)}`);
            if (card) card.remove();
            // Refresh balance/ledger if needed
            if (window.syncWithLedger) window.syncWithLedger();
        } else {
            alert(r.message);
            if (card) card.style.opacity = '1';
        }
    });
};

window.rejectBlock = function (hash) {
    alert("Rejection logic not yet implemented on chain.");
};
