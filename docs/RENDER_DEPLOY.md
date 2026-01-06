# Quick Deploy to Render.com Guide

**Estimated Time**: 10 minutes  
**Prerequisites**: GitHub account, Render.com account

---

## Step 1: Push to GitHub (if not already)

```bash
cd /Volumes/Extreme\ SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark

# Initialize git if needed
git init
git add .
git commit -m "Production-ready Ark with role system"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/The_Ark.git
git push -u origin main
```

---

## Step 2: Create Render Account

1. Go to <https://render.com>
2. Sign up with GitHub
3. Grant Render access to your repository

---

## Step 3: Deploy

### Option A: One-Click Deploy (render.yaml)

1. In Render dashboard: **New** → **Blueprint**
2. Connect your GitHub repo
3. Render auto-detects `render.yaml`
4. Click **Apply**
5. Done! Get your URL: `https://ark-os.onrender.com`

### Option B: Manual Deploy

1. **New** → **Web Service**
2. Connect repository
3. Configure:
   - **Name**: `ark-os`
   - **Environment**: `Python 3`
   - **Build Command**: (leave empty)
   - **Start Command**: `python3 server.py`
   - **Port**: `3001` (or use `PORT` env var)

4. Set Environment Variables:
   - `PORT`: `3001`
   - `JWT_SECRET`: (auto-generate or set custom)
   - `ARK_MOCK_EXCHANGE`: `1` (for testing)

5. Click **Create Web Service**

---

## Step 4: Verify Deployment

```bash
# Test health endpoint
curl https://ark-os.onrender.com/api/health

# Test role API
curl https://ark-os.onrender.com/api/roles

# Should return 13 roles
```

---

## Step 5: Update URLs

### GitHub Webhooks

Update webhook URLs to use Render URL:

- `https://ark-os.onrender.com/api/webhook/github-pr`

### Wiki Links

Update public URL in wiki documentation

### Demo Credentials

Share public URL + demo credentials with friends

---

## Environment Variables Reference

| Variable | Value | Purpose |
|----------|-------|---------|
| `PORT` | `3001` | Render default port |
| `JWT_SECRET` | (auto-gen) | Auth security |
| `ARK_MOCK_EXCHANGE` | `1` | Mock Lightning for testing |

For production with real Lightning:

- Remove `ARK_MOCK_EXCHANGE`
- Add real Coinbase API keys

---

## Post-Deployment

✅ Server is live globally  
✅ Wiki can link to public URL  
✅ Friends can access immediately  
✅ GitHub webhooks work  
✅ n8n can receive public webhooks

**Your URL**: `https://ark-os.onrender.com`

---

## Troubleshooting

**Issue**: Build fails  
**Fix**: Check `render.yaml` syntax

**Issue**: Server crashes  
**Fix**: Check logs in Render dashboard

**Issue**: Port conflict  
**Fix**: Use `$PORT` environment variable

---

## Free Tier Limits

- Spins down after 15min inactivity
- First request after spin-down takes ~30 seconds
- Upgrade to paid tier for always-on

**For demo**: Free tier is perfect  
**For production**: Paid tier recommended ($7/month)
