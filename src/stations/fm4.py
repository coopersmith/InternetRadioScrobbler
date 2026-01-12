"""ORF FM4 radio station fetcher."""

import requests
from typing import Optional
try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo


class FM4Fetcher(BaseStationFetcher):
    """Fetcher for ORF FM4 radio."""
    
    def __init__(self):
        super().__init__("fm4")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)'
        })
    
    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Fetch currently playing track from ORF FM4.
        
        Uses Online Radio Box playlist page as the primary source.
        """
        # Try Online Radio Box first (most reliable)
        track_info = self.get_from_onlineradiobox("at/fm4")
        if track_info:
            return track_info
        
        # Fallback: Try ORF FM4's own API endpoints
        endpoints = [
            "https://audioapi.orf.at/fm4/api/json/current/live",
            "https://api.orf.at/fm4/now-playing",
            "https://fm4.orf.at/api/now-playing",
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
        
        self.logger.warning("Could not fetch track from FM4")
        return None
    
    def _parse_response(self, data: dict) -> Optional[TrackInfo]:
        """Parse API response to extract track info."""
        artist = None
        title = None
        
        # ORF FM4 common structure
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        
        if 'artist' in data:
            artist = data['artist']
        elif 'interpret' in data:  # German for artist
            artist = data['interpret']
        elif 'interpreter' in data:
            artist = data['interpreter']
        elif 'current' in data and isinstance(data['current'], dict):
            artist = data['current'].get('artist') or data['current'].get('interpret')
        
        if 'title' in data:
            title = data['title']
        elif 'titel' in data:  # German for title
            title = data['titel']
        elif 'song' in data:
            title = data['song']
        elif 'current' in data and isinstance(data['current'], dict):
            title = data['current'].get('title') or data['current'].get('titel') or data['current'].get('song')
        
        if artist and title:
            return TrackInfo(
                artist=self.normalize_artist(str(artist)),
                title=self.normalize_title(str(title))
            )
        
        return None
