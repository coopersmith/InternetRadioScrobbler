# Troubleshooting Guide

## Double Scrobbling

If you're seeing double scrobbles, check:

1. **Local Process Running?**
   ```bash
   ps aux | grep "main.py" | grep -v grep
   ```
   If found, kill it:
   ```bash
   pkill -f "python.*main.py"
   ```

2. **Multiple Railway Deployments?**
   - Go to Railway → Deployments
   - Make sure only ONE deployment is active
   - Delete old/duplicate deployments

3. **Check Railway Logs**
   - Look for duplicate "Scrobbled" messages
   - Should only see one per track change

## Station Not Scrobbling

### FM4 Not Working

**Issue:** FM4 fetcher can't find tracks from Online Radio Box

**Possible causes:**
1. Online Radio Box format changed
2. FM4 playlist page structure different
3. Need to use different endpoint

**Check:**
- Visit: https://onlineradiobox.com/at/fm4/playlist/?lang=en
- Look for "Live" track in the table
- Check if format matches Superfly

**Fix:**
- May need to update FM4 fetcher to handle different HTML structure
- Or use FM4's own API endpoint

### General Station Issues

1. **Check Railway Logs:**
   - Look for errors about the station
   - Check if station initialized successfully

2. **Verify Configuration:**
   - Station name matches fetcher name
   - `enabled: true` in config
   - Credentials are correct

3. **Test Fetcher Locally:**
   ```bash
   cd /Users/coopersmith/radio-scrobbler
   source venv/bin/activate
   python3 -c "
   import sys
   sys.path.insert(0, 'src')
   from stations.fm4 import FM4Fetcher
   fetcher = FM4Fetcher()
   track = fetcher.get_current_track()
   print(track)
   "
   ```

## Railway Issues

**Service keeps restarting:**
- Check logs for fatal errors
- Verify JSON syntax in STATIONS_CONFIG
- Check environment variables are set correctly

**No logs appearing:**
- Check Railway service is running
- Verify deployment succeeded
- Check service status

## Last.fm Issues

**Authentication failed:**
- Verify API credentials are correct
- Check password is correct
- Ensure API key has proper permissions

**Scrobbles not appearing:**
- Wait a few minutes (Last.fm can be slow)
- Check Last.fm profile directly
- Verify account is active
