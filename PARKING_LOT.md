# Parking Lot

Stations that are **not** enabled because they don't (yet) return fresh, live
now-playing data. Each entry records what we found and what it would take to
revive it, so the investigation doesn't have to be repeated.

The active lineup is the four confirmed-live stations: **fip (main), fm4, ness,
radionova**. Everything below is removed from the scrobbler registry
(`src/scrobbler.py`).

## FIP thematic webradios — jazz, rock, electro, reggae, groove, metal

- **Status:** parked (stale feed).
- **What works:** Radio France's livemeta API returns a valid, genre-correct
  track: `https://api.radiofrance.fr/livemeta/pull/{id}` with ids
  `rock=64, jazz=65, groove=66, monde=69, nouveautes=70, reggae=71,
  electro=74, metal=77` (main `fip=7`). The response shape (`steps` + `levels`)
  is parsed by `FIPFetcher.get_from_livemeta` in `src/stations/fip.py`, which
  still supports these ids via `LIVEMETA_IDS`.
- **Why parked:** the per-genre feeds returned the **same track for ~14 minutes**
  across multiple health checks while the main `fip` feed (same API) cycled
  normally — i.e. the genre responses appear stale/cached, so scrobbles would be
  wrong or missed.
- **To revive:** confirm the staleness, then try defeating it — e.g. a
  cache-buster query param on the livemeta request, a different Radio France
  endpoint, or the modern JS API (see hip-hop below). Once a genre feed is
  confirmed live, re-add it to `STATION_FETCHERS`, e.g.
  `'fipjazz': lambda: FIPFetcher('jazz')`.

## FIP Hip-Hop and FIP Pop

- **Status:** parked (no working source found).
- **What we ruled out:**
  - livemeta ids 1–140 swept — Hip-Hop and Pop are **not** present (only the
    classic webradios above are).
  - recenttracks.com — no FIP sub-stations (404).
  - onlineradiobox `fr/fip{genre}` — page exists but has no playlist table.
  - Icecast stream ICY metadata — the streams exist
    (`https://icecast.radiofrance.fr/fiphiphop-midfi.mp3`,
    `.../fippop-midfi.mp3`, also `-hifi.aac`) but Radio France sends **no
    `icy-metaint`**, so there is no in-band track title.
- **To revive:** capture the now-playing API the radiofrance.fr player calls via
  a headless browser (Playwright on the CI runner), then wire Hip-Hop/Pop to it.
  This is the "pause hip-hop" item — deferred by choice.

## Superfly

- **Status:** parked (laggy source).
- **What works:** Online Radio Box at `at/983superflyfm` returns a track.
- **Why parked:** the Online Radio Box playlist for Superfly is stale/sparse —
  it sat on the same track for ~20 minutes and logs songs only sporadically, so
  it isn't a reliable live feed.
- **To revive:** find a live source — Superfly's own site
  (`superfly.fm`) loads now-playing via a JS widget (its homepage HTML exposes
  no obvious feed), so this likely also needs a headless browser or the widget's
  backing API.

## KBCO

- **Status:** removed permanently (owner's request — iHeartMedia). Not to be
  revived.

## WNYC

- **Status:** parked (little to scrobble).
- **Why:** public talk/news radio; Online Radio Box `us/wnyc` returned no track.
  Low value even if fixed.
