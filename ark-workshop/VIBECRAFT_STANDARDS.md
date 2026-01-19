# Vibecraft Design Standards - Reverse Engineered

## 🎨 Core Patterns Extracted

### 1. **Multi-Zone Hex Grid System**

```typescript
// From WorkshopScene.ts
- HexGrid class for zone placement (radius=10, spacing=1.0)
- Automatic spiral placement: `hexGrid.getNextInSpiral()`
- Direction-aware assignment: `findNearestFreeFromCartesian()`
- Zone elevation system (painting hexes underneath

 raises zones)
- Pending zones with loading animation (spinner + ring)
```

**Apply to Ark Workshop**: ✅ Already implemented basic zones, add hex painting elevation

### 2. **Character Animation System**

```typescript
// From Claude.ts
- States: 'idle' | 'walking' | 'working' | 'thinking'
- Smooth state transitions with color-coded status rings
- Walking: Bob animation + arm swing + face direction
- Working: Arm motion (like hammering/typing) + body bob
- Thinking: Head tilt + hand-on-chin pose + thought bubbles
- Thought bubbles: 3 sizes, float up, pulse opacity
```

**Apply to Ark Workshop**: 🔄 Implement agent character with full animation states

### 3. **Station Interaction Design**

```typescript
// From WorkshopScene.ts
- Station types: center, desk, terminal, bookshelf, antenna, scanner, workbench, taskboard
- Each station has: mesh, label, contextSprite
- Station pulses on tool usage (brief highlight glow)
- Detail functions: addDeskDetails(), addTerminalDetails(), etc.
- OrbitControls with damping (smoothness = 0.05)
```

**Apply to Ark Workshop**: ✅ Already have workstations, add detail models

### 4. **Visual Polish Standards**

```typescript
// Performance + aesthetics
- Antialias: false (for performance)
- PixelRatio: capped at 1.5 (not full retina)
- Shadow type: BasicShadowMap (fastest)
- Damping factor: 0.05 (smooth camera)
- Fog: disabled for multi-zone viewing

// Colors (ice/cyan theme)
ZONE_COLORS = [
  0x4ac8e8, // Cyan (primary)
  0x60a5fa, // Blue
  0x22d3d8, // Teal
  0x4ade80, // Green
  0xa78bfa, // Purple
  0xfbbf24, // Orange
  0xf472b6, // Pink
  0xa3e635, // Lime
]
```

**Apply to Ark Workshop**: 🔄 Update colors to match ice/cyan theme, optimize renderer

### 5. **Click Pulse Effects**

```typescript
// From WorkshopScene.ts
- Ring expands from click point
- Hex highlights with color flash
- Ripple effect with delayed animation
- Fade to baseOpacity (not to zero)
- Hover highlight with sound (pitch based on distance)
```

**Apply to Ark Workshop**: 🆕 Add click pulses and hover sound

### 6. **Notification System**

```typescript
// ZoneNotifications.ts
- Floating text above zones
- Fade in → hold → fade out
- Color-coded by event type
- Position tracks zone elevation
- Multiple notifications stack vertically
```

**Apply to Ark Workshop**: 🆕 Implement for file changes, XP gains, quest updates

### 7. **Station Panels**

```typescript
// StationPanels.ts
- Info cards appear near stations
- Show file context, line numbers
- Auto-hide when not relevant
- Smooth fade transitions
```

**Apply to Ark Workshop**: 🆕 Add for rich tool context display

---

## 🚀 Priority Implementation Order

### Story 004: Activity Feed UI (NEXT)

- [x] Real-time event display
- [x] Filter by agent
- [x] Color-coded by agent
- [ ] **Add**: File path shortened display
- [ ] **Add**: Line count for edits
- [ ] **Add**: Git status integration

### Story 005: Claude Code Hooks

- [ ] PreToolUse/PostToolUse hooks
- [ ] Extract: agent name, tool name, file path
- [ ] Send to WebSocket server
- [ ] Trigger 3D animations

### Story 006: Agent Animations

- [ ] Implement Claude character class
- [ ] States: idle, walking, working, thinking
- [ ] Thought bubbles (3 sizes, animated)
- [ ] Status ring (color-coded)
- [ ] Move to station on tool use

### Story 007: Session Recording (Already Working)

- [x] Start/stop controls
- [x] Save to JSON
- [ ] **Add**: Canvas → WebM video export
- [ ] **Add**: Timeline scrubbing UI

### Story 008: Quest Integration

- [x] Read task.md for overlay
- [x] XP progress bar
- [ ] **Add**: Level-up celebration (zone flash)
- [ ] **Add**: Quest completion confetti

### Story 009: Live Testing

- [ ] Test with real Claude Code session
- [ ] Performance: 60fps verification
- [ ] Multi-agent simultaneous testing

### Story 010: Polish + Commit

- [ ] README with setup instructions
- [ ] Screenshots for documentation
- [ ] Git commit with clear messages
- [ ] Victory log entry

---

## 💎 Key Learnings

1. **Performance First**: Disable antialiasing, cap pixel ratio, use BasicShadowMap
2. **Smooth Everything**: 0.05 damping factor, lerp camera, ease animations
3. **Color Psychology**: Status rings change color by state (green=idle, blue=walking, yellow=working, purple=thinking)
4. **Multi-Zone Architecture**: Hex grid, spiral placement, elevation system
5. **Character Personality**: Thought bubbles, head tilt, arm swing give life
6. **Sound Design**: Hover sounds with pitch variation adds immersion

---

## 🎯 Next Steps

1. **Finish Activity Feed** (Story 004)
   - File path shortening
   - Line count display
   - Git status badges

2. **Build Claude Hooks** (Story 005)
   - Shell script: `ark-hook.sh`
   - Parse tool events
   - Send to WebSocket

3. **Animate Agents** (Story 006)
   - Port Claude character class
   - Add to each zone
   - Trigger animations on events

4. **Integrate CoVe + XP**
   - CoVe workflow reads from Ark Workshop events
   - XP gains trigger zone celebrations
   - Level-ups flash all zones

---

**Status**: Patterns extracted, ready to implement remaining stories using Vibecraft standards
