#!/usr/bin/env python3
"""TEMPORARY diagnostic: probe candidate now-playing sources for FIP webradios.

The thematic FIP stations (jazz, rock, electro, ...) currently fail because
their Radio France API endpoint pattern is dead. The main `fip` station works
via recenttracks.com. This script probes a matrix of candidate sources for a
representative thematic station (jazz) so we can see which URL responds and
what its data shape is, then implement the real fix.

Run on a host with open internet (e.g. the GitHub Actions runner). Delete this
file once the FIP fetcher is fixed.
"""

import json
import requests

UA = "Mozilla/5.0 (compatible; RadioScrobbler/1.0)"

# (label, url, kind) — kind is "json" or "html"
CANDIDATES = [
    # Known-working reference (main fip via recenttracks) to confirm the probe env works
    ("recenttracks main fip (reference)", "https://recenttracks.com/stations/fip/recently-played", "html"),

    # recenttracks candidates for the jazz webradio
    ("recenttracks fip-jazz", "https://recenttracks.com/stations/fip-jazz/recently-played", "html"),
    ("recenttracks fip-radio-jazz", "https://recenttracks.com/stations/fip-radio-jazz/recently-played", "html"),
    ("recenttracks fipjazz", "https://recenttracks.com/stations/fipjazz/recently-played", "html"),

    # Radio France API candidates for the jazz webradio
    ("rf current code path", "https://www.radiofrance.fr/fip/radio-jazz/api/songs", "json"),
    ("rf live/webradios fip_jazz", "https://www.radiofrance.fr/fip/api/live/webradios/fip_jazz", "json"),
    ("rf api/songs?webradio", "https://www.radiofrance.fr/fip/api/songs?webradio=fip_jazz", "json"),
    ("rf api/live", "https://www.radiofrance.fr/fip/api/live", "json"),
    ("rf api/live/webradios (no id)", "https://www.radiofrance.fr/fip/api/live/webradios", "json"),

    # onlineradiobox candidates for a FIP webradio
    ("orb fr/fipjazz", "https://onlineradiobox.com/fr/fipjazz/playlist/?lang=en", "html"),
    ("orb fr/fip_jazz", "https://onlineradiobox.com/fr/fip_jazz/playlist/?lang=en", "html"),
]


def probe(label, url, kind):
    print(f"\n=== {label}\n    {url}")
    try:
        headers = {"User-Agent": UA}
        if kind == "json":
            headers["Accept"] = "application/json"
        r = requests.get(url, headers=headers, timeout=15)
        ctype = r.headers.get("content-type", "")
        print(f"    status={r.status_code}  content-type={ctype}  length={len(r.text)}")
        if r.status_code != 200:
            return
        if kind == "json":
            try:
                data = r.json()
                if isinstance(data, dict):
                    print(f"    JSON top-level keys: {list(data.keys())[:20]}")
                elif isinstance(data, list):
                    print(f"    JSON list len={len(data)}; first item keys: "
                          f"{list(data[0].keys())[:20] if data and isinstance(data[0], dict) else 'n/a'}")
                print("    JSON snippet: " + json.dumps(data)[:400])
            except ValueError:
                print("    (not valid JSON) body snippet: " + r.text[:200].replace('\n', ' '))
        else:
            # HTML: show whether it looks like it has a track table
            body = r.text
            print("    HTML snippet: " + " ".join(body[:300].split()))
            print(f"    has <table>: {'<table' in body.lower()}   "
                  f"mentions 'recently': {'recently' in body.lower()}")
    except Exception as e:
        print(f"    ERROR {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("FIP endpoint probe (representative station: jazz)")
    for label, url, kind in CANDIDATES:
        probe(label, url, kind)
    print("\nDone.")
