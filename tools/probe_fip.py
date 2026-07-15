#!/usr/bin/env python3
"""TEMPORARY diagnostic #4: find FIP Hip-Hop (and Pop) on the livemeta API.

The classic FIP webradios use ids 7,64,65,66,69,70,71,74,77. Hip-Hop and Pop
are newer and weren't in that range, so sweep a broad id range and print the
current song + stationId for every id that returns 200, so we can spot the
rap/hip-hop station (and pop).

Run on a host with open internet. Delete once fixed.
"""

import requests

UA = "Mozilla/5.0 (compatible; RadioScrobbler/1.0)"
S = requests.Session()
S.headers.update({"User-Agent": UA})

KNOWN = {7: "fip", 64: "rock", 65: "jazz", 66: "groove", 69: "monde",
         70: "nouveautes", 71: "reggae", 74: "electro", 77: "metal"}


def current_song(data):
    try:
        steps = data.get("steps") or {}
        levels = data.get("levels") or []
        if not (steps and levels):
            return "(no steps/levels)"
        level = levels[0]
        items = level.get("items") or []
        pos = level.get("position")
        if pos is None or not (0 <= pos < len(items)):
            pos = len(items) - 1
        step = steps.get(items[pos], {})
        title = step.get("title") or step.get("titre")
        artist = (step.get("authors") or step.get("interpreteMorceau")
                  or step.get("performers"))
        return f"{artist} - {title}"
    except Exception as e:
        return f"(parse err {e})"


if __name__ == "__main__":
    print("Sweeping livemeta ids for Hip-Hop / Pop\n")
    hits = []
    for rid in range(1, 141):
        url = f"https://api.radiofrance.fr/livemeta/pull/{rid}"
        try:
            r = S.get(url, timeout=8)
            if r.status_code != 200:
                continue
            data = r.json()
            sid = data.get("stationId")
            song = current_song(data)
            tag = KNOWN.get(rid, "?")
            print(f"id={rid:<4} stationId={sid}  [{tag}]  NOW: {song}")
            hits.append(rid)
        except ValueError:
            print(f"id={rid:<4} 200 but not JSON")
        except Exception:
            pass
    print(f"\n{len(hits)} live ids found: {hits}")
    print("Look for a rap/hip-hop artist above -> that id is FIP Hip-Hop.")
    print("Done.")
