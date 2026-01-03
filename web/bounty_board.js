/**
 * Bounty Board Module - OSE Civilization OS
 * Handles fetching, rendering, and interactions for the Community Bounty Board.
 * Modularized for reusability.
 */

window.initBountyBoard = function () {
    console.log("[BOUNTY] Initializing Board...");
    // Identify containers
    const containerOpen = document.getElementById('bounties-open');
    const containerActive = document.getElementById('bounties-active');
    const containerVerify = document.getElementById('bounties-verify');

    // If containers exist, render.
    if (containerOpen && containerActive && containerVerify) {
        window.renderBountyBoard();
    }
}

window.toggleBountyForm = function () {
    const form = document.getElementById('bounty-form');
    if (form) form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

window.renderBountyBoard = function () {
    const containerOpen = document.getElementById('bounties-open');
    const containerActive = document.getElementById('bounties-active');
    const containerVerify = document.getElementById('bounties-verify');

    if (!containerOpen || !containerActive || !containerVerify) return;

    containerOpen.innerHTML = '<div style="color:#64748b; font-size:0.8rem; padding:10px;">📡 Fetching from Mycelium...</div>';

    apiFetch('/api/bounties').then(data => {
        if (!data || !data.bounties) return;

        containerOpen.innerHTML = '';
        containerActive.innerHTML = '';
        containerVerify.innerHTML = '';

        const myName = appState.currentUser.name;
        let hasActive = false;

        data.bounties.forEach(b => {
            const card = document.createElement('div');
            card.className = 'glass-panel';
            card.style.padding = '15px';
            card.style.marginBottom = '10px';
            card.style.borderLeft = b.status === 'OPEN' ? '4px solid #10B981' : '4px solid #F59E0B';

            // OPEN BOUNTIES (Not mine)
            if (b.status === 'OPEN' && b.owner !== myName) {
                card.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:8px;">
                        <div style="font-weight:bold; color:var(--primary-light);">${b.title}</div>
                        <div style="color:#FBBF24; font-weight:bold; font-family:'JetBrains Mono'; font-size:0.9rem;">${b.reward} AT</div>
                    </div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:12px; line-height:1.4;">${b.description}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-size:0.7rem; color:#64748b;">By <span style="color:#10B981;">${b.owner}</span></div>
                        <button onclick="claimBounty('${b.id}')" class="btn-primary" style="padding:6px 12px; font-size:0.75rem;">⚡ Claim</button>
                    </div>
                `;
                containerOpen.appendChild(card);
            }

            // ACTIVE TASKS (I am worker)
            if (b.worker === myName && (b.status === 'CLAIMED' || b.status === 'SUBMITTED' || b.status === 'COMPLETED')) {
                hasActive = true;
                let actionArea = '';
                if (b.status === 'CLAIMED') {
                    actionArea = `<button onclick="submitBounty('${b.id}')" class="btn-primary" style="width:100%; margin-top:10px; background:#10B981; border:none;">📤 Submit Proof</button>`;
                } else if (b.status === 'SUBMITTED') {
                    actionArea = `<div style="margin-top:10px; font-size:0.75rem; color:#F59E0B; text-align:center; padding:8px; background:rgba(245,158,11,0.1); border-radius:6px; border:1px solid rgba(245,158,11,0.2);">⏳ Verification Pending</div>`;
                } else {
                    actionArea = `<div style="margin-top:10px; font-size:0.75rem; color:#10B981; text-align:center; padding:8px; background:rgba(16,185,129,0.1); border-radius:6px;">✅ Task Completed</div>`;
                }

                card.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:8px;">
                        <div style="font-weight:bold; color:var(--primary-light);">${b.title}</div>
                        <div style="color:#FBBF24; font-weight:bold; font-size:0.9rem;">${b.reward} AT</div>
                    </div>
                    <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:10px;">${b.description}</div>
                    ${actionArea}
                `;
                containerActive.appendChild(card);
            }

            // VERIFY QUEUE (I am owner)
            if (b.owner === myName && b.status !== 'COMPLETED') {
                let statusColor = b.status === 'SUBMITTED' ? '#F59E0B' : '#64748b';
                let verifyArea = '';

                if (b.status === 'SUBMITTED') {
                    verifyArea = `
                        <div style="margin-top:12px; padding:10px; background:rgba(0,0,0,0.3); border-radius:8px; border:1px solid rgba(245,158,11,0.3);">
                            <div style="font-size:0.75rem; color:var(--text-main); margin-bottom:8px;"><strong>Proof:</strong> "${b.proof}"</div>
                            <button onclick="verifyBounty('${b.id}')" class="btn-primary" style="width:100%; height:32px; font-size:0.8rem; background:#10B981;">💰 Release ${b.reward} AT</button>
                        </div>
                    `;
                }

                card.innerHTML = `
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-weight:bold; color:var(--primary-light);">${b.title}</span>
                        <span class="badge" style="background:rgba(16,185,129,0.05); color:${statusColor}; font-size:0.6rem;">${b.status}</span>
                    </div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">Worker: <span style="color:#60A5FA;">${b.worker || 'Searching...'}</span></div>
                    ${verifyArea}
                `;
                containerVerify.appendChild(card);
            }
        });

        if (!hasActive) containerActive.innerHTML = '<div style="color:#64748b; font-size:0.8rem; padding:10px; text-align:center;">No active tasks. Join the grid!</div>';
        if (containerOpen.children.length === 0) containerOpen.innerHTML = '<div style="color:#64748b; font-size:0.8rem; padding:10px; text-align:center;">The board is clear. Check back later!</div>';
    });
}


window.createBounty = function () {
    const title = document.getElementById('b-title').value;
    const desc = document.getElementById('b-desc').value;
    const reward = document.getElementById('b-reward').value;

    if (!title || !reward) return alert("Title and Reward required");

    apiFetch('/api/bounties/create', {
        method: 'POST',
        body: { title, description: desc, reward }
    }).then(r => {
        if (r.status === 'success') {
            logToTerminal(`[BOUNTY] Created: ${title} (${reward} AT)`);
            toggleBountyForm();
            renderBountyBoard();
        } else {
            alert(r.message);
        }
    });
}

window.claimBounty = function (id) {
    if (!confirm("Commit to this task?")) return;
    apiFetch('/api/bounties/claim', {
        method: 'POST',
        body: { id }
    }).then(r => {
        if (r.status === 'success') {
            logToTerminal(`[BOUNTY] Claimed Task`);
            renderBountyBoard();
        } else {
            alert(r.message);
        }
    });
}

window.submitBounty = function (id) {
    const proof = prompt("Describe work done (Proof):");
    if (!proof) return;

    apiFetch('/api/bounties/submit', {
        method: 'POST',
        body: { id, proof }
    }).then(r => {
        if (r.status === 'success') {
            logToTerminal(`[BOUNTY] Submitted Proof`);
            renderBountyBoard();
        } else {
            alert(r.message);
        }
    });
}

window.verifyBounty = function (id) {
    apiFetch('/api/bounties/verify', {
        method: 'POST',
        body: { id }
    }).then(r => {
        if (r.status === 'success') {
            logToTerminal(`[BOUNTY] Bounty Verified & Paid!`);
            alert("Payment Released: " + r.reward + " AT");
            renderBountyBoard();
            if (window.syncWithLedger) window.syncWithLedger();
        } else {
            alert(r.message);
        }
    });
}
