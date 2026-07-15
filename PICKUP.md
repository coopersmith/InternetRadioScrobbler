# Pickup / Resume Notes

Working notes for continuing this project in Claude Code. The code lives on
GitHub, so any session that clones this repo has everything it needs.

## Current status (2026-07-15)

- Project revived after ~6 months dormant.
- Architecture: `main.py` -> `src/scrobbler.py` (orchestrator) -> per-station
  fetchers in `src/stations/` -> `src/lastfm_client.py`.
- **Enabled lineup (4, all confirmed fresh & live):** `fip` (main, via Radio
  France livemeta id 7 + recenttracks fallback), `fm4` and `ness` (Online Radio
  Box), `radionova` (recenttracks.com).
- **Everything else is parked** — see `PARKING_LOT.md` for each station, why it
  was parked, and how to revive it. Summary: FIP thematic webradios return a
  *stale* livemeta feed; Superfly's Online Radio Box data is laggy; FIP
  Hip-Hop/Pop have no working source (would need a headless browser); KBCO
  removed permanently; WNYC parked.
- Sources in use: `api.radiofrance.fr/livemeta` (FIP), `onlineradiobox.com`
  (fm4, ness), `recenttracks.com` (radionova, FIP fallback).

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

Active lineup is healthy. Remaining work is optional / parked:

1. Revive parked stations when a live source is found — see `PARKING_LOT.md`
   (FIP genre staleness, Superfly live source, FIP Hip-Hop/Pop via headless
   browser).
2. Add silent-failure logging/alerting so a dead scraper is visible.
3. Consolidate the ~15 markdown docs; add test coverage beyond
   `test_superfly.py` (note: the Superfly fetcher/tests were removed).
