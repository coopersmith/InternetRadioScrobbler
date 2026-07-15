"""Radio FIP station fetcher - works for the main FIP station and all its
thematic webradios (jazz, rock, electro, pop, reggae, groove, metal, hip-hop).

Data sources (Radio France's own API was retired and now 404s for every
webradio, so it is not used):

- Main ``fip``: recenttracks.com, with Online Radio Box as a fallback.
- Thematic webradios: Online Radio Box, e.g. ``fr/fipjazz`` for FIP Jazz.
  This is the same source the Superfly/FM4/Ness fetchers use.
"""

import requests
from typing import Optional
try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo


class FIPFetcher(BaseStationFetcher):
    """Generic fetcher for Radio FIP and its thematic webradios.

    Pass the bare genre for a thematic station (e.g. ``FIPFetcher('jazz')``),
    or nothing / ``'fip'`` for the main station.
    """

    def __init__(self, station_name: str = "fip"):
        super().__init__(station_name)
        self.station_name = station_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)',
            'Accept': 'application/json'
        })

        # Online Radio Box station path. FIP webradios are listed as
        # fr/fip<genre> (e.g. fr/fipjazz, fr/fiphiphop); the main station is
        # fr/fip.
        if station_name == "fip":
            self.onlineradiobox_path = "fr/fip"
        else:
            self.onlineradiobox_path = f"fr/fip{station_name}"

    def get_current_track(self) -> Optional[TrackInfo]:
        """Fetch the currently playing track from Radio FIP.

        Main FIP tries recenttracks.com first (most reliable), then Online
        Radio Box. Thematic webradios use Online Radio Box directly.
        """
        if self.station_name == "fip":
            track_info = self.get_from_recenttracks()
            if track_info:
                self.logger.debug("Found FIP track from RecentTracks.com")
                return track_info

        track_info = self.get_from_onlineradiobox(self.onlineradiobox_path)
        if track_info:
            self.logger.debug(
                f"Found FIP track from Online Radio Box ({self.onlineradiobox_path})"
            )
            return track_info

        self.logger.warning(f"Could not fetch track from FIP ({self.station_name})")
        return None

    def get_from_recenttracks(self) -> Optional[TrackInfo]:
        """Fetch the current track from RecentTracks.com for the main FIP station."""
        try:
            url = "https://recenttracks.com/stations/fip/recently-played"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # The track data lives in a table; find the first real row.
                    for table in soup.find_all('table'):
                        for row in table.find_all('tr'):
                            cells = row.find_all(['td', 'th'])
                            if len(cells) < 3:
                                continue

                            time_cell = cells[0].get_text(strip=True)
                            artist = cells[1].get_text(strip=True)
                            title = cells[2].get_text(strip=True)

                            # Skip header rows / empties.
                            if artist.lower() in ['artist', 'time'] or title.lower() in ['title', 'time']:
                                continue
                            if not artist or not title:
                                continue

                            # A real track row has a HH:MM timestamp.
                            if ':' in time_cell and len(time_cell) <= 6:
                                self.logger.debug(
                                    f"Found FIP track from RecentTracks.com: {artist} - {title}"
                                )
                                return TrackInfo(
                                    artist=self.normalize_artist(artist),
                                    title=self.normalize_title(title)
                                )

                            # Fallback for rows without a parseable time.
                            if len(artist) > 1 and len(title) > 1 and (artist[0].isupper() or title[0].isupper()):
                                self.logger.debug(
                                    f"Found FIP track from RecentTracks.com (no time): {artist} - {title}"
                                )
                                return TrackInfo(
                                    artist=self.normalize_artist(artist),
                                    title=self.normalize_title(title)
                                )
                except ImportError:
                    self.logger.debug("BeautifulSoup not available for RecentTracks.com parsing")
                except Exception as e:
                    self.logger.debug(f"Error parsing RecentTracks.com page: {e}")

        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Error fetching from RecentTracks.com: {e}")
        except Exception as e:
            self.logger.debug(f"Unexpected error fetching from RecentTracks.com: {e}")

        return None
