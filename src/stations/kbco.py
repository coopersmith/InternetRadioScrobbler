"""KBCO radio station fetcher."""

import requests
from typing import Optional
try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo


class KBCOFetcher(BaseStationFetcher):
    """Fetcher for KBCO radio."""
    
    def __init__(self):
        super().__init__("kbco")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)'
        })
    
    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Fetch currently playing track from KBCO.
        
        Uses Online Radio Box playlist page as the primary source.
        """
        # Try Online Radio Box first (most reliable)
        track_info = self.get_from_onlineradiobox("us/kbco")
        if track_info:
            return track_info
        
        # Fallback: Try KBCO's own API endpoints
        endpoints = [
            "https://www.kbco.com/api/now-playing",
            "https://api.kbco.com/now-playing",
            "https://www.kbco.com/now-playing.json",
            "https://playerservices.streamtheworld.com/api/livestream?version=1.5&mount=KBCOFM_SC&lang=en",
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    track_info = self._parse_response(data)
                    if track_info:
                        return track_info
            except requests.exceptions.RequestException:
                continue
            except Exception as e:
                self.logger.debug(f"Error trying {endpoint}: {e}")
                continue
        
        self.logger.warning("Could not fetch track from KBCO")
        return None
    
    def _parse_response(self, data: dict) -> Optional[TrackInfo]:
        """Parse API response to extract track info."""
        artist = None
        title = None
        
        # Handle nested structures
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        
        # Common field patterns
        if 'artist' in data:
            artist = data['artist']
        elif 'artistName' in data:
            artist = data['artistName']
        elif 'current' in data and isinstance(data['current'], dict):
            artist = data['current'].get('artist') or data['current'].get('artistName')
        elif 'nowPlaying' in data and isinstance(data['nowPlaying'], dict):
            artist = data['nowPlaying'].get('artist') or data['nowPlaying'].get('artistName')
        
        if 'title' in data:
            title = data['title']
        elif 'track' in data:
            title = data['track']
        elif 'trackName' in data:
            title = data['trackName']
        elif 'song' in data:
            title = data['song']
        elif 'current' in data and isinstance(data['current'], dict):
            title = data['current'].get('title') or data['current'].get('track') or data['current'].get('trackName')
        elif 'nowPlaying' in data and isinstance(data['nowPlaying'], dict):
            title = data['nowPlaying'].get('title') or data['nowPlaying'].get('track') or data['nowPlaying'].get('trackName')
        
        if artist and title:
            return TrackInfo(
                artist=self.normalize_artist(str(artist)),
                title=self.normalize_title(str(title))
            )
        
        return None
