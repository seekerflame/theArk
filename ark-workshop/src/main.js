import { Workspace } from './workspace.js';

// Initialize workspace
const container = document.getElementById('canvas-container');
const workspace = new Workspace(container);

// WebSocket connection for real-time updates
let ws = null;
let reconnectInterval = null;
const WS_URL = 'ws://localhost:4004';

// Activity feed state
let currentFilter = 'all';
let eventCount = 0;
const maxFeedItems = 100;

// Quest state (will sync with task.md)
let currentXP = 650;
let targetXP = 800;
let currentLevel = 2;
let activeQuest = 'Building Ark Workshop MVP';

// Connect to WebSocket server
function connectWebSocket() {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log('✅ Connected to Ark Workshop server');
        updateHUD({ status: 'connected' });

        // Register this client
        ws.send(JSON.stringify({
            type: 'register',
            agent: 'user',
            session: 'Ark-Workshop-Build'
        }));
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleServerEvent(data);
    };

    ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
    };

    ws.onclose = () => {
        console.log('🔌 Disconnected from server, reconnecting...');
        updateHUD({ status: 'reconnecting' });

        // Attempt reconnection
        if (!reconnectInterval) {
            reconnectInterval = setInterval(() => {
                if (ws.readyState === WebSocket.CLOSED) {
                    connectWebSocket();
                } else {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }
            }, 3000);
        }
    };
}

// Handle events from server
function handleServerEvent(data) {
    switch (data.type) {
        case 'agent_activity':
            addActivityItem(data);
            animateAgent(data);
            eventCount++;
            updateHUD({ events: eventCount });
            break;

        case 'xp_gain':
            addXP(data.amount, data.reason);
            break;

        case 'quest_update':
            updateQuest(data);
            break;

        case 'agent_count':
            updateHUD({ agents: data.count });
            break;
    }
}

// Add activity to feed
function addActivityItem(data) {
    const feed = document.getElementById('activity-feed');

    // Check filter
    if (currentFilter !== 'all' && currentFilter !== data.agent) {
        return;
    }

    // Create activity item
    const item = document.createElement('div');
    item.className = 'activity-item';
    item.innerHTML = `
    <div class="activity-header">
      <span class="agent-name ${data.agent}">${formatAgentName(data.agent)}</span>
      <span class="timestamp">${formatTimestamp(data.timestamp)}</span>
    </div>
    <div class="activity-content">
      <span class="tool-name">${data.tool}</span> ${formatTarget(data.target)}
    </div>
  `;

    // Add to top of feed
    feed.insertBefore(item, feed.firstChild);

    // Limit feed items
    while (feed.children.length > maxFeedItems) {
        feed.removeChild(feed.lastChild);
    }
}

// Animate agent in 3D workspace
function animateAgent(data) {
    const { agent, tool } = data;

    // Map tools to workstations
    const toolToStation = {
        'Read': 'read',
        'Write': 'write',
        'Edit': 'edit',
        'Bash': 'terminal',
        'Search': 'search'
    };

    const station = toolToStation[tool];
    if (station) {
        const stationData = workspace.workstations.get(station);
        if (stationData) {
            workspace.moveAgent(agent, stationData.position);
            workspace.highlightWorkstation(station);
        }
    }
}

// XP system
function addXP(amount, reason) {
    currentXP += amount;

    // Check for level up
    if (currentXP >= targetXP) {
        levelUp();
    }

    updateQuestOverlay();

    // Add to activity feed
    addActivityItem({
        agent: 'system',
        tool: 'XP Gained',
        target: `+${amount} XP - ${reason}`,
        timestamp: Date.now()
    });
}

function levelUp() {
    currentLevel++;
    currentXP = currentXP - targetXP;
    targetXP = Math.floor(targetXP * 1.5); // 50% increase per level

    // Celebration animation
    celebrateLevelUp();

    addActivityItem({
        agent: 'system',
        tool: '🎉 LEVEL UP',
        target: `Level ${currentLevel} achieved!`,
        timestamp: Date.now()
    });
}

