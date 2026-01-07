# Deployment Guide: Going Public

To share the **Collaborative Mermaid Editor** with friends, we need to push your local changes to GitHub. Render is connected to your repository and will automatically deploy the latest version.

## 1. Commit & Push (Manual)

Run these commands in your terminal to save your work and update the live server:

```bash
git add .
git commit -m "feat: Add Collaborative Mermaid Editor"
git push
```

## 2. Check Render Dashboard

Once pushed:

1. Go to your [Render Dashboard](https://dashboard.render.com).
2. Look for **ark-os-production**.
3. You should see a "Deploying..." status.
4. Once "Live", share the URL: `https://ark-os-production.onrender.com/collab/index.html`

## 3. Temporary Tunnel (Immediate)

If you want a link *right now* without waiting for a build:

```bash
# Install localtunnel if not installed
npm install -g localtunnel

# Create a public tunnel to your local port 3000
lt --port 3000
```

*This gives you a url like `https://tender-wombat-42.loca.lt` that points directly to your Mac Mini.*
