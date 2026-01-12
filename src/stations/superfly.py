"""Superfly radio station fetcher."""

import requests
import re
from typing import Optional
try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo


class SuperflyFetcher(BaseStationFetcher):
    """Fetcher for Superfly radio."""
    
    def __init__(self):
        super().__init__("superfly")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)'
        })
    
    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Fetch currently playing track from Superfly.
        
        Uses Online Radio Box playlist page as the source.
        """
        # Use Online Radio Box (most reliable)
        track_info = self.get_from_onlineradiobox("at/983superflyfm")
        if track_info:
            return track_info
        
        self.logger.warning("Could not fetch track from Superfly")
        return None
    
    def _scrape_player_page(self) -> Optional[TrackInfo]:
        """Scrape track info from the Superfly player page."""
        try:
            response = self.session.get("https://superfly.fm/player/", timeout=10)
            if response.status_code == 200:
                html = response.text
                
                # Try to find track info in various formats
                # Look for JSON data embedded in script tags
                json_patterns = [
                    r'"artist"\s*:\s*"([^"]+)"',
                    r'"title"\s*:\s*"([^"]+)"',
                    r'"track"\s*:\s*"([^"]+)"',
                    r'"song"\s*:\s*"([^"]+)"',
                ]
                
                # Look for HTML patterns
                # Example: <div class="artist">Artist Name</div>
                artist_patterns = [
                    r'<[^>]*class="[^"]*artist[^"]*"[^>]*>([^<]+)</',
                    r'<[^>]*id="[^"]*artist[^"]*"[^>]*>([^<]+)</',
                    r'data-artist="([^"]+)"',
                ]
                
                title_patterns = [
                    r'<[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</',
                    r'<[^>]*id="[^"]*title[^"]*"[^>]*>([^<]+)</',
                    r'data-title="([^"]+)"',
                    r'<[^>]*class="[^"]*track[^"]*"[^>]*>([^<]+)</',
                ]
                
                artist = None
                title = None
                
                # Try to extract from HTML
                for pattern in artist_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        artist = match.group(1).strip()
                        break
                
                for pattern in title_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                        break
                
                if artist and title:
                    return TrackInfo(
                        artist=self.normalize_artist(artist),
                        title=self.normalize_title(title)
                    )
                
                self.logger.debug("Could not extract track info from HTML")
        except Exception as e:
            self.logger.debug(f"Error scraping player page: {e}")
        
        self.logger.warning("Could not fetch track from Superfly - may need API endpoint update")
        return None
    
    def _parse_response(self, data: dict) -> Optional[TrackInfo]:
        """Parse API response to extract track info."""
        # Try various common field names
        artist = None
        title = None
        
        # Common patterns
        if 'artist' in data:
            artist = data['artist']
        elif 'artistName' in data:
            artist = data['artistName']
        elif 'current' in data and isinstance(data['current'], dict):
            artist = data['current'].get('artist') or data['current'].get('artistName')
        
        if 'title' in data:
            title = data['title']
        elif 'track' in data:
            title = data['track']
        elif 'trackName' in data:
            title = data['trackName']
        elif 'current' in data and isinstance(data['current'], dict):
            title = data['current'].get('title') or data['current'].get('track') or data['current'].get('trackName')
        
        if artist and title:
            return TrackInfo(
                artist=self.normalize_artist(str(artist)),
                title=self.normalize_title(str(title))
            )
        
        return None
