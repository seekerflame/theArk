/**
 * PIP-BOY ENHANCEMENTS v1.0
 * Connects Pip-Boy UI to Ark OS Core Modules
 */

// 1. Tech Tree Definitions
const TECH_TREE = [
    { id: 'ledger_base', name: 'SOVEREIGN LEDGER', threshold: 0, desc: 'Decentralized accounting established.' },
    { id: 'mint_labor', name: 'MINT PROTOCOL', threshold: 100, desc: 'Ability to track labor hours as value.' },
    { id: 'federation', name: 'MESH FEDERATION', threshold: 500, desc: 'Connect to peer nodes across the cosmos.' },
    { id: 'governance', name: 'ORACLE JUSTICE', threshold: 1500, desc: 'Validation and auditing of node actions.' },
    { id: 'mitosis', name: 'DUNBAR MITOSIS', threshold: 5000, desc: 'Scaling beyond 150 members via cellular split.' }
];

window.renderTechTree = function (currentXP) {
    const container = document.getElementById('tech-tree-content');
    if (!container) return;

    container.innerHTML = TECH_TREE.map(tech => {
        const isUnlocked = currentXP >= tech.threshold;
        return `
            <div class="tech-node ${isUnlocked ? 'unlocked' : 'locked'}">
                <div class="tech-node-header">
                    <span>${tech.name}</span>
                    <span>${isUnlocked ? '[ACTIVE]' : tech.threshold + ' XP'}</span>
                </div>
                <div class="tech-node-desc">${tech.desc}</div>
            </div>
        `;
    }).join('');
}

// 2. Radio / Chat Logic
window.sendChat = function () {
    const input = document.getElementById('chat-input');
    const content = input.value.trim();
    if (!content) return;

    const user = window.appState.currentUser.name || 'GUEST';

    // Log Activity locally
    if (window.logActivity) {
        window.logActivity('MESSAGE', user, { content: content, channel: 'BROADCAST' });
    }

    // Append to Pip-Boy Terminal
    const terminal = document.getElementById('terminal-log');
    if (terminal) {
        const entry = document.createElement('div');
        entry.style.marginBottom = '5px';
        entry.innerHTML = `<span style="color:var(--pip-dim)">[${new Date().toLocaleTimeString()}]</span> <b>${user}:</b> ${content}`;
        terminal.appendChild(entry);
        terminal.scrollTop = terminal.scrollHeight;
    }

    input.value = '';

    // Optional: Send to backend
    if (window.apiFetch) {
        window.apiFetch('/api/chat/send', {
            method: 'POST',
            body: { message: content, channel: 'general' }
        }).catch(e => console.warn("Backend chat failed, logged locally."));
    }
}

// 3. View Hook Overrides
const originalSwitchPipTab = window.switchPipTab;
window.switchPipTab = function (tabName) {
    if (originalSwitchPipTab) originalSwitchPipTab(tabName);

    // Contextual Initializations
    if (tabName === 'data') {
        window.renderTechTree(window.appState.xp || 0);
    }
    if (tabName === 'map') {
        if (window.initMobilityUI) {
            window.initMobilityUI();
        }
        // Force Leaflet resize
        setTimeout(() => {
            if (window.mobilityState && window.mobilityState.map) {
                window.mobilityState.map.invalidateSize();
            }
        }, 300);
    }
    if (tabName === 'deck') {
        if (window.renderAdminDeck) window.renderAdminDeck();
    }
    if (tabName === 'founders') {
        if (window.Founders && window.Founders.render) {
            window.Founders.render();
        }
    }
}

// 4. Founders Visibility Hook
const originalUpdateUI = window.updateUI;
window.updateUI = function () {
    if (originalUpdateUI) originalUpdateUI();
    if (window.Founders && window.Founders.updateTabVisibility) {
        window.Founders.updateTabVisibility();
    }
};

// 5. Update Stats in Real Time

setInterval(() => {
    const hpEl = document.getElementById('hp-stat');
    const lvlEl = document.getElementById('lvl-stat');
    const apEl = document.getElementById('ap-stat');

    if (hpEl) hpEl.innerText = "100/100"; // Hook to real health if added
    if (lvlEl && window.appState) {
        lvlEl.innerText = Math.floor((window.appState.xp || 0) / 1000) + 1;
    }
    if (apEl) apEl.innerText = Math.floor(Math.random() * 20) + 80 + "/100"; // Flicker for effect
}, 2000);
