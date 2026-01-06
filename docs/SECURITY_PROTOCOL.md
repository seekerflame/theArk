# 🔒 SECURITY PROTOCOL: SOP_SEC_001

## Absolute Rules (NEVER VIOLATE)

### 1. Secrets NEVER in Git

- API keys
- JWT secrets  
- Passwords
- Seed phrases
- Private keys

### 2. Protected Files (Always .gitignore)

```
.env
.env.*
*.key
*secret*
*.pem
credentials.json
render_api_key*
```

### 3. Pre-Commit Hook (Automatic Protection)

Script: `.git/hooks/pre-commit`

- Scans for secrets patterns
- Blocks commits with exposed keys
- Alerts immediately

### 4. Wiki Protection

- No secrets in wiki pages
- No API keys documented
- No credentials shared
- Use placeholders: `<YOUR_API_KEY>`

---

## Access Control

### Git Repository

- **Owner**: You (seekerflame)
- **Push access**: Owner only (no collaborators with write)
- **Branch protection**: Enable on `main`
- **Require reviews**: Enable for PRs

### Recommended GitHub Settings

1. Settings → Branches → Add rule for `main`
2. ✅ Require pull request reviews
3. ✅ Require status checks
4. ✅ Include administrators

### If Using Collaborators

- Fork-only contribution model
- PRs require your approval
- No direct push to main

---

## Secret Storage Hierarchy

### ✅ SAFE

- `.env.local` (gitignored)
- Environment variables (local machine)
- Render dashboard (env vars)
- 1Password/similar vault

### ❌ NEVER

- Git commits
- Wiki pages
- README files
- Discord/chat
- Code comments
- Public artifacts

---

## Emergency Response

### If Key Exposed

1. **IMMEDIATELY** revoke key in Render dashboard
2. Create new key
3. Update `.env.local`
4. Check git history (`git log -p | grep rnd_`)
5. If in history: rotate ALL keys

### Command to Check

```bash
# Check if secrets in git history
git log -p | grep -E "(rnd_|sk_|secret)" && echo "⚠️ EXPOSED" || echo "✅ Clean"
```

---

## AI Agent Rules (GAIA NEXUS)

1. NEVER log API keys
2. NEVER write keys to files except `.env*`
3. NEVER include keys in artifacts
4. NEVER display keys in output
5. Use `os.environ.get()` ONLY

---

## Verification Checklist

- [ ] `.gitignore` includes all secret patterns
- [ ] No secrets in git history
- [ ] Branch protection enabled
- [ ] Pre-commit hook installed
- [ ] `.env.local` created (local only)
- [ ] Wiki has no credentials
- [ ] All keys use environment variables

---

**Protocol Status**: ACTIVE  
**Last Updated**: 2026-01-05  
**Owner**: seekerflame  
**Enforced By**: GAIA NEXUS
