"""Ness Radio station fetcher."""

import requests
from typing import Optional
try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo


class NessFetcher(BaseStationFetcher):
    """Fetcher for Ness Radio."""
    
    def __init__(self):
        super().__init__("ness")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)'
        })
    
    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Fetch currently playing track from Ness Radio.
        
        Uses Online Radio Box playlist page as the source.
        """
        # Use Online Radio Box (most reliable)
        track_info = self.get_from_onlineradiobox("ma/ness")
        if track_info:
            return track_info
        
        self.logger.warning("Could not fetch track from Ness Radio")
        return None
