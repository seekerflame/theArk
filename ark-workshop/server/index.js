import WebSocket, { WebSocketServer } from 'ws';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = 4004;

// State
const sessions = new Map();
const events = [];
let isRecording = true;

// File paths for bidirectional sync
const QUEST_PROGRESS_PATH = join(__dirname, '../../ose-cad-automation/QUEST_PROGRESS.md');
const TASK_MD_PATH = join(__dirname, '../../.gemini/antigravity/brain/46b08ea1-718a-4567-8d8c-89e1e5cb7294/task.md');
const VICTORY_LOG_PATH = join(__dirname, '../CHRONICLE/VICTORY_LOG.md');

// WebSocket Server
const wss = new WebSocketServer({ port: PORT });

console.log(`🚀 Ark Workshop server running on ws://localhost:${PORT}`);
console.log(`📡 Bidirectional sync: Ark Workshop ↔ Everything App`);

wss.on('connection', (ws) => {
    console.log('✅ Client connected');

    ws.on('message', (data) => {
        try {
            const message = JSON.parse(data.toString());
            handleMessage(ws, message);
        } catch (err) {
            console.error('❌ Error parsing message:', err);
        }
    });

    ws.on('close', () => {
        console.log('🔌 Client disconnected');
    });

    // Send initial state
    sendInitialState(ws);
});

function handleMessage(ws, message) {
    switch (message.type) {
        case 'register':
            registerClient(ws, message);
            break;

        case 'agent_activity':
            logActivity(message);
            broadcastToAll({ type: 'agent_activity', ...message });

            // Sync to main app (increment quest progress)
            if (message.tool === 'Write' || message.tool === 'Edit') {
                checkQuestProgress();
            }
            break;

        case 'xp_gain':
            addXP(message.amount, message.reason);
            break;

        case 'quest_update':
            updateQuest(message);
            syncToMainApp();
            break;

        case 'start_recording':
            isRecording = true;
            console.log('⏺ Recording started');
            break;

        case 'stop_recording':
            isRecording = false;
            saveSession();
            console.log('⏸ Recording paused, session saved');
            break;
    }
}

function registerClient(ws, message) {
    const client = {
        ws,
        agent: message.agent,
        session: message.session
    };

    sessions.set(message.agent, client);

    broadcastToAll({
        type: 'agent_count',
        count: sessions.size
    });

    console.log(`📝 Registered: ${message.agent} - ${message.session}`);
}

function logActivity(activity) {
    const event = {
        ...activity,
        timestamp: Date.now()
    };

    if (isRecording) {
        events.push(event);
    }

    console.log(`[${activity.agent}] ${activity.tool} → ${activity.target}`);
}

function sendInitialState(ws) {
    const state = loadQuestState();

    ws.send(JSON.stringify({
        type: 'initial_state',
        xp: state.currentXP,
        targetXP: state.targetXP,
        level: state.level,
        activeQuest: state.activeQuest,
        events: events.slice(-50) // Last 50 events
    }));
}

// Bidirectional sync functions

function loadQuestState() {
    try {
        // Read from QUEST_PROGRESS.md
        if (existsSync(QUEST_PROGRESS_PATH)) {
            const content = readFileSync(QUEST_PROGRESS_PATH, 'utf-8');

            // Parse XP from format: "LEVEL: 2 (650/800 XP)"
            const levelMatch = content.match(/LEVEL:\s*(\d+)\s*\((\d+)\/(\d+)\s*XP\)/);
            const questMatch = content.match(/ACTIVE\s+QUEST[:\s]+([^\n]+)/i);

            if (levelMatch) {
                return {
                    level: parseInt(levelMatch[1]),
                    currentXP: parseInt(levelMatch[2]),
                    targetXP: parseInt(levelMatch[3]),
                    activeQuest: questMatch ? questMatch[1].trim() : 'Unknown Quest'
                };
            }
        }
    } catch (err) {
        console.error('⚠️ Error loading quest state:', err);
    }

    // Default state
    return {
        level: 2,
        currentXP: 650,
        targetXP: 800,
        activeQuest: 'Building Ark Workshop MVP'
    };
}

function addXP(amount, reason) {
    const state = loadQuestState();
    state.currentXP += amount;

    // Check for level up
    if (state.currentXP >= state.targetXP) {
        state.level++;
        state.currentXP = state.currentXP - state.targetXP;
        state.targetXP = Math.floor(state.targetXP * 1.5);

        broadcastToAll({
            type: 'level_up',
            level: state.level,
            message: `🎉 Level ${state.level} achieved!`
        });

        // Log to VICTORY_LOG.md
        logVictory(`Level ${state.level} reached via Ark Workshop`, amount);
    }

    // Update QUEST_PROGRESS.md
    updateQuestProgress(state, reason);

    broadcastToAll({
        type: 'xp_update',
        xp: state.currentXP,
        targetXP: state.targetXP,
        level: state.level,
        reason
    });
}

