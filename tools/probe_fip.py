#!/usr/bin/env python3
"""TEMPORARY diagnostic #2: figure out where FIP thematic now-playing lives.

Online Radio Box returns 200 for fr/fipjazz but the parser extracts no track,
so this dumps the actual page internals to see what's there, and checks whether
Radio France's own page embeds now-playing data (Next.js __NEXT_DATA__).

Run on a host with open internet. Delete once the FIP fetcher is fixed.
"""

import re
import requests

UA = "Mozilla/5.0 (compatible; RadioScrobbler/1.0)"
S = requests.Session()
S.headers.update({"User-Agent": UA})


def dump_onlineradiobox():
    url = "https://onlineradiobox.com/fr/fipjazz/playlist/?lang=en"
    print(f"\n########## ONLINE RADIO BOX: {url}")
    r = S.get(url, timeout=15)
    print(f"status={r.status_code} length={len(r.text)}")
    if r.status_code != 200:
        return
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table")
    print(f"num <table>: {len(tables)}")
    for ti, table in enumerate(tables[:3]):
        rows = table.find_all("tr")
        cls = table.get("class")
        print(f"\n-- table[{ti}] class={cls} rows={len(rows)}")
        for ri, row in enumerate(rows[:10]):
            cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
            print(f"   row[{ri}] ncells={len(cells)} {cells}")
    # Also look for any element that screams "now playing"
    for sel in ["track_history", "now", "player", "current"]:
        hits = soup.find_all(attrs={"class": re.compile(sel, re.I)})
        if hits:
            print(f"\n-- elements with class~='{sel}': {len(hits)}; first text: "
                  f"{hits[0].get_text(' ', strip=True)[:120]!r}")


def scan_radiofrance():
    url = "https://www.radiofrance.fr/fip/radio-jazz"
    print(f"\n########## RADIO FRANCE PAGE: {url}")
    r = S.get(url, timeout=15)
    print(f"status={r.status_code} length={len(r.text)}")
    if r.status_code != 200:
        return
    html = r.text
    for marker in ["__NEXT_DATA__", "firstLine", "secondLine", "nowTitle",
                   "\"now\"", "trackTitle", "\"song\"", "interpreters", "playerData"]:
        idx = html.find(marker)
        print(f"\n-- marker {marker!r}: {'FOUND @'+str(idx) if idx>=0 else 'absent'}")
        if idx >= 0:
            print("   ..." + " ".join(html[idx:idx + 300].split()))


if __name__ == "__main__":
    try:
        dump_onlineradiobox()
    except Exception as e:
        print(f"onlineradiobox probe error: {type(e).__name__}: {e}")
    try:
        scan_radiofrance()
    except Exception as e:
        print(f"radiofrance probe error: {type(e).__name__}: {e}")
    print("\nDone.")
