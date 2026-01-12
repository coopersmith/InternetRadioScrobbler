# Railway Deployment Setup

## Quick Setup

### Option 1: Environment Variable (Recommended)

1. **In Railway Dashboard**, go to your project → **Variables** tab

2. **Add a new variable** named `STATIONS_CONFIG` with this JSON value:

```json
{
  "stations": [
    {
      "name": "superfly",
      "lastfm_username": "coRadioSuperfly",
      "lastfm_api_key": "a85d7805cb7f94f0e0a83e6a766675e8",
      "lastfm_api_secret": "70602b67ed936bd528748f1b33e994e8",
      "lastfm_password": "tukniw-6jiwbu-wIznyn",
      "poll_interval": 30,
      "enabled": true
    }
  ]
}
```

**Important:** Replace with your actual credentials!

3. **Save** and Railway will automatically redeploy

### Option 2: YAML Format (Alternative)

You can also use YAML format in the environment variable:

```yaml
stations:
  - name: superfly
    lastfm_username: coRadioSuperfly
    lastfm_api_key: a85d7805cb7f94f0e0a83e6a766675e8
    lastfm_api_secret: 70602b67ed936bd528748f1b33e994e8
    lastfm_password: tukniw-6jiwbu-wIznyn
    poll_interval: 30
    enabled: true
```

## Adding More Stations

Just add more entries to the `stations` array:

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
    },
    {
      "name": "fm4",
      "lastfm_username": "coRadioFM4",
      "lastfm_api_key": "...",
      "lastfm_api_secret": "...",
      "lastfm_password": "...",
      "poll_interval": 30,
      "enabled": true
    }
  ]
}
```

## Verify Deployment

1. Check **Logs** tab in Railway
2. You should see:
   ```
   INFO - Loading configuration from STATIONS_CONFIG environment variable
   INFO - Loaded 1 station(s)
   INFO - Initialized station: superfly -> coRadioSuperfly
   INFO - Starting scrobbler with 1 station(s)
   ```

3. Check your Last.fm profile: https://www.last.fm/user/coRadioSuperfly

## Troubleshooting

**"Configuration file not found"**
- Make sure `STATIONS_CONFIG` environment variable is set
- Check the JSON/YAML syntax is valid

**"No stations configured"**
- Check that `enabled: true` is set
- Verify JSON structure is correct

**"Failed to connect to Last.fm"**
- Double-check API credentials
- Verify password is correct
