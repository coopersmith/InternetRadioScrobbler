# Personal Radio Scrobbler Web Interface

A web-based interface for scrobbling radio stations to your personal Last.fm account.

## Quick Start

### 1. Create Configuration File

Copy the example config and fill in your Last.fm credentials:

```bash
cp config/personal_scrobbler.yaml.example config/personal_scrobbler.yaml
```

Edit `config/personal_scrobbler.yaml` and add your Last.fm credentials:
- `username`: Your Last.fm username
- `api_key`: Your Last.fm API key
- `api_secret`: Your Last.fm API secret  
- `password`: Your Last.fm password

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Web Server

```bash
python web_main.py
```

### 4. Access the Interface

Open your browser to: http://localhost:5000

## Features

- **Dynamic Station Discovery**: Automatically discovers all stations from the main scrobbler registry
- **Simple Interface**: Select a station and click "Start Scrobbling"
- **Real-time Status**: See what track is currently playing and what was last scrobbled
- **Automatic Updates**: When new stations are added to the Railway system, they automatically appear here

## How It Works

1. Select a station from the dropdown (populated from `STATION_FETCHERS` registry)
2. Click "Start Scrobbling" to begin
3. The system polls the station every 30 seconds (configurable)
4. When a new track is detected, it's automatically scrobbled to your Last.fm account
5. Click "Stop" when you're done listening

## Configuration Options

Edit `config/personal_scrobbler.yaml`:

- `poll_interval`: How often to check for new tracks (default: 30 seconds)
- `server.host`: Server host (default: 0.0.0.0)
- `server.port`: Server port (default: 5000)

## Environment Variables

You can also use environment variables for Last.fm credentials:

```bash
export LASTFM_USERNAME="your_username"
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"
export LASTFM_PASSWORD="your_password"
```

Then in `config/personal_scrobbler.yaml`, use:
```yaml
lastfm:
  username: "${LASTFM_USERNAME}"
  api_key: "${LASTFM_API_KEY}"
  # etc.
```

## Deployment

### Local Development

```bash
python web_main.py
```

### Railway Deployment

1. Set environment variables for Last.fm credentials
2. Update Railway to run `web_main.py` instead of `main.py`
3. Configure Railway to expose port 5000
4. Set `PORT` environment variable if Railway uses a different port

## Troubleshooting

- **"Scrobbler not initialized"**: Make sure you've created `config/personal_scrobbler.yaml` with valid credentials
- **"Failed to connect to Last.fm"**: Check your API credentials are correct
- **Stations not loading**: Ensure the main scrobbler code is up to date (stations are discovered from `STATION_FETCHERS`)

## Notes

- This web interface is completely independent from the Railway automated scrobbler
- The Railway system continues to run separately, scrobbling to separate Last.fm accounts
- This interface scrobbles to YOUR personal Last.fm account
- Duplicate prevention is handled automatically (won't scrobble the same track twice)
