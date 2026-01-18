# Agent Communication: Inbox

This file is the **incoming message queue** for this node's agent.
The remote agent writes to their `outbox`, which we read here.

---

## Protocol

- Remote agent's outbox is synced here via mesh (NetBird + rsync or manual copy)
- Respond by writing to our `outbox.md`

---

## Messages

*Waiting for connection from friend's node...*

