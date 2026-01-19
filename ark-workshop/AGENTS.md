# Ark Workshop Build Patterns

## Three.js Performance

- ALWAYS use BufferGeometry (not Geometry - deprecated)
- Hexagonal grids: CircleGeometry with 6 segments
- Keep poly count low for real-time (target: \u003c100K triangles total)
- Use instancing for repeated objects (workstations)

## WebSocket Architecture

- Port 4004 for Ark Workshop (avoid conflicts with Vibecraft 4002/4003)
- Reconnection logic essential (Claude restarts = connection drop)
- Heartbeat every 30s to detect dead connections
- Pattern: Client reconnects automatically, server persists events

## Claude Code Hooks

- Use PreToolUse/PostToolUse hooks (not just PostToolUse)
- Environment vars: TOOL_NAME, FILE_PATH, AGENT_NAME (custom)
- Gotcha: Hooks run in separate process, must be fast (\u003c100ms)
- Pattern: Hook → JSON to WebSocket → Immediate return

## Agent Identification

- Antigravity: Long-term tokens, autonomous
- Business-OS: Different workspace, separate hooks
- User: Detected by keyboard/mouse events (future)
- Pattern: Agent name from Claude workspace directory

## Session Recording

- SQLite for events (fast writes, easy queries)
- JSON export for sharing
- Video export: Canvas → WebM (future phase)
- Pattern: New session = new SQLite file for clean replays

## No Telemetry Standards

- ZERO external requests (localhost only)
- No npm packages with analytics
- Audit dependencies: ws, three (both clean)
- Pattern: \"If it phones home, we don't use it\"

## Cyberpunk Aesthetic

- Colors: Neon green (#00ff88), purple (#aa44ff), teal (#00ddff), gold (#ffaa00)
- Background: Dark (#0a0e1a gradient to #1a1e2a)
- Glows: emissive materials + point lights
- Pattern: High contrast, smooth animations, premium feel

## Integration Points

- Quest system: Read task.md for overlay
- Mermaid builder: Future - diagrams → 3D
- Git commits: Trigger celebration animations
- Everything App: Unified authentication (future)
