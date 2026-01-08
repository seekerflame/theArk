# ##############################################################################

# ARK OS ENVIRONMENT CONFIGURATION (TEMPLATE)

# ##############################################################################

## Steps to Secure Your Tokens

1. Create a file named `.env` in the project root.
2. Copy the contents below into that file.
3. Replace the placeholder values with your actual tokens.

# --- TEMPLATE ---

```bash
# --- CORE SECURITY ---
# Used for JWT signing. Change this to a long random string.
JWT_SEC\
RET=GAIA_PROTO_CENTENNIAL_2026_REVOLUTION

# --- PLUGIN TOKENS ---
# Mermaid Chart API Key (Paste the token provided in chat here)
MERMAID_CHART_API_KEY=your_token_here

# Lightning Network (Optional)
LND_MACAROON_PATH=admin.macaroon

# --- EXTERNAL INTEGRATIONS ---
# If using OpenRouter for evolution engine fallbacks
OPENROUTER_API_KEY=your_openrouter_key_here

# --- NETWORK ---
PORT=3000
HOST=0.0.0.0
```

---
**Security Note:** The `.env` file is excluded from git via `.gitignore`. Never share this file.
