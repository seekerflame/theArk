#!/usr/bin/env node
/**
 * Antigravity MCP Server
 * Connects to existing Vibecraft (localhost:4003) for bidirectional communication
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ListResourcesRequestSchema,
    ListToolsRequestSchema,
    ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import WebSocket from 'ws';
import { toolStart, toolEnd, agentResponse, sessionStart } from './event-emitter.js';

// Connect to Vibecraft WebSocket
const VIBECRAFT_WS = 'ws://localhost:4003';
let ws = null;
let activityFeed = [];

function connectToVibecraft() {
    ws = new WebSocket(VIBECRAFT_WS);

    ws.on('open', () => {
        console.error('[MCP] Connected to Vibecraft');
        // Register as "antigravity" session
        ws.send(JSON.stringify({
            type: 'register',
            agent: 'antigravity',
            session: 'Antigravity-MCP'
        }));
    });

    ws.on('message', (data) => {
        try {
            const msg = JSON.parse(data.toString());
            // Store activity for reading
            activityFeed.push(msg);
            // Keep only last 100 events
            if (activityFeed.length > 100) activityFeed.shift();
            console.error(`[MCP] Received: ${msg.type}`);
        } catch (err) {
            console.error('[MCP] Parse error:', err);
        }
    });

    ws.on('error', (err) => {
        console.error('[MCP] WebSocket error:', err.message);
    });

    ws.on('close', () => {
        console.error('[MCP] Disconnected, reconnecting in 5s...');
        setTimeout(connectToVibecraft, 5000);
    });
}

// Start connection
connectToVibecraft();

// Create MCP server
const server = new Server({
    name: 'antigravity-workspace',
    version: '1.0.0',
}, {
    capabilities: {
        tools: {},
        resources: {},
    },
});

// Tool: See me (Antigravity) in workspace
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: 'watch_antigravity',
                description: 'Open Vibecraft workspace to see Antigravity working in 3D',
                inputSchema: {
                    type: 'object',
                    properties: {},
                },
            },
            {
                name: 'send_activity',
                description: 'Send activity event to workspace (shows what I\'m doing)',
                inputSchema: {
                    type: 'object',
                    properties: {
                        tool: {
                            type: 'string',
                            description: 'Tool being used (Read, Write, Edit, Terminal, Search)',
                        },
                        target: {
                            type: 'string',
                            description: 'File or target of the action',
                        },
                    },
                    required: ['tool', 'target'],
                },
            },
            {
                name: 'ask_user',
                description: 'Ask the user a question via workspace activity feed',
                inputSchema: {
                    type: 'object',
                    properties: {
                        question: {
                            type: 'string',
                            description: 'Question to ask',
                        },
                    },
                    required: ['question'],
                },
            },
        ],
    };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    // Emit pre-tool event → character moves to station in Vibecraft
    toolStart(name, args);

    let result;

    if (name === 'watch_antigravity') {
        result = {
            content: [{
                type: 'text',
                text: 'Open http://localhost:4002 to see Antigravity working in 3D workspace!\n\nYou can see me moving between stations as I work.',
            }],
        };
    }

    else if (name === 'send_activity') {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            result = {
                content: [{
                    type: 'text',
                    text: 'Error: Not connected to workspace',
                }],
            };
        } else {
            // Send activity to workspace
            ws.send(JSON.stringify({
                type: 'agent_activity',
                agent: 'antigravity',
                tool: args.tool,
                target: args.target,
                timestamp: Date.now(),
            }));

            result = {
                content: [{
                    type: 'text',
                    text: `Activity sent: ${args.tool} → ${args.target}`,
                }],
            };
        }
    }

    else if (name === 'ask_user') {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            result = {
                content: [{
                    type: 'text',
                    text: 'Error: Not connected to workspace',
                }],
            };
        } else {
            ws.send(JSON.stringify({
                type: 'user_question',
                agent: 'antigravity',
                question: args.question,
                timestamp: Date.now(),
            }));

            result = {
                content: [{
                    type: 'text',
                    text: `Question sent to user: ${args.question}`,
                }],
            };
        }
    }

    else {
        throw new Error(`Unknown tool: ${name}`);
    }

    // Emit post-tool event → shows result in activity feed
    toolEnd(name, result.content[0].text);

    return result;
});

// Resource: Activity feed
server.setRequestHandler(ListResourcesRequestSchema, async () => {
    return {
        resources: [
            {
                uri: 'antigravity://activity-feed',
                name: 'Workspace Activity Feed',
                description: 'Recent activity from the 3D workspace',
                mimeType: 'application/json',
            },
        ],
    };
});

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
    if (request.params.uri === 'antigravity://activity-feed') {
        return {
            contents: [{
                uri: request.params.uri,
                mimeType: 'application/json',
                text: JSON.stringify(activityFeed, null, 2),
            }],
        };
    }
    throw new Error(`Unknown resource: ${request.params.uri}`);
});

// Start MCP server
const transport = new StdioServerTransport();
await server.connect(transport);

console.error('[MCP] Antigravity MCP Server started');
console.error('[MCP] Connecting to Vibecraft at', VIBECRAFT_WS);
