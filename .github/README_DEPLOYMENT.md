# Deployment Setup

## Railway Deployment

1. Fork this repository
2. Go to [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your forked repository
5. Add environment variables (see below)
6. Deploy!

## Environment Variables

For Railway, you'll need to set these environment variables. You can either:

**Option A: Use the config file as an environment variable**
- Set `STATIONS_CONFIG` with the YAML content (base64 encoded or as-is)

**Option B: Use individual environment variables** (recommended)
- `STATION_SUPERFLY_USERNAME=your_username`
- `STATION_SUPERFLY_API_KEY=your_key`
- `STATION_SUPERFLY_API_SECRET=your_secret`
- `STATION_SUPERFLY_PASSWORD=your_password`

See `CLOUD_DEPLOYMENT.md` for more details.