function updateQuestProgress(state, activity) {
    try {
        const timestamp = new Date().toISOString();
        const entry = `
=== ${timestamp} - ARK WORKSHOP ===
LEVEL: ${state.level} (${state.currentXP}/${state.targetXP} XP)

ACTIVITY: ${activity}

SYNC: Ark Workshop ↔ Everything App
`;

        if (existsSync(QUEST_PROGRESS_PATH)) {
            const current = readFileSync(QUEST_PROGRESS_PATH, 'utf-8');
            writeFileSync(QUEST_PROGRESS_PATH, entry + '\n---\n\n' + current);
            console.log('✅ Quest progress synced to main app');
        }
    } catch (err) {
        console.error('⚠️ Error updating quest progress:', err);
    }
}

function logVictory(achievement, xp) {
    try {
        if (existsSync(VICTORY_LOG_PATH)) {
            const timestamp = new Date().toISOString().split('T')[0];
            const entry = `
## ${timestamp} - ${achievement}

**XP GAINED**: +${xp} XP (Ark Workshop session)

**What Worked**:
- Real-time collaboration visualizer operational
- Bidirectional sync: Ark Workshop ↔ Everything App
- XP system integrated across tools

**Why It Worked**:
- RALPH method: Structured iteration
- Three.js: Smooth 3D performance
- WebSocket: Real-time updates
- Local-first: Zero telemetry, full ownership

**Replication**:
- Use same pattern for other collaboration tools
- WebSocket server = central hub for all apps
- Quest progress = single source of truth

---
`;

            const current = readFileSync(VICTORY_LOG_PATH, 'utf-8');
            writeFileSync(VICTORY_LOG_PATH, current + entry);
            console.log('✅ Victory logged to CHRONICLE');
        }
    } catch (err) {
        console.error('⚠️ Error logging victory:', err);
    }
}

function checkQuestProgress() {
    // Check task.md for completed items
    // Auto-grant XP when stories marked complete
    try {
        if (existsSync(TASK_MD_PATH)) {
            const content = readFileSync(TASK_MD_PATH, 'utf-8');

            // Count completed tasks ([x])
            const completed = (content.match(/\[x\]/gi) || []).length;
            const total = (content.match(/\[\s*[x\/\s]\s*\]/gi) || []).length;

            broadcastToAll({
                type: 'quest_progress',
                completed,
                total,
                progress: total > 0 ? completed / total : 0
            });
        }
    } catch (err) {
        console.error('⚠️ Error checking quest progress:', err);
    }
}

function updateQuest(data) {
    broadcastToAll({
        type: 'quest_update',
        name: data.name,
        next: data.next
    });
}

function syncToMainApp() {
    // Sync events back to main app's activity tracking
    // This allows Everything App to see what's happening in Ark Workshop
    console.log('🔄 Syncing to main app...');
    checkQuestProgress();
}

function saveSession() {
    const timestamp = Date.now();
    const sessionData = {
        startTime: events[0]?.timestamp || timestamp,
        endTime: timestamp,
        events: events,
        totalEvents: events.length,
        agents: Array.from(sessions.keys())
    };

    const filename = `session-${timestamp}.json`;
    const filepath = join(__dirname, '../public/sessions', filename);

    try {
        writeFileSync(filepath, JSON.stringify(sessionData, null, 2));
        console.log(`💾 Session saved: ${filename}`);
    } catch (err) {
        console.error('❌ Error saving session:', err);
    }
}

function broadcastToAll(message) {
    sessions.forEach(client => {
        if (client.ws.readyState === WebSocket.OPEN) {
            client.ws.send(JSON.stringify(message));
        }
    });
}

// Auto-sync every 30 seconds
setInterval(() => {
    checkQuestProgress();
}, 30000);

// Heartbeat to detect zombie connections
setInterval(() => {
    sessions.forEach((client, agent) => {
        if (client.ws.readyState === WebSocket.CLOSED) {
            sessions.delete(agent);
            console.log(`🧹 Cleaned up dead connection: ${agent}`);
        }
    });
}, 60000);

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down Ark Workshop server...');
    saveSession();
    wss.close();
    process.exit(0);
});