function celebrateLevelUp() {
    // Flash all zones
    workspace.agents.forEach(agent => {
        for (let i = 0; i < 3; i++) {
            setTimeout(() => {
                agent.group.children[1].material.emissiveIntensity = 1;
                setTimeout(() => {
                    agent.group.children[1].material.emissiveIntensity = 0.2;
                }, 200);
            }, i * 400);
        }
    });
}

// Update quest overlay
function updateQuestOverlay() {
    const progressBar = document.querySelector('.quest-progress-bar');
    const xpStat = document.querySelector('.quest-stat:nth-child(3)');

    const progress = (currentXP / targetXP) * 100;
    progressBar.style.width = `${progress}%`;
    xpStat.textContent = `XP: ${currentXP}/${targetXP} (Level ${currentLevel})`;
}

function updateQuest(data) {
    activeQuest = data.name;
    document.querySelector('.quest-stat:first-child strong').textContent = data.name;
    document.querySelector('.quest-stat:last-child').textContent = `Next: ${data.next}`;
}

// HUD updates
function updateHUD(updates) {
    if (updates.agents !== undefined) {
        document.getElementById('agent-count').textContent = updates.agents;
    }
    if (updates.events !== undefined) {
        document.getElementById('event-count').textContent = updates.events;
    }
    if (updates.status) {
        const sessionName = document.getElementById('session-name');
        sessionName.textContent = updates.status === 'connected'
            ? 'Ark Workshop Build'
            : 'Reconnecting...';
    }
}

// Filter controls
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentFilter = e.target.dataset.agent;
        refreshFeed();
    });
});

function refreshFeed() {
    // In full implementation, would re-query events and re-render
    // For MVP, just clear and let new events come in
    // (Could also fetch from SQLite here)
}

// Recording controls
let isRecording = true; // Auto-record by default
document.getElementById('record-btn').addEventListener('click', () => {
    isRecording = !isRecording;
    const btn = document.getElementById('record-btn');

    if (isRecording) {
        btn.classList.add('recording');
        btn.textContent = '⏺ Recording';
        ws?.send(JSON.stringify({ type: 'start_recording' }));
    } else {
        btn.classList.remove('recording');
        btn.textContent = '⏸ Paused';
        ws?.send(JSON.stringify({ type: 'stop_recording' }));
    }
});

document.getElementById('screenshot-btn').addEventListener('click', () => {
    takeScreenshot();
});

function takeScreenshot() {
    const canvas = workspace.renderer.domElement;
    canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ark-workshop-${Date.now()}.png`;
        a.click();

        addActivityItem({
            agent: 'user',
            tool: 'Screenshot',
            target: 'Workspace captured',
            timestamp: Date.now()
        });
    });
}

// Utility functions
function formatAgentName(agent) {
    const names = {
        'antigravity': 'Antigravity',
        'business-os': 'Business-OS',
        'user': 'You',
        'system': 'System'
    };
    return names[agent] || agent;
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}

function formatTarget(target) {
    if (target.length > 60) {
        return target.substring(0, 57) + '...';
    }
    return target;
}

// Simulate activity for demo (remove when hooks working)
function simulateActivity() {
    const agents = ['antigravity', 'business-os', 'user'];
    const tools = ['Read', 'Write', 'Edit', 'Bash'];
    const targets = [
        'workspace.js',
        'main.js',
        'server/index.js',
        'npm install',
        'AGENTS.md',
        'prd.json'
    ];

    setInterval(() => {
        const agent = agents[Math.floor(Math.random() * agents.length)];
        const tool = tools[Math.floor(Math.random() * tools.length)];
        const target = targets[Math.floor(Math.random() * targets.length)];

        handleServerEvent({
            type: 'agent_activity',
            agent,
            tool,
            target,
            timestamp: Date.now()
        });
    }, 3000);
}

// Initialize
connectWebSocket();
updateQuestOverlay();

// Demo mode (remove when real hooks working)
setTimeout(() => {
    if (ws?.readyState !== WebSocket.OPEN) {
        console.log('📺 Demo mode: Simulating activity');
        simulateActivity();
        updateHUD({ agents: 3, events: 0, status: 'demo' });
    }
}, 2000);

// Export for debugging
window.arkWorkshop = {
    workspace,
    addXP,
    updateQuest,
    addActivityItem
};
