"""Radio FIP station fetcher - works for all FIP thematic stations.

FIP stations use a consistent API pattern:
https://www.radiofrance.fr/fip/radio-{station-name}/api/songs

Available stations: jazz, rock, electro, pop, reggae, groove, metal, hip-hop, world, etc.

For the main FIP station, uses recenttracks.com as primary source,
with fallback to Radio France API and Online Radio Box.
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
            # Main FIP station - try multiple sources
            # Possible API endpoints for main FIP station
            self.api_urls = [
                "https://www.radiofrance.fr/fip/api/songs",
                "https://www.radiofrance.fr/fip/radio-fip/api/songs",
            ]
        elif station_name == "fiphiphop":
            # Legacy name for hip-hop
            self.api_urls = ["https://www.radiofrance.fr/fip/radio-hip-hop/api/songs"]
        else:
            # Thematic station (jazz, rock, etc.)
            self.api_urls = [f"https://www.radiofrance.fr/fip/radio-{station_name}/api/songs"]
    
    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Fetch currently playing track from Radio FIP.
        
        For main FIP station, tries sources in order:
        1. RecentTracks.com (most reliable)
        2. Radio France API
        3. Online Radio Box (fallback)
        
        For thematic stations, uses the FIP API endpoint.
        """
        # Main FIP station - try multiple sources
        if self.station_name == "fip":
            # Try RecentTracks.com first
            track_info = self.get_from_recenttracks()
            if track_info:
                self.logger.debug("Found FIP track from RecentTracks.com")
                return track_info
            
            # Try Radio France API endpoints
            track_info = self.get_from_fip_api()
            if track_info:
                self.logger.debug("Found FIP track from Radio France API")
                return track_info
            
            # Fallback to Online Radio Box
            track_info = self.get_from_onlineradiobox("fr/fip")
            if track_info:
                self.logger.debug("Found FIP track from Online Radio Box")
                return track_info
            
            return None
        
        # Thematic stations - use FIP API
        if not self.api_urls:
            self.logger.warning(f"No API URL configured for station: {self.station_name}")
            return None
        
        return self.get_from_fip_api()
    
    def get_from_recenttracks(self) -> Optional[TrackInfo]:
        """
        Fetch current track from RecentTracks.com for FIP.
        
        Similar to RadioNovaFetcher, parses the HTML table to extract
        the most recent track.
        """
        try:
            url = "https://recenttracks.com/stations/fip/recently-played"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all tables - the track data might be in a different table
                    tables = soup.find_all('table')
                    
                    for table in tables:
                        rows = table.find_all('tr')
                        
                        # Look for rows with track data (skip header rows)
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            
                            if len(cells) >= 3:
                                time_cell = cells[0].get_text(strip=True)
                                artist = cells[1].get_text(strip=True)
                                title = cells[2].get_text(strip=True)
                                
                                # Skip header rows
                                if artist.lower() in ['artist', 'time'] or title.lower() in ['title', 'time']:
                                    continue
                                
                                # Skip if empty
                                if not artist or not title:
                                    continue
                                
                                # Check if time looks like a timestamp (HH:MM format)
                                # This helps identify actual track rows vs headers
                                if ':' in time_cell and len(time_cell) <= 6:
                                    # This looks like a real track row
                                    if artist and title:
                                        self.logger.debug(f"Found FIP track from RecentTracks.com: {artist} - {title}")
                                        return TrackInfo(
                                            artist=self.normalize_artist(artist),
                                            title=self.normalize_title(title)
                                        )
                                
                                # Also try rows without time validation (in case format differs)
                                if artist and title and len(artist) > 1 and len(title) > 1:
                                    # Make sure it's not a header
                                    if artist[0].isupper() or title[0].isupper():  # Likely a real track
                                        self.logger.debug(f"Found FIP track from RecentTracks.com (no time): {artist} - {title}")
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
    
    def get_from_fip_api(self) -> Optional[TrackInfo]:
        """
        Fetch current track from Radio France FIP API.
        
        Tries multiple API endpoints in order until one succeeds.
        """
        if not self.api_urls:
            return None
        
        for api_url in self.api_urls:
            try:
                response = self.session.get(api_url, timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        track_info = self._parse_api_response(data)
                        if track_info:
                            self.logger.debug(f"Found track via API ({api_url}): {track_info}")
                            return track_info
                    except ValueError as e:
                        self.logger.debug(f"Error parsing JSON response from {api_url}: {e}")
                        continue
                else:
                    self.logger.debug(f"API returned status {response.status_code} for {api_url}")
            except requests.exceptions.RequestException as e:
                self.logger.debug(f"Error fetching from FIP API ({api_url}): {e}")
                continue
            except Exception as e:
                self.logger.debug(f"Unexpected error fetching from {api_url}: {e}")
                continue
        
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
