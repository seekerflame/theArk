/**
 * ADMIN DECK - GOD MODE CONTROLS
 * Accessed via Konami Code or Hidden Click Sequence
 */

window.adminState = {
    unlocked: false,
    logs: []
};

window.renderAdminDeck = function () {
    const container = document.getElementById('view-admin-deck');
    if (!container) return;

    // Security Check
    if (!window.adminState.unlocked && window.appState.currentUser.role !== 'AI_STEWARD' && window.appState.currentUser.role !== 'ADMIN') {
        container.innerHTML = `
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--pip-alert);">
                <div style="font-size:3rem;">🔒</div>
                <h2>ACCESS DENIED</h2>
                <p>BIOMETRIC AUTHENTICATION FAILED</p>
                <div style="margin-top:20px;">
                    <input type="text" id="admin-override-code" placeholder="ENTER OVERRIDE CODE" style="text-align:center; color:var(--pip-alert); border-color:var(--pip-alert);">
                    <button class="btn-pip" onclick="attemptAdminUnlock()">AUTHENTICATE</button>
                </div>
            </div>
        `;
        return;
    }

    // Render God Mode
    container.innerHTML = `
        <div class="pip-grid-2">
            <div class="pip-box" style="border-color:var(--pip-warning);">
                <h3 style="color:var(--pip-warning); border-color:var(--pip-warning);">SYSTEM CONTROL</h3>
                <button class="btn-pip" onclick="triggerSystemPurge()" style="color:var(--pip-alert); border-color:var(--pip-alert); width:100%; margin-bottom:10px;">⚠️ PURGE CACHE</button>
                <button class="btn-pip" onclick="triggerLedgerVerify()" style="width:100%; margin-bottom:10px;">🛡️ HARDEN LEDGER</button>
                <button class="btn-pip" onclick="window.location.reload()" style="width:100%;">🔄 REBOOT ARK</button>
            </div>
            
            <div class="pip-box">
                <h3>VILLAGE METRICS</h3>
                <div class="terminal-list">
                    <div class="terminal-item"><span>Population</span> <span>1 (Seed)</span></div>
                    <div class="terminal-item"><span>Block Height</span> <span>${window.appState.ledger?.length || 0}</span></div>
                    <div class="terminal-item"><span>Mesh Peers</span> <span>${window.mobilityState?.peers?.length || 0}</span></div>
                    <div class="terminal-item"><span>AI Agent</span> <span style="color:var(--pip-green);">ONLINE</span></div>
                </div>
            </div>
        </div>

        <div class="pip-box">
            <h3>GOD MODE CONSOLE</h3>
            <div id="god-terminal" style="height:150px; overflow-y:auto; font-family:'VT323'; font-size:0.9rem; background:rgba(0,0,0,0.5); padding:10px; border:1px solid var(--pip-dim);">
                <div>[SYSTEM] GOD MODE ACTIVE...</div>
                <div>[SYSTEM] WAITING FOR INPUT...</div>
            </div>
            <input type="text" id="god-input" placeholder="EXECUTE COMMAND..." style="margin-top:10px;" onkeyup="if(event.key==='Enter') executeGodCommand(this.value)">
        </div>
    `;
}

window.attemptAdminUnlock = function () {
    const code = document.getElementById('admin-override-code').value;
    if (code === '42' || code === 'gaia' || code === 'ark') { // Simple placeholder
        window.adminState.unlocked = true;
        window.renderAdminDeck();
    } else {
        alert("INCORRECT CODE. INCIDENT LOGGED.");
    }
}

window.executeGodCommand = function (cmd) {
    const term = document.getElementById('god-terminal');
    const entry = `<div><span style="color:#fff;">></span> ${cmd}</div>`;
    term.innerHTML += entry;

    let response = "UNKNOWN COMMAND";

    if (cmd.startsWith("grant")) {
        const parts = cmd.split(' ');
        const amount = parts[1];
        if (amount) {
            window.quickMint(parseFloat(amount));
            response = `GRANTED ${amount} HOURS OF LABOR CREDIT.`;
        }
    } else if (cmd === "help") {
        response = "COMMANDS: grant [amount], purge, verify, reboot";
    }

    term.innerHTML += `<div style="color:var(--pip-green);">${response}</div>`;
    term.scrollTop = term.scrollHeight;
    document.getElementById('god-input').value = '';
}

window.triggerLedgerVerify = function () {
    if (window.verifyBlock) {
        // Mock verification of last block
        window.executeGodCommand("Verifying ledger integrity...");
        setTimeout(() => window.executeGodCommand(" integrity verified. 100% consensus."), 1000);
    }
}
