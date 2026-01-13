"""Radio FIP station fetcher - works for all FIP thematic stations.

FIP stations use a consistent API pattern:
https://www.radiofrance.fr/fip/radio-{station-name}/api/songs

Available stations: jazz, rock, electro, pop, reggae, groove, metal, hip-hop, world, etc.
"""

import requests
from typing import Optional
try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo


class FIPFetcher(BaseStationFetcher):
    """Generic fetcher for Radio FIP stations.
    
    Works for all FIP thematic stations (jazz, rock, electro, pop, etc.)
    by using the station name in the API URL.
    """
    
    def __init__(self, station_name: str = "fip"):
        """
        Initialize FIP fetcher.
        
        Args:
            station_name: Name of the FIP station (e.g., "jazz", "rock", "hip-hop")
                         Defaults to "fip" for the main FIP station
        """
        super().__init__(station_name)
        self.station_name = station_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)',
            'Accept': 'application/json'
        })
        
        # Build API URL based on station name
        # Handle special cases like "fip" (main station) vs thematic stations
        if station_name == "fip":
            # Main FIP station - try Online Radio Box first, then API
            self.api_url = None
        elif station_name == "fiphiphop":
            # Legacy name for hip-hop
            self.api_url = "https://www.radiofrance.fr/fip/radio-hip-hop/api/songs"
        else:
            # Thematic station (jazz, rock, etc.)
            self.api_url = f"https://www.radiofrance.fr/fip/radio-{station_name}/api/songs"
    
    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Fetch currently playing track from Radio FIP.
        
        For main FIP station, tries Online Radio Box first.
        For thematic stations, uses the FIP API endpoint.
        """
        # Main FIP station - use Online Radio Box
        if self.station_name == "fip":
            track_info = self.get_from_onlineradiobox("fr/fip")
            if track_info:
                return track_info
            # Could add fallback to FIP API here if needed
            return None
        
        # Thematic stations - use FIP API
        if not self.api_url:
            self.logger.warning(f"No API URL configured for station: {self.station_name}")
            return None
        
        try:
            response = self.session.get(self.api_url, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    track_info = self._parse_api_response(data)
                    if track_info:
                        self.logger.debug(f"Found track via API: {track_info}")
                        return track_info
                except ValueError as e:
                    self.logger.debug(f"Error parsing JSON response: {e}")
            else:
                self.logger.debug(f"API returned status {response.status_code} for {self.api_url}")
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Error fetching from FIP API: {e}")
        except Exception as e:
            self.logger.debug(f"Unexpected error: {e}")
        
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
        
        return None
