# Railway Deployment Guide for Web Interface

## Overview

Deploy the personal radio scrobbler web interface to Railway so you can access it from anywhere.

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository with your code
- Last.fm API credentials

## Deployment Steps

### 1. Push Code to GitHub

Make sure all your code is committed and pushed:

```bash
git add .
git commit -m "Add web interface for personal scrobbling"
git push
```

### 2. Create New Railway Project

1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `radio-scrobbler` repository

### 3. Configure Environment Variables

In Railway project settings, add these environment variables:

```
LASTFM_USERNAME=coopersmith
LASTFM_API_KEY=your_api_key
LASTFM_API_SECRET=your_api_secret
LASTFM_PASSWORD=your_password
PORT=5000
```

**Note**: Railway automatically sets `PORT` - you don't need to set it manually, but the code will use it if available.

### 4. Update Start Command

In Railway project settings → "Settings" → "Start Command", set:

```
python web_main.py
```

Or leave it blank and update the Dockerfile CMD (see below).

### 5. Update Dockerfile (Optional)

If you want Railway to use Docker, update the Dockerfile CMD:

```dockerfile
# For web interface mode
CMD ["python", "web_main.py"]
```

Or create a separate Dockerfile for web:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY web_main.py .
COPY web_app.py .
COPY config/ ./config/
COPY web/ ./web/

# Create directory for logs
RUN mkdir -p /app/logs

# Expose port (Railway will set PORT env var)
EXPOSE 5000

# Run web interface
CMD ["python", "web_main.py"]
```

### 6. Deploy

Railway will automatically:
1. Build your project
2. Install dependencies
3. Start the web server
4. Generate a public URL

### 7. Access Your Web Interface

Once deployed, Railway will provide a public URL like:
- `https://your-project-name.up.railway.app`

Click the URL to access your web interface!

## Configuration Options

### Using Environment Variables (Recommended)

Instead of a config file, use environment variables:

```bash
LASTFM_USERNAME=coopersmith
LASTFM_API_KEY=a648ef744d0625587e4ff2e7e052455a
LASTFM_API_SECRET=db4a9a22bec287389230fa773e9dba7d
LASTFM_PASSWORD=Myttob-tydri6-venbyg
POLL_INTERVAL=30
```

Then update `web_main.py` to read from environment variables if config file doesn't exist.

### Using Config File

Alternatively, you can create `config/personal_scrobbler.yaml` in your repo (but don't commit credentials - use env vars).

## Safety Features

The web interface includes several safety features:

1. **Stop Button**: Normal stop
2. **Emergency Stop**: Immediately halts all scrobbling
3. **Auto-Stop on Errors**: Automatically stops after 5 consecutive errors
4. **Error Display**: Shows errors in the UI

## Monitoring

Check Railway logs to monitor:
- Scrobbling activity
- Errors
- Station polling

## Troubleshooting

### Port Issues
- Railway sets `PORT` automatically - the code reads it from environment
- Default is 5000 if `PORT` not set

### Authentication Errors
- Verify Last.fm credentials are correct
- Check Railway environment variables are set

### Station Not Found
- Ensure `STATION_FETCHERS` registry is up to date
- Check that station names match exactly

## Running Both Systems

You can run both:
- **Railway Automated Scrobbler**: Runs `main.py` (scrobbles to separate accounts)
- **Railway Web Interface**: Runs `web_main.py` (scrobbles to your personal account)

Create two separate Railway services:
1. One for automated scrobbling (`main.py`)
2. One for web interface (`web_main.py`)
