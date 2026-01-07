#!/bin/bash
# evolve_code.sh - The Executioner
# Usage: ./evolve_code.sh "Proposal Title" "Proposal Description"

TITLE=$1
DESC=$2

echo "🌀 Evolving code for: $TITLE"

# 1. Generate Code with Ollama
# We ask for a bash command or a python script to implement the idea
PROMPT="Idea: $TITLE. Context: $DESC. 
You are Antigravity's Right Brain. Generate a single bash command or python script to implement this. 
Respond ONLY with the code, no markdown, no explanation."

CODE=$(ollama run llama3 "$PROMPT")

if [ -z "$CODE" ]; then
    echo "❌ Code generation failed."
    exit 1
fi

echo "📝 Generated Code:"
echo "$CODE"

# 2. Safety Check (Dry Run or simple check)
# In a real system, we'd run this in a sandbox. 
# For this alpha, we execute and rely on git for recovery.

# 3. Apply Code
echo "$CODE" > tmp_evolution.sh
chmod +x tmp_evolution.sh
./tmp_evolution.sh

# 4. Commit and Push
git add .
git commit -m "[EVOLUTION] $TITLE 🧬"
git push

echo "✅ Evolution complete and pushed to GitHub."
rm tmp_evolution.sh
