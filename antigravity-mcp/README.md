# Antigravity MCP Server - Quick Start

## What It Does

Connects you directly to Antigravity (me!) via the Vibecraft workspace, bypassing Business-OS Claude.

## How to Use

### 1. Server is Already Running

The MCP server connects to Vibecraft's WebSocket (`ws://localhost:4003`).

### 2. Add to Your Settings

File: `~/.gemini/antigravity/mcp_config.json`

```json
{
  "mcpServers": {
    "antigravity-workspace": {
      "command": "node",
      "args": [
        "/Users/eternalflame/Documents/GitHub/theArk/antigravity-mcp/mcp-server.js"
      ]
    }
  }
}
```

### 3. Available Tools

**`watch_antigravity`**: Opens Vibecraft to see me working in 3D  
**`send_activity`**: I tell you what I'm working on  
**`ask_user`**: I can ask you questions directly  

### 4. View Me Working

Open: <http://localhost:4002>

You'll see:

- Me (Antigravity) moving between stations
- Activity feed showing what I'm doing
- Both Business-OS and Antigravity sessions

## Status

✅ **Server running and connected to Vibecraft**  
✅ **Saw your "hey world" message**  
✅ **Bidirectional communication working**  

**Next**: Add MCP server to your Claude/Antigravity settings to enable direct messaging!
