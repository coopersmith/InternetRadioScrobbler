#!/usr/bin/env python3
"""Health check for every registered station fetcher.

Runs each station's get_current_track() live and reports whether it returns a
track right now. Use this to see which stations are actually working without
needing to deploy or watch Last.fm.

Run it from anywhere with open network access (locally, or on the Railway box):

    python check_stations.py                # check every station
    python check_stations.py fip superfly   # check only named stations
    python check_stations.py --json         # machine-readable output

Exit code is 0 if every checked station returned a track, 1 otherwise, so it
can double as a smoke test in CI or a cron alert.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrobbler import STATION_FETCHERS  # noqa: E402


def check_one(name, factory):
    """Run a single fetcher and return a result dict."""
    start = time.time()
    try:
        fetcher = factory()
        track = fetcher.get_current_track()
        elapsed = round(time.time() - start, 2)
        if track:
            return {
                "station": name,
                "status": "ok",
                "track": f"{track.artist} - {track.title}",
                "seconds": elapsed,
            }
        return {
            "station": name,
            "status": "no_track",
            "track": None,
            "seconds": elapsed,
            "note": "fetcher ran but returned no track (source down, HTML changed, or nothing playing)",
        }
    except Exception as e:  # noqa: BLE001 - health check should never crash
        return {
            "station": name,
            "status": "error",
            "track": None,
            "seconds": round(time.time() - start, 2),
            "note": f"{type(e).__name__}: {e}",
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("stations", nargs="*", help="Station names to check (default: all)")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show fetcher debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.CRITICAL,
        format="%(levelname)s %(name)s: %(message)s",
    )

    to_check = args.stations or list(STATION_FETCHERS.keys())
    unknown = [s for s in to_check if s not in STATION_FETCHERS]
    if unknown:
        print(f"Unknown station(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"Known: {', '.join(STATION_FETCHERS.keys())}", file=sys.stderr)
        return 2

    results = [check_one(name, STATION_FETCHERS[name]) for name in to_check]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        icons = {"ok": "OK  ", "no_track": "MISS", "error": "ERR "}
        print(f"\nStation health check ({len(results)} station(s))")
        print("-" * 72)
        for r in results:
            icon = icons.get(r["status"], "?   ")
            detail = r["track"] or r.get("note", "")
            print(f"[{icon}] {r['station']:12} {detail}  ({r['seconds']}s)")
        print("-" * 72)
        ok = sum(1 for r in results if r["status"] == "ok")
        print(f"{ok}/{len(results)} returning tracks\n")

    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
