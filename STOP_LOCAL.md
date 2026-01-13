# Stop Local Scrobbler

If you're getting double scrobbles, you likely have both local and Railway running.

## Quick Stop Commands

**Stop all Python scrobbler processes:**
```bash
pkill -f "python.*main.py"
pkill -f "radio-scrobbler"
```

**Or more specifically:**
```bash
cd /Users/coopersmith/radio-scrobbler
pkill -f "python3 main.py"
```

**Check if stopped:**
```bash
ps aux | grep "main.py" | grep -v grep
```
(Should return nothing)

## Verify Only Railway is Running

1. **Check Railway logs** - Should see scrobbles there
2. **Stop local script** - Use commands above
3. **Wait 30 seconds** - Check Last.fm
4. **Should see single scrobbles** - Not doubles

## Background Processes

If you started it with `nohup` or `&`:
```bash
# Find background jobs
jobs

# Kill by job number
kill %1
```

## Check for Multiple Instances

```bash
# Count running instances
ps aux | grep "main.py" | grep -v grep | wc -l
# Should be 0
```

## Railway Only Setup

Once local is stopped:
- ✅ Railway handles all scrobbling
- ✅ No local script needed
- ✅ Single scrobbles only
