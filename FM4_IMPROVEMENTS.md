# FM4 Scrobbling Improvements

## Issue
FM4 isn't scrobbling as frequently as tracks appear on the playlist.

## Possible Causes

1. **Online Radio Box "Live" row updates slowly**
   - The "Live" row might only update every few minutes
   - If tracks change every 2-3 minutes, we might miss some

2. **Poll interval too long**
   - Currently polling every 30 seconds
   - If tracks change faster, we might miss them

3. **Duplicate detection too strict**
   - Might be preventing legitimate scrobbles

## Solutions Applied

1. ✅ **Improved Live row detection** - Now properly finds and prioritizes "Live" row
2. ✅ **Better filtering** - Skips non-music entries (podcasts, jingles, etc.)
3. ✅ **Fallback to most recent track** - If no Live row, uses first time-based row

## Further Improvements (if needed)

### Option 1: Reduce Poll Interval for FM4

In Railway `STATIONS_CONFIG`, set FM4 to poll more frequently:

```json
{
  "name": "fm4",
  "poll_interval": 15,  // Poll every 15 seconds instead of 30
  ...
}
```

### Option 2: Use Most Recent Track Instead of Live

If "Live" row updates too slowly, we could modify FM4 fetcher to always use the most recent time-based track instead.

### Option 3: Check Multiple Recent Tracks

We could track the last few tracks and scrobble any that are new, not just the current one.

## Current Status

The improved fetcher should now:
- ✅ Find "Live" row correctly
- ✅ Filter out non-music entries
- ✅ Use most recent track as fallback

Monitor Railway logs to see if FM4 scrobbling improves!
