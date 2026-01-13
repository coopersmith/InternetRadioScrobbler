# Fix Double Scrobbling

## Quick Fix

**Stop all local processes:**
```bash
pkill -f "python.*main.py"
pkill -f "radio-scrobbler"
```

**Verify stopped:**
```bash
ps aux | grep "main.py" | grep -v grep
```
(Should return nothing)

## Check Railway

1. **Go to Railway Dashboard**
2. **Check Deployments tab**
3. **Make sure only ONE deployment is active**
4. **If multiple, delete old ones**

## Verify Single Instance

**Check Railway Logs:**
- Should see ONE "Scrobbled" message per track change
- If you see two, there are multiple instances

**Check Last.fm:**
- Wait for a new track to play
- Should see ONE scrobble, not two

## If Still Double Scrobbling

1. **Pause Railway deployment** temporarily
2. **Check if scrobbles stop** (confirms Railway is one source)
3. **Check local processes again**
4. **Restart Railway** with only one deployment
