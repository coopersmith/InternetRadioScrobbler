#!/usr/bin/env python3
"""TEMPORARY diagnostic #5: read ICY stream metadata for FIP Hip-Hop / Pop.

Hip-Hop and Pop aren't on the livemeta API. But every FIP webradio streams
from Radio France's Icecast, and the stream carries the current track in its
ICY metadata (StreamTitle='Artist - Title'). This probes candidate stream URLs
and prints the StreamTitle so we can wire Hip-Hop and Pop to their streams.

Run on a host with open internet. Delete once fixed.
"""

import requests

UA = "Mozilla/5.0 (compatible; RadioScrobbler/1.0)"

# Candidate Icecast stream URLs (slug variants x quality/format).
SLUGS = {
    "fip (reference)": ["fip"],
    "hiphop": ["fiphiphop", "fip_hiphop", "fip-hiphop", "fiphip-hop"],
    "pop": ["fippop", "fip_pop", "fip-pop"],
    "jazz (reference)": ["fipjazz"],
}
FORMATS = ["midfi.mp3", "hifi.aac", "lofi.mp3"]
HOST = "https://icecast.radiofrance.fr/{slug}-{fmt}"


def read_icy_title(url):
    """Open the stream, read one ICY metadata block, return StreamTitle."""
    headers = {"User-Agent": UA, "Icy-MetaData": "1"}
    r = requests.get(url, headers=headers, stream=True, timeout=15)
    try:
        if r.status_code != 200:
            return f"status={r.status_code}"
        metaint = r.headers.get("icy-metaint")
        if not metaint:
            return f"200 but no icy-metaint (headers: {list(r.headers.keys())})"
        metaint = int(metaint)
        raw = r.raw
        raw.read(metaint)  # skip audio payload
        length_byte = raw.read(1)
        if not length_byte:
            return "no metadata length byte"
        meta_len = length_byte[0] * 16
        if meta_len == 0:
            return "(empty metadata this block; retry)"
        meta = raw.read(meta_len).decode("utf-8", errors="replace")
        return meta.strip("\x00").strip()
    finally:
        r.close()


if __name__ == "__main__":
    print("Probing FIP Icecast stream metadata\n")
    for label, slugs in SLUGS.items():
        print(f"### {label}")
        for slug in slugs:
            for fmt in FORMATS:
                url = HOST.format(slug=slug, fmt=fmt)
                try:
                    result = read_icy_title(url)
                    print(f"  {url}\n      -> {result}")
                except Exception as e:
                    print(f"  {url}\n      -> ERROR {type(e).__name__}: {e}")
        print()
    print("Done.")
