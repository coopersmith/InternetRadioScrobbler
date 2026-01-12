"""Radio FIP station fetcher."""

import requests
from typing import Optional
try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo


class FIPFetcher(BaseStationFetcher):
    """Fetcher for Radio FIP (France Inter Paris)."""
    
    # Radio FIP API endpoint - this may need to be adjusted based on actual API
    API_URL = "https://www.fip.fr/latest/api/graphql"
    
    # Alternative: Try the JSON endpoint that many radio stations use
    JSON_URL = "https://www.fip.fr/latest/api/graphql"
    
    def __init__(self):
        super().__init__("fip")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)'
        })
    
    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Fetch currently playing track from Radio FIP.
        
        Uses Online Radio Box playlist page as the primary source.
        """
        # Try Online Radio Box first (most reliable)
        track_info = self.get_from_onlineradiobox("fr/fip")
        if track_info:
            return track_info
        
        # Fallback: Try FIP's own API
        try:
            # Try GraphQL query for current track
            query = """
            {
                now {
                    firstLine
                    secondLine
                    start
                    end
                }
            }
            """
            
            response = self.session.post(
                self.API_URL,
                json={"query": query},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and 'now' in data['data']:
                now = data['data']['now']
                artist = now.get('firstLine', '').strip()
                title = now.get('secondLine', '').strip()
                
                if artist and title:
                    return TrackInfo(
                        artist=self.normalize_artist(artist),
                        title=self.normalize_title(title)
                    )
            
            # Fallback: Try alternative endpoint format
            return self._try_alternative_endpoint()
            
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Error fetching FIP track from API: {e}")
            return None
        except Exception as e:
            self.logger.debug(f"Unexpected error fetching FIP track: {e}")
            return None
    
    def _try_alternative_endpoint(self) -> Optional[TrackInfo]:
        """Try alternative API endpoints."""
        # Common pattern: JSON endpoint with current track
        alternative_urls = [
            "https://www.fip.fr/latest/api/graphql?operationName=Now&variables={}&extensions={}",
            "https://www.fip.fr/latest/api/graphql",
        ]
        
        for url in alternative_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # Try to extract track info from various possible structures
                    if isinstance(data, dict):
                        # Look for common field names
                        for key in ['now', 'current', 'track', 'playing']:
                            if key in data:
                                track_data = data[key]
                                if isinstance(track_data, dict):
                                    artist = track_data.get('artist') or track_data.get('firstLine') or track_data.get('artistName', '')
                                    title = track_data.get('title') or track_data.get('secondLine') or track_data.get('trackName', '')
                                    
                                    if artist and title:
                                        return TrackInfo(
                                            artist=self.normalize_artist(str(artist)),
                                            title=self.normalize_title(str(title))
                                        )
            except Exception:
                continue
        
        return None
