import { appendFileSync } from 'fs';
import { resolve } from 'path';
import { homedir } from 'os';

// Vibecraft events file
const EVENTS_FILE = resolve(homedir(), '.vibecraft/data/events.jsonl');
const SESSION_ID = 'antigravity-session-' + Date.now();
const CWD = '/Users/eternalflame/Documents/GitHub/theArk';

/**
 * Emit event to Vibecraft
 * Events are written to ~/.vibecraft/data/events.jsonl
 * Vibecraft watches this file and updates 3D workspace
 */
function emitEvent(type, payload) {
    const event = {
        id: `${SESSION_ID}-${Date.now()}-${Math.floor(Math.random() * 100000)}`,
        timestamp: Date.now(),
        type,
        sessionId: SESSION_ID,
        cwd: CWD,
        ...payload
    };

    try {
        appendFileSync(EVENTS_FILE, JSON.stringify(event) + '\n');
    } catch (err) {
        console.error('[Event Emitter] Failed to write event:', err.message);
    }
}

/**
 * Tool events - show character moving to stations
 */
export function toolStart(tool, input) {
    emitEvent('pre_tool_use', {
        tool,
        input: { args: input }
    });
}

export function toolEnd(tool, output) {
    emitEvent('post_tool_use', {
        tool,
        output
    });
}

/**
 * User message events
 */
export function userMessage(message) {
    emitEvent('user_prompt_submit', {
        prompt: message
    });
}

/**
 * Agent response events
 */
export function agentResponse(response) {
    emitEvent('stop', {
        response,
        stopHookActive: false
    });
}

/**
 * Session start event
 */
export function sessionStart() {
    emitEvent('start', {
        agent: 'antigravity',
        session: 'Antigravity-MCP'
    });
}
