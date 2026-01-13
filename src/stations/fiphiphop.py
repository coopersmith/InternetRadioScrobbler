"""Radio FIP Hip-Hop station fetcher.

NOTE: Radio France loads track data dynamically via JavaScript.
To find the API endpoint:
1. Open https://www.radiofrance.fr/fip/radio-hip-hop in a browser
2. Open Developer Tools (F12) -> Network tab
3. Filter by XHR/Fetch
4. Look for API calls that return track data (JSON responses)
5. Share the endpoint URL and we'll update this fetcher

Once we have the endpoint, update the API_URLS list below.
"""

import requests
from typing import Optional
try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo


class FIPHipHopFetcher(BaseStationFetcher):
    """Fetcher for Radio FIP Hip-Hop."""
    
    # API endpoint discovered from browser Network tab
    API_URLS = [
        "https://www.radiofrance.fr/fip/radio-hip-hop/api/songs",
    ]
    
    def __init__(self):
        super().__init__("fiphiphop")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)',
            'Accept': 'application/json'
        })
    
    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Fetch currently playing track from Radio FIP Hip-Hop.
        
        Currently returns None until API endpoint is discovered.
        See module docstring for instructions on finding the endpoint.
        """
        if not self.API_URLS:
            self.logger.warning(
                "FIP Hip-Hop API endpoint not configured. "
                "See src/stations/fiphiphop.py for instructions on finding the endpoint."
            )
            return None
        
        # Try each API endpoint
        for url in self.API_URLS:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        track_info = self._parse_api_response(data)
                        if track_info:
                            self.logger.info(f"Found track via API: {track_info}")
                            return track_info
                    except ValueError:
                        continue
            except requests.exceptions.RequestException:
                continue
            except Exception as e:
                self.logger.debug(f"Error trying {url}: {e}")
                continue
        
        self.logger.warning("Could not fetch track from FIP Hip-Hop - API endpoint may need update")
        return None
    
    def _parse_api_response(self, data: dict) -> Optional[TrackInfo]:
        """Parse Radio France API response."""
        # The API returns a structure with a 'songs' array
        # The first song in the array is the currently playing track
        if 'songs' in data and isinstance(data['songs'], list) and len(data['songs']) > 0:
            current_song = data['songs'][0]
            artist = current_song.get('firstLine', '').strip()
            title = current_song.get('secondLine', '').strip()
            
            if artist and title:
                return TrackInfo(
                    artist=self.normalize_artist(artist),
                    title=self.normalize_title(title)
                )
        
        # Fallback: Try various other possible structures
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        
        # Common field patterns used by Radio France
        artist = None
        title = None
        
        # Check for nested structures
        if 'now' in data:
            now = data['now']
            artist = now.get('firstLine') or now.get('artist') or now.get('artistName')
            title = now.get('secondLine') or now.get('title') or now.get('trackName')
        elif 'current' in data:
            current = data['current']
            artist = current.get('firstLine') or current.get('artist') or current.get('artistName')
            title = current.get('secondLine') or current.get('title') or current.get('trackName')
        elif 'live' in data:
            live = data['live']
            artist = live.get('firstLine') or live.get('artist') or live.get('artistName')
            title = live.get('secondLine') or live.get('title') or live.get('trackName')
        else:
            # Direct fields
            artist = data.get('firstLine') or data.get('artist') or data.get('artistName')
            title = data.get('secondLine') or data.get('title') or data.get('trackName')
        
        if artist and title:
            return TrackInfo(
                artist=self.normalize_artist(str(artist)),
                title=self.normalize_title(str(title))
            )
        
        return None
