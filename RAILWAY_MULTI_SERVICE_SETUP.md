# Deploying Multiple Services from Same Repository on Railway

You can run both the automated scrobbler AND the web interface from the same GitHub repository.

## Current Setup

You likely have one Railway service running:
- **Service 1**: Automated scrobbler (`main.py`) - scrobbles to separate Last.fm accounts

## Adding Second Service (Web Interface)

### Step 1: Create New Service

1. Go to your Railway project dashboard
2. Click **"+ New"** button (top right)
3. Select **"GitHub Repo"**
4. Choose the **same repository** (`radio-scrobbler`)
5. Railway will create a new service

### Step 2: Configure the New Service

In the new service settings:

#### A. Set Environment Variable to Identify Service
Since Railway reads `railway.json` and you can't override it, we use an environment variable:

1. Go to **Variables** tab
2. Add this environment variable:
   ```
   RAILWAY_SERVICE=web
   ```
   
   This tells the `start.sh` script to run `web_main.py` instead of `main.py`.

**How it works:**
- The `railway.json` now uses `./start.sh` as the start command
- `start.sh` checks the `RAILWAY_SERVICE` environment variable
- If `RAILWAY_SERVICE=web`, it runs `web_main.py`
- Otherwise, it runs `main.py` (for your automated scrobbler service)

#### B. Add Environment Variables
Go to **Variables** tab and add:

```
LASTFM_USERNAME=coopersmith
LASTFM_API_KEY=a648ef744d0625587e4ff2e7e052455a
LASTFM_API_SECRET=db4a9a22bec287389230fa773e9dba7d
LASTFM_PASSWORD=Myttob-tydri6-venbyg
POLL_INTERVAL=30
```

**Note**: Railway automatically sets `PORT` - you don't need to add it.

#### C. Configure Service Name (Optional)
1. Click on the service name at the top
2. Rename it to something like: **"Personal Scrobbler Web"** or **"Web Interface"**

### Step 3: Deploy

Railway will automatically:
1. Build the project
2. Install dependencies
3. Start `web_main.py`
4. Generate a public URL

### Step 4: Access Your Web Interface

Once deployed, Railway will provide a URL like:
- `https://your-web-service.up.railway.app`

Click the URL to access your web interface!

## Result

You'll now have **two separate Railway services**:

1. **Automated Scrobbler Service**
   - Runs: `main.py`
   - Scrobbles to separate Last.fm accounts (coRadioSuperfly, coRadioFM4, etc.)
   - Runs continuously 24/7

2. **Web Interface Service**
   - Runs: `web_main.py`
   - Scrobbles to your personal Last.fm account (coopersmith)
   - Provides web UI for manual control
   - Accessible via public URL

## Important Notes

- Both services use the **same codebase** from GitHub
- They run **independently** - stopping one doesn't affect the other
- They use **different Last.fm accounts** - no conflicts
- Each service has its own **environment variables** and **logs**
- Railway will **auto-deploy** both when you push to GitHub

## Troubleshooting

### Service Uses Wrong Command
- Check **Settings → Start Command** is set to `python web_main.py`

### Can't Access Web Interface
- Check Railway logs for errors
- Verify environment variables are set correctly
- Make sure the service is running (green status)

### Both Services Deploying on Push
- This is normal! Railway watches your repo and redeploys all services
- Each service uses its own start command, so they'll run correctly

## Managing Services

- **View Logs**: Click on service → "Deployments" → Click a deployment → "View Logs"
- **Redeploy**: Click "Redeploy" button
- **Stop/Start**: Use the power button in service settings
- **Delete**: Settings → Danger Zone → Delete Service
