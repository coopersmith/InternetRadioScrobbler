# Pickup / Resume Notes

Working notes for continuing this project in Claude Code. The code lives on
GitHub, so any session that clones this repo has everything it needs.

## Current status (2026-07-14)

- Project was dormant ~6 months; being revived.
- Architecture is sound: `main.py` -> `src/scrobbler.py` (orchestrator) ->
  per-station fetchers in `src/stations/` -> `src/lastfm_client.py`.
- Most fetchers scrape third-party sites, NOT the stations directly:
  - `onlineradiobox.com` -> Superfly, FM4, KBCO, WNYC, Ness
  - `recenttracks.com` -> Radio Nova, main FIP
  - `www.radiofrance.fr` API -> FIP thematic stations + hip-hop
- Confirmed working in production (per old docs): **Superfly** only.
- Known broken: **FIP Hip-Hop** (`src/stations/fiphiphop.py`) returns None —
  its API endpoint was never discovered.
- KBCO/WNYC "own-API" endpoint guesses (e.g. `/now-playing.json`) are almost
  certainly dead; they rely on the onlineradiobox fallback.

## How to verify which stations actually work

`check_stations.py` runs every fetcher live and reports OK / MISS / ERR. It
needs no credentials (it only tests fetching, never scrobbles).

```bash
python check_stations.py            # all stations
python check_stations.py fip fm4    # specific ones
python check_stations.py --json     # machine-readable
```

Exit code is 0 only if every checked station returned a track.

### Network requirement

Fetching is blocked under the default **Trusted** network policy. To run the
health check, the environment needs **Custom** access (default list + these
domains) or **Full**:

```
onlineradiobox.com
recenttracks.com
www.radiofrance.fr
audioapi.orf.at
api.orf.at
fm4.orf.at
```

A policy change only applies to NEW sessions — start a fresh session after
editing it.

## Where the real config lives

`config/stations.yaml` (real Last.fm credentials) is gitignored — only the
`.example` is committed. The live copy is the Railway service's
`STATIONS_CONFIG` environment variable (Railway dashboard -> service ->
Variables). Needed only for actual scrobbling / redeploy, not for the health
check.

## Next tasks (punch list)

1. Run `check_stations.py` with network open -> get ground truth per station.
2. Fix or remove FIP Hip-Hop.
3. Drop the dead guessed-API endpoints in KBCO/WNYC fetchers.
4. Add silent-failure logging/alerting so a dead scraper is visible.
5. Consolidate the ~15 markdown docs; add test coverage beyond
   `test_superfly.py`.
