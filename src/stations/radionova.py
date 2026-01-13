"""Radio Nova station fetcher."""

import requests
from typing import Optional
try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo


class RadioNovaFetcher(BaseStationFetcher):
    """Fetcher for Radio Nova using recenttracks.com."""
    
    def __init__(self):
        super().__init__("radionova")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)'
        })
    
    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Fetch currently playing track from Radio Nova.
        
        Uses recenttracks.com as the source. The page loads content dynamically,
        so we need to check all tables and find the one with actual track data.
        """
        try:
            url = "https://recenttracks.com/stations/radio-nova/recently-played"
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
                                        self.logger.debug(f"Found Radio Nova track: {artist} - {title}")
                                        return TrackInfo(
                                            artist=self.normalize_artist(artist),
                                            title=self.normalize_title(title)
                                        )
                                
                                # Also try rows without time validation (in case format differs)
                                if artist and title and len(artist) > 1 and len(title) > 1:
                                    # Make sure it's not a header
                                    if artist[0].isupper() or title[0].isupper():  # Likely a real track
                                        self.logger.debug(f"Found Radio Nova track (no time): {artist} - {title}")
                                        return TrackInfo(
                                            artist=self.normalize_artist(artist),
                                            title=self.normalize_title(title)
                                        )
                                        
                except ImportError:
                    self.logger.warning("BeautifulSoup not available for Radio Nova")
                except Exception as e:
                    self.logger.debug(f"Error parsing Radio Nova page: {e}")
            
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Error fetching Radio Nova: {e}")
        except Exception as e:
            self.logger.debug(f"Unexpected error fetching Radio Nova: {e}")
        
        self.logger.warning("Could not fetch track from Radio Nova")
        return None
