# SOP: AUTO_002 - n8n Steward Blueprints

> [!TIP]
> **Mission**: These workflows represent the "Sleep-Cycle" of the OS. While the user sleeps, the Steward builds.

## 1. Workflow: The Evolutionary Loop

This loop continuously audits the Ledger and the Tech Tree to identify the next growth milestone.

```json
{
  "name": "OSE Steward: Evolutionary Loop",
  "nodes": [
    {
      "parameters": { "interval": 4, "unit": "hours" },
      "name": "Interval Trigger",
      "type": "n8n-nodes-base.cron"
    },
    {
      "parameters": { "url": "http://localhost:3000/api/evolution" },
      "name": "Audit System State",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "parameters": {
        "prompt": "Analyze the current node state: {{ $json.evolution_cycles }} cycles. Based on ROADMAP_001, propose a technical upgrade to Entropic Resistance."
      },
      "name": "Steward AI Analysis",
      "type": "n8n-nodes-base.openAi"
    },
    {
      "parameters": { "conditions": { "boolean": [ { "value1": "={{ $json.confidence > 0.8 }}", "value2": true } ] } },
      "name": "Is High Confidence?",
      "type": "n8n-nodes-base.if"
    }
  ],
  "connections": { ... }
}
```

## 2. Workflow: The Mesh Immune Response

Detects unauthorized changes or potential Sybil attacks.

1.  **Trigger**: New MINT block detected on ledger.
2.  **Logic**: Cross-reference Minter ID with **Proof of Presence** history.
3.  **Action**: If anomalous, flag for Oracle (Admin) and pause AT minting from that ID.

## 3. Workflow: Community Spore Sync

Ensures your node is contributing to the global mycelium.

1.  **Trigger**: Daily status check.
2.  **Action**: Anonymize successful "Harvest" and "Labor" blocks.
3.  **Action**: Push to Global Registry (if Gate is Open).
4.  **Reward**: Increment "Federation Mastery" XP in your Local Tech Tree.

---
*Status: STEWARD LOOPS PENDING N8N DEPLOY*
