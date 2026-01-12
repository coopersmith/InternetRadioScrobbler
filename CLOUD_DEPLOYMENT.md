# Cloud Deployment Options

Since this is a long-running service (not a web app), here are the best cloud options:

## 🚀 Recommended: Railway.app (Easiest)

**Why Railway:**
- ✅ Free tier: $5/month credit (enough for this service)
- ✅ Zero-config deployment from GitHub
- ✅ Automatic HTTPS and domain
- ✅ Easy environment variable management
- ✅ Built-in logging

**Deploy Steps:**

1. Push your code to GitHub (make sure `config/stations.yaml` is NOT committed - use environment variables instead)

2. Go to [railway.app](https://railway.app) and sign up

3. Click "New Project" → "Deploy from GitHub repo"

4. Select your repository

5. Add environment variables in Railway dashboard:
   - Create a `stations.yaml` file content as environment variable, OR
   - Set individual variables (see below)

6. Railway will auto-detect Python and deploy!

**Cost:** Free tier covers ~100 hours/month (enough for 24/7)

---

## 🎯 Alternative: Render.com (Free Tier Available)

**Why Render:**
- ✅ Free tier for background workers
- ✅ Simple deployment
- ✅ Good documentation

**Deploy Steps:**

1. Push code to GitHub

2. Go to [render.com](https://render.com) and sign up

3. Click "New" → "Background Worker"

4. Connect your GitHub repo

5. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python3 main.py -c config/stations.yaml -l INFO`
   - **Environment:** Python 3

6. Add environment variables (see below)

**Cost:** Free tier available (spins down after 15 min inactivity, but auto-wakes on requests - may need a ping service)

---

## ☁️ Alternative: Fly.io

**Why Fly.io:**
- ✅ Generous free tier
- ✅ Global edge deployment
- ✅ Great for long-running services

**Deploy Steps:**

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`

2. Login: `fly auth login`

3. Create app: `fly launch`

4. Deploy: `fly deploy`

**Cost:** Free tier includes 3 shared VMs

---

## 🔧 Using Environment Variables Instead of Config File

For cloud deployment, it's better to use environment variables. Update your config:

**Option 1: Single JSON Environment Variable**

Set `STATIONS_CONFIG` as a JSON string:
```json
{
  "stations": [
    {
      "name": "superfly",
      "lastfm_username": "coRadioSuperfly",
      "lastfm_api_key": "...",
      "lastfm_api_secret": "...",
      "lastfm_password": "...",
      "poll_interval": 30,
      "enabled": true
    }
  ]
}
```

**Option 2: Individual Environment Variables**

Set these in Railway/Render:
- `STATION_SUPERFLY_USERNAME=coRadioSuperfly`
- `STATION_SUPERFLY_API_KEY=...`
- `STATION_SUPERFLY_API_SECRET=...`
- `STATION_SUPERFLY_PASSWORD=...`

Then modify `config_loader.py` to read from env vars.

---

## 📝 Quick Railway Setup

1. **Create `railway.json`** (already created)

2. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

3. **Deploy on Railway:**
   - Go to railway.app
   - New Project → Deploy from GitHub
   - Select repo
   - Add environment variables
   - Deploy!

---

## ⚠️ Important Notes

**Don't commit secrets!**
- Add `config/stations.yaml` to `.gitignore` (already done)
- Use environment variables in cloud platforms

**Keep-alive (for Render free tier):**
- Render free tier spins down after inactivity
- Consider adding a simple HTTP endpoint that pings every 5 minutes
- Or use Railway/Fly.io which don't have this issue

**Monitoring:**
- All platforms provide built-in logs
- Check logs if scrobbling stops

---

## 🆓 Free Options Summary

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| **Railway** | $5/month credit | Easiest setup |
| **Render** | Free (with limits) | Simple deployment |
| **Fly.io** | Generous free tier | Global edge |
| **Heroku** | Paid only now | Not recommended |
| **Netlify** | ❌ Not suitable | Web apps only |

---

## 🎯 Recommendation

**For your use case:** Start with **Railway.app**
- Easiest to set up
- Free tier covers your needs
- No downtime issues
- Great developer experience

Want help setting up Railway or modifying the code to use environment variables?
