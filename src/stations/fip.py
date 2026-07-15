"""Radio FIP station fetcher - main FIP station and its thematic webradios.

Radio France's live metadata API is the reliable source for every FIP
webradio. Each webradio has a numeric id:

    https://api.radiofrance.fr/livemeta/pull/{id}

The response contains a ``steps`` dict (keyed by track uid) and a ``levels``
list whose current ``position`` points at the track playing now.

Note: FIP Pop and FIP Hip-Hop are newer stations that are not served by this
legacy endpoint, so they are not mapped here (they return no track until a
working source is found).
"""

import requests
from typing import Optional
try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo


# Genre name (as registered in scrobbler.STATION_FETCHERS) -> livemeta id.
LIVEMETA_IDS = {
    "fip": 7,
    "rock": 64,
    "jazz": 65,
    "groove": 66,
    "reggae": 71,
    "electro": 74,
    "metal": 77,
    # Available on livemeta but not currently in the station lineup:
    # "monde": 69, "nouveautes": 70,
}


class FIPFetcher(BaseStationFetcher):
    """Fetcher for Radio FIP and its thematic webradios via the livemeta API.

    Pass the bare genre for a thematic station (e.g. ``FIPFetcher('jazz')``),
    or nothing / ``'fip'`` for the main station.
    """

    def __init__(self, station_name: str = "fip"):
        super().__init__(station_name)
        self.station_name = station_name
        self.livemeta_id = LIVEMETA_IDS.get(station_name)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)',
            'Accept': 'application/json'
        })

    def get_current_track(self) -> Optional[TrackInfo]:
        """Fetch the currently playing track from Radio FIP."""
        if self.livemeta_id is not None:
            track = self.get_from_livemeta(self.livemeta_id)
            if track:
                self.logger.debug(f"Found FIP track via livemeta id={self.livemeta_id}")
                return track

        # Fallback for the main station only.
        if self.station_name == "fip":
            track = self.get_from_recenttracks()
            if track:
                self.logger.debug("Found FIP track from RecentTracks.com")
                return track

        self.logger.warning(f"Could not fetch track from FIP ({self.station_name})")
        return None

    def get_from_livemeta(self, station_id: int) -> Optional[TrackInfo]:
        """Fetch the current track from Radio France's livemeta API."""
        url = f"https://api.radiofrance.fr/livemeta/pull/{station_id}"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                self.logger.debug(f"livemeta returned {response.status_code} for id={station_id}")
                return None

            data = response.json()
            steps = data.get("steps") or {}
            levels = data.get("levels") or []
            if not steps or not levels:
                return None

            # The first level tracks the live stream; its position points at
            # the track playing now.
            level = levels[0]
            items = level.get("items") or []
            if not items:
                return None
            pos = level.get("position")
            if pos is None or not (0 <= pos < len(items)):
                pos = len(items) - 1

            step = steps.get(items[pos]) or {}
            title = (step.get("title") or step.get("titre") or "").strip()
            artist = (
                step.get("authors")
                or step.get("interpreteMorceau")
                or step.get("performers")
                or ""
            ).strip()
            album = (step.get("titreAlbum") or step.get("album") or "").strip() or None

            if artist and title:
                return TrackInfo(
                    artist=self.normalize_artist(artist),
                    title=self.normalize_title(title),
                    album=album,
                )
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Error fetching livemeta id={station_id}: {e}")
        except ValueError as e:
            self.logger.debug(f"Error parsing livemeta JSON for id={station_id}: {e}")
        except Exception as e:
            self.logger.debug(f"Unexpected error fetching livemeta id={station_id}: {e}")

        return None

    def get_from_recenttracks(self) -> Optional[TrackInfo]:
        """Fallback for the main FIP station via RecentTracks.com."""
        try:
            url = "https://recenttracks.com/stations/fip/recently-played"
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                self.logger.debug("BeautifulSoup not available for RecentTracks.com parsing")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            for table in soup.find_all('table'):
                for row in table.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 3:
                        continue
                    time_cell = cells[0].get_text(strip=True)
                    artist = cells[1].get_text(strip=True)
                    title = cells[2].get_text(strip=True)
                    if artist.lower() in ['artist', 'time'] or title.lower() in ['title', 'time']:
                        continue
                    if not artist or not title:
                        continue
                    if ':' in time_cell and len(time_cell) <= 6:
                        return TrackInfo(
                            artist=self.normalize_artist(artist),
                            title=self.normalize_title(title),
                        )
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Error fetching from RecentTracks.com: {e}")
        except Exception as e:
            self.logger.debug(f"Unexpected error fetching from RecentTracks.com: {e}")

        return None
