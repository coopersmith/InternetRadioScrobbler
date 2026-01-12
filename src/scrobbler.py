"""Main scrobbler service that orchestrates station polling and scrobbling."""

import logging
import time
from typing import Dict, Optional
from dataclasses import dataclass

try:
    from .lastfm_client import LastFMClient
    from .stations.base import BaseStationFetcher, TrackInfo
    from .stations.fip import FIPFetcher
    from .stations.superfly import SuperflyFetcher
    from .stations.fm4 import FM4Fetcher
    from .stations.kbco import KBCOFetcher
    from .stations.wnyc import WNYCFetcher
except ImportError:
    # Allow imports when running as a module
    from lastfm_client import LastFMClient
    from stations.base import BaseStationFetcher, TrackInfo
    from stations.fip import FIPFetcher
    from stations.superfly import SuperflyFetcher
    from stations.fm4 import FM4Fetcher
    from stations.kbco import KBCOFetcher
    from stations.wnyc import WNYCFetcher

logger = logging.getLogger(__name__)


# Station fetcher registry
STATION_FETCHERS = {
    'fip': FIPFetcher,
    'superfly': SuperflyFetcher,
    'fm4': FM4Fetcher,
    'kbco': KBCOFetcher,
    'wnyc': WNYCFetcher,
    'ness': NessFetcher,
}


@dataclass
class StationConfig:
    """Configuration for a single radio station."""
    name: str
    lastfm_username: str
    lastfm_api_key: str
    lastfm_api_secret: str
    lastfm_password_hash: Optional[str] = None
    lastfm_password: Optional[str] = None
    poll_interval: int = 30
    enabled: bool = True


class RadioScrobbler:
    """Main service that polls stations and scrobbles tracks to Last.fm."""
    
    def __init__(self, stations: list[StationConfig]):
        """
        Initialize the scrobbler service.
        
        Args:
            stations: List of station configurations
        """
        self.stations: Dict[str, StationConfig] = {}
        self.fetchers: Dict[str, BaseStationFetcher] = {}
        self.clients: Dict[str, LastFMClient] = {}
        self.last_tracks: Dict[str, Optional[TrackInfo]] = {}
        self.station_stats: Dict[str, dict] = {}
        
        # Initialize stations
        for station_config in stations:
            if not station_config.enabled:
                logger.info(f"Skipping disabled station: {station_config.name}")
                continue
            
            self._initialize_station(station_config)
    
    def _initialize_station(self, config: StationConfig):
        """Initialize a single station."""
        try:
            # Get fetcher class
            fetcher_class = STATION_FETCHERS.get(config.name.lower())
            if not fetcher_class:
                logger.error(f"Unknown station: {config.name}")
                return
            
            # Create fetcher
            fetcher = fetcher_class()
            self.fetchers[config.name] = fetcher
            
            # Create Last.fm client
            client = LastFMClient(
                username=config.lastfm_username,
                api_key=config.lastfm_api_key,
                api_secret=config.lastfm_api_secret,
                password_hash=config.lastfm_password_hash,
                password=config.lastfm_password
            )
            
            # Test connection
            if not client.test_connection():
                logger.error(f"Failed to connect to Last.fm for {config.name}")
                return
            
            self.clients[config.name] = client
            self.stations[config.name] = config
            self.last_tracks[config.name] = None
            self.station_stats[config.name] = {
                'scrobbles': 0,
                'errors': 0,
                'last_success': None,
            }
            
            logger.info(f"Initialized station: {config.name} -> {config.lastfm_username}")
            
        except Exception as e:
            logger.error(f"Error initializing station {config.name}: {e}")
    
    def poll_station(self, station_name: str) -> bool:
        """
        Poll a single station and scrobble if track changed.
        
        Args:
            station_name: Name of the station to poll
            
        Returns:
            True if successful, False otherwise
        """
        if station_name not in self.fetchers:
            logger.error(f"Station not found: {station_name}")
            return False
        
        try:
            fetcher = self.fetchers[station_name]
            client = self.clients[station_name]
            config = self.stations[station_name]
            
            # Fetch current track
            current_track = fetcher.get_current_track()
            
            if not current_track:
                logger.debug(f"No track currently playing on {station_name}")
                return False
            
            # Check if track changed
            last_track = self.last_tracks[station_name]
            if last_track and current_track == last_track:
                logger.debug(f"Track unchanged on {station_name}: {current_track}")
                return True
            
            # Scrobble new track
            success = client.scrobble(
                artist=current_track.artist,
                title=current_track.title,
                album=current_track.album
            )
            
            if success:
                self.last_tracks[station_name] = current_track
                self.station_stats[station_name]['scrobbles'] += 1
                self.station_stats[station_name]['last_success'] = time.time()
                logger.info(f"Scrobbled {station_name}: {current_track}")
                return True
            else:
                self.station_stats[station_name]['errors'] += 1
                logger.error(f"Failed to scrobble {station_name}: {current_track}")
                return False
                
        except Exception as e:
            self.station_stats[station_name]['errors'] += 1
            logger.error(f"Error polling station {station_name}: {e}", exc_info=True)
            return False
    
    def poll_all_stations(self):
        """Poll all enabled stations."""
        for station_name in self.stations.keys():
            self.poll_station(station_name)
    
    def run_forever(self):
        """Run the scrobbler service continuously."""
        logger.info("Starting radio scrobbler service...")
        
        # Calculate next poll times for each station
        next_polls = {}
        for station_name, config in self.stations.items():
            next_polls[station_name] = time.time()
        
        try:
            while True:
                current_time = time.time()
                
                # Poll stations that are due
                for station_name, config in self.stations.items():
                    if current_time >= next_polls[station_name]:
                        self.poll_station(station_name)
                        next_polls[station_name] = current_time + config.poll_interval
                
                # Sleep for a short interval before checking again
                sleep_time = min(
                    max(0, min(next_polls.values()) - time.time()),
                    1.0  # Don't sleep more than 1 second at a time
                )
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logger.info("Shutting down radio scrobbler service...")
        except Exception as e:
            logger.error(f"Fatal error in scrobbler service: {e}", exc_info=True)
            raise
    
    def get_stats(self) -> Dict[str, dict]:
        """Get statistics for all stations."""
        return self.station_stats.copy()
