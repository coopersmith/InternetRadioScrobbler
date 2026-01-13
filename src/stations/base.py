"""Base class for radio station track fetchers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import logging
import requests
import re

logger = logging.getLogger(__name__)


@dataclass
class TrackInfo:
    """Information about a currently playing track."""
    artist: str
    title: str
    album: Optional[str] = None
    
    def __str__(self) -> str:
        if self.album:
            return f"{self.artist} - {self.title} ({self.album})"
        return f"{self.artist} - {self.title}"
    
    def __eq__(self, other) -> bool:
        """Compare tracks by artist and title only."""
        if not isinstance(other, TrackInfo):
            return False
        return (self.artist.lower() == other.artist.lower() and 
                self.title.lower() == other.title.lower())


class BaseStationFetcher(ABC):
    """Abstract base class for fetching current track info from radio stations."""
    
    def __init__(self, station_name: str):
        """
        Initialize the station fetcher.
        
        Args:
            station_name: Name of the radio station
        """
        self.station_name = station_name
        self.logger = logging.getLogger(f"{__name__}.{station_name}")
    
    @abstractmethod
    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Fetch the currently playing track from the station.
        
        Returns:
            TrackInfo if a track is currently playing, None otherwise
        """
        pass
    
    def normalize_artist(self, artist: str) -> str:
        """Normalize artist name (strip whitespace, etc.)."""
        return artist.strip()
    
    def normalize_title(self, title: str) -> str:
        """Normalize track title (strip whitespace, etc.)."""
        return title.strip()
    
    def get_from_onlineradiobox(self, station_path: str) -> Optional[TrackInfo]:
        """
        Get current track from Online Radio Box playlist page.
        
        Args:
            station_path: The station path on Online Radio Box (e.g., 'at/983superflyfm')
            
        Returns:
            TrackInfo if found, None otherwise
        """
        try:
            url = f"https://onlineradiobox.com/{station_path}/playlist/?lang=en"
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (compatible; RadioScrobbler/1.0)'
            })
            
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                # Look for the "Live" track in the playlist table
                # Pattern: | Live  | [Artist - Title](/track/...) |
                live_patterns = [
                    r'\| Live\s+\|.*?\[([^\]]+)\].*?\|',  # [Artist - Title]
                    r'\| Live\s+\|([^|]+)\|',  # Artist - Title (no link)
                    r'Live.*?\[([^\]]+)\]',  # More flexible
                ]
                
                for pattern in live_patterns:
                    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                    if match:
                        track_text = match.group(1).strip()
                        # Parse "Artist - Title" format
                        if ' - ' in track_text:
                            parts = track_text.split(' - ', 1)
                            artist = parts[0].strip()
                            title = parts[1].strip()
                            
                            # Clean up any HTML entities or extra characters
                            artist = re.sub(r'<[^>]+>', '', artist)
                            title = re.sub(r'<[^>]+>', '', title)
                            
                            if artist and title:
                                self.logger.debug(f"Found Live track from Online Radio Box: {artist} - {title}")
                                return TrackInfo(
                                    artist=self.normalize_artist(artist),
                                    title=self.normalize_title(title)
                                )
                
                # Alternative: Use BeautifulSoup if available
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find table rows
                    rows = soup.find_all('tr')
                    live_track = None
                    most_recent_track = None
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) < 2:
                            continue
                            
                        first_cell = cells[0].get_text(strip=True)
                        track_cell = cells[1]
                        
                        # Try to find link text or cell text
                        link = track_cell.find('a')
                        if link:
                            track_text = link.get_text(strip=True)
                        else:
                            track_text = track_cell.get_text(strip=True)
                        
                        # Skip non-music entries
                        if any(skip in track_text.lower() for skip in ['www.', 'podcast', 'jingle', 'programmation', 'shop', 'articles', 'empfiehlt', 'verrät', 'ist unser']):
                            continue
                        
                        # Remove extra info like "| FM4 Musik Podcast" or "| FM4 OKFM4"
                        if ' | ' in track_text:
                            track_text = track_text.split(' | ')[0].strip()
                        
                        if ' - ' not in track_text:
                            continue
                            
                        parts = track_text.split(' - ', 1)
                        artist = parts[0].strip()
                        title = parts[1].strip()
                        
                        # Skip if artist or title is too short (likely not a real track)
                        if len(artist) < 2 or len(title) < 2:
                            continue
                        
                        track_info = TrackInfo(
                            artist=self.normalize_artist(artist),
                            title=self.normalize_title(title)
                        )
                        
                        # Check for "Live" row first
                        if first_cell.lower() == 'live':
                            live_track = track_info
                            self.logger.debug(f"Found Live track via BeautifulSoup: {artist} - {title}")
                            break  # Live row takes priority
                        
                        # Track time-based rows (most recent track)
                        # Format: "HH:MM | Artist - Title"
                        elif first_cell and ':' in first_cell and len(first_cell) <= 6:
                            # Only use first time-based row as most recent
                            if most_recent_track is None:
                                most_recent_track = track_info
                    
                    # Return Live track if found, otherwise most recent
                    if live_track:
                        return live_track
                    elif most_recent_track:
                        self.logger.debug(f"Found most recent track via BeautifulSoup: {most_recent_track.artist} - {most_recent_track.title}")
                        return most_recent_track
                except ImportError:
                    # BeautifulSoup not available, continue with regex
                    pass
                
        except Exception as e:
            self.logger.debug(f"Error fetching from Online Radio Box ({station_path}): {e}")
        
        return None
