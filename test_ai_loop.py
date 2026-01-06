from ai_orchestrator import GaiaNexus
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Initialize
nexus = GaiaNexus("http://localhost:3000", "test_token")

# Create a manual mission
mission = {
    'type': 'IMPROVE_CODE',
    'priority': 'HIGH',
    'reason': 'User requested imagination test'
}

# Execute
print("🚀 Triggering AI Imagination...")
success = nexus.improve_code(mission)

if success:
    print("✅ AI Cycle Successful")
else:
    print("❌ AI Cycle Failed")
