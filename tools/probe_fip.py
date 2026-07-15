#!/usr/bin/env python3
"""TEMPORARY diagnostic #3.

FIP: neither onlineradiobox nor recenttracks nor the radiofrance.fr page yield
thematic now-playing data. Try Radio France's `livemeta` API (the historical
FIP endpoint, one numeric id per webradio) and map which id is which genre.

Superfly: onlineradiobox is stale for it, so scan superfly.fm for a live
now-playing source.

Run on a host with open internet. Delete once fixed.
"""

import json
import requests

UA = "Mozilla/5.0 (compatible; RadioScrobbler/1.0)"
S = requests.Session()
S.headers.update({"User-Agent": UA})

# Historical FIP webradio ids for the livemeta API (guesses to be mapped).
LIVEMETA_IDS = [7, 64, 65, 66, 69, 70, 71, 74, 77, 78, 95, 98]
LIVEMETA_HOSTS = [
    "https://api.radiofrance.fr/livemeta/pull/{id}",
    "https://www.fip.fr/livemeta/{id}",
]


def probe_livemeta():
    print("\n########## RADIO FRANCE LIVEMETA API")
    for host in LIVEMETA_HOSTS:
        print(f"\n--- host pattern: {host}")
        for rid in LIVEMETA_IDS:
            url = host.format(id=rid)
            try:
                r = S.get(url, timeout=12)
                note = f"status={r.status_code} len={len(r.text)}"
                song = ""
                if r.status_code == 200:
                    try:
                        data = r.json()
                        song = summarize_livemeta(data)
                        note += f" keys={list(data.keys())[:8]}"
                    except ValueError:
                        note += " (not json)"
                print(f"  id={rid:<4} {note}  {song}")
            except Exception as e:
                print(f"  id={rid:<4} ERROR {type(e).__name__}: {e}")


def summarize_livemeta(data):
    """Pull the current song out of a livemeta response, if shaped as expected."""
    try:
        steps = data.get("steps") or {}
        levels = data.get("levels") or []
        if levels and steps:
            items = levels[0].get("items", [])
            pos = levels[0].get("position", len(items) - 1)
            uid = items[pos] if 0 <= pos < len(items) else items[-1]
            step = steps.get(uid, {})
            title = step.get("title") or step.get("titre")
            author = step.get("authors") or step.get("interpreteMorceau") or step.get("performers")
            return f">>> NOW: {author} - {title}"
        # Alternative shapes
        for k in ("now", "current", "song"):
            if k in data:
                return f">>> {k}: " + json.dumps(data[k])[:200]
    except Exception as e:
        return f"(parse err {e})"
    return "(no song parsed) snippet=" + json.dumps(data)[:150]


def scan_superfly():
    print("\n########## SUPERFLY SITE SCAN")
    for url in ["https://www.superfly.fm/", "https://superfly.fm/"]:
        print(f"\n--- {url}")
        try:
            r = S.get(url, timeout=12)
            print(f"status={r.status_code} len={len(r.text)}")
            if r.status_code != 200:
                continue
            html = r.text.lower()
            for marker in ["nowplaying", "now_playing", "now-playing", "currenttrack",
                           "current-track", "onair", "on-air", "streamabc", "radio.co",
                           "laut.fm", "creacast", "icecast", "wp-json", "/api/", ".mp3"]:
                idx = html.find(marker)
                if idx >= 0:
                    print(f"  {marker!r} @ {idx}: ..." + " ".join(r.text[idx:idx + 160].split()))
        except Exception as e:
            print(f"  ERROR {type(e).__name__}: {e}")


if __name__ == "__main__":
    try:
        probe_livemeta()
    except Exception as e:
        print(f"livemeta probe error: {type(e).__name__}: {e}")
    try:
        scan_superfly()
    except Exception as e:
        print(f"superfly scan error: {type(e).__name__}: {e}")
    print("\nDone.")
