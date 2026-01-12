# Radio Scrobbler

A scalable Python service that monitors multiple internet radio stations and automatically scrobbles their currently playing tracks to individual Last.fm accounts.

Inspired by the [twifip project](https://github.com/bouil/twifip), this service allows you to create separate Last.fm accounts for each radio station you listen to, making it easy to track what's playing on different stations.

## Features

- **Multi-station support**: Monitor multiple radio stations simultaneously
- **Plugin architecture**: Easy to add new stations by implementing a simple fetcher class
- **Duplicate prevention**: Automatically detects when the same track is playing and avoids duplicate scrobbles
- **Configurable polling**: Set different poll intervals for each station
- **Error handling**: Robust error handling with comprehensive logging
- **Docker support**: Easy deployment with Docker and docker-compose

## Supported Stations

Currently supports:
- **Radio FIP** (France Inter Paris)
- **Superfly**
- **ORF FM4**
- **KBCO**
- **WNYC**

More stations can be easily added by creating a new fetcher class.

## Prerequisites

- Python 3.11+ (if running directly)
- Docker and Docker Compose (for containerized deployment)
- Last.fm API credentials for each station account

## Setup

### 1. Create Last.fm Accounts and API Keys

For each radio station you want to scrobble:

1. Create a Last.fm account (e.g., `twifip`, `twisuperfly`, etc.)
2. Go to [Last.fm API Account](https://www.last.fm/api/account/create) and create an API account
3. Note down your API Key and API Secret
4. Generate an MD5 hash of your Last.fm password:
   ```bash
   echo -n "your_password" | md5sum
   ```

### 2. Configure Stations

1. Copy the example configuration file:
   ```bash
   cp config/stations.yaml.example config/stations.yaml
   ```

2. Edit `config/stations.yaml` and fill in your Last.fm credentials for each station:
   ```yaml
   stations:
     - name: fip
       lastfm_username: twifip
       lastfm_api_key: YOUR_API_KEY_HERE
       lastfm_api_secret: YOUR_API_SECRET_HERE
       lastfm_password_hash: YOUR_PASSWORD_HASH_HERE
       poll_interval: 30
       enabled: true
   ```

3. Set `enabled: false` for stations you don't want to use yet.

### 3. Deploy with Docker (Recommended)

1. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. View logs:
   ```bash
   docker-compose logs -f
   ```

3. Stop the service:
   ```bash
   docker-compose down
   ```

### 4. Run Directly (Alternative)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the service:
   ```bash
   python main.py -c config/stations.yaml
   ```

## Usage

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  -c, --config PATH     Path to configuration file (default: config/stations.yaml)
  -l, --log-level LEVEL Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
  --log-file PATH       Optional log file path
```

### Example

```bash
# Run with custom config and debug logging
python main.py -c config/stations.yaml -l DEBUG --log-file logs/scrobbler.log
```

## Adding New Stations

To add a new radio station:

1. Create a new fetcher class in `src/stations/`:
   ```python
   from .base import BaseStationFetcher, TrackInfo
   import requests
   
   class MyStationFetcher(BaseStationFetcher):
       def __init__(self):
           super().__init__("mystation")
           self.session = requests.Session()
       
       def get_current_track(self) -> Optional[TrackInfo]:
           # Fetch and parse track info from station's API
           # Return TrackInfo(artist="...", title="...")
           pass
   ```

2. Register it in `src/scrobbler.py`:
   ```python
   from .stations.mystation import MyStationFetcher
   
   STATION_FETCHERS = {
       # ... existing stations ...
       'mystation': MyStationFetcher,
   }
   ```

3. Add configuration in `config/stations.yaml`:
   ```yaml
   - name: mystation
     lastfm_username: twimystation
     # ... credentials ...
   ```

## Station API Endpoints

Each station fetcher attempts to find the correct API endpoint. You may need to:

1. Inspect the station's website to find their "now playing" API
2. Check browser network requests when viewing the station's website
3. Update the fetcher's endpoint URLs accordingly

Common patterns:
- `/api/now-playing`
- `/now-playing.json`
- GraphQL endpoints
- Stream metadata (ICY protocol)

## Troubleshooting

### Station Not Scrobbling

1. Check logs: `docker-compose logs -f` or check log files
2. Verify the station's API endpoint is correct (may need to update fetcher code)
3. Test Last.fm connection: The service will log connection errors
4. Check that the station is enabled in configuration

### Last.fm Authentication Errors

1. Verify your API key and secret are correct
2. Ensure password hash is correct (MD5 of your Last.fm password)
3. Check that your Last.fm account is active

### Duplicate Scrobbles

The service tracks the last scrobbled track per station and only scrobbles when the track changes. If you see duplicates:

1. Check that the station fetcher is returning consistent track info
2. Verify the duplicate prevention logic in `scrobbler.py`

## Architecture

```
radio-scrobbler/
├── src/
│   ├── scrobbler.py          # Main orchestrator service
│   ├── lastfm_client.py      # Last.fm API wrapper
│   ├── config_loader.py      # YAML configuration loader
│   ├── stations/
│   │   ├── base.py           # Base fetcher class
│   │   ├── fip.py            # Radio FIP fetcher
│   │   └── ...               # Other station fetchers
│   └── utils.py              # Utility functions
├── config/
│   └── stations.yaml         # Station configuration
├── main.py                   # Entry point
├── Dockerfile
└── docker-compose.yml
```

## License

This project is provided as-is for personal use.

## Acknowledgments

- Inspired by [twifip](https://github.com/bouil/twifip)
- Uses [pylast](https://github.com/pylast/pylast) for Last.fm API interaction
