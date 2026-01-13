"""Personal scrobbler service for web interface.

Manages scrobbling a single selected station to user's personal Last.fm account.
"""

import logging
import threading
import time
from typing import Optional, Dict
from dataclasses import dataclass

try:
    from .lastfm_client import LastFMClient
    from .stations.base import BaseStationFetcher, TrackInfo
    from .scrobbler import STATION_FETCHERS
except ImportError:
    from lastfm_client import LastFMClient
    from stations.base import BaseStationFetcher, TrackInfo
    from scrobbler import STATION_FETCHERS

logger = logging.getLogger(__name__)


@dataclass
class ScrobblerStatus:
    """Current status of the personal scrobbler."""
    is_active: bool
    station_name: Optional[str] = None
    current_track: Optional[TrackInfo] = None
    last_scrobbled: Optional[TrackInfo] = None
    error: Optional[str] = None


class PersonalScrobbler:
    """Manages scrobbling a selected station to user's personal Last.fm account."""
    
    def __init__(self, lastfm_username: str, lastfm_api_key: str, 
                 lastfm_api_secret: str, lastfm_password: Optional[str] = None,
                 lastfm_password_hash: Optional[str] = None,
                 poll_interval: int = 30,
                 max_consecutive_errors: int = 5,
                 auto_stop_on_errors: bool = True):
        """
        Initialize personal scrobbler.
        
        Args:
            lastfm_username: User's Last.fm username
            lastfm_api_key: Last.fm API key
            lastfm_api_secret: Last.fm API secret
            lastfm_password: Plain text password (optional)
            lastfm_password_hash: MD5 hash of password (optional)
            poll_interval: Seconds between polling attempts
            max_consecutive_errors: Auto-stop after this many consecutive errors
            auto_stop_on_errors: Whether to auto-stop on repeated errors
        """
        self.lastfm_client = LastFMClient(
            username=lastfm_username,
            api_key=lastfm_api_key,
            api_secret=lastfm_api_secret,
            password=lastfm_password,
            password_hash=lastfm_password_hash
        )
        
        self.poll_interval = poll_interval
        self.max_consecutive_errors = max_consecutive_errors
        self.auto_stop_on_errors = auto_stop_on_errors
        self._active_station: Optional[str] = None
        self._fetcher: Optional[BaseStationFetcher] = None
        self._last_track: Optional[TrackInfo] = None
        self._status = ScrobblerStatus(is_active=False)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._consecutive_errors = 0
        
        # Test connection
        if not self.lastfm_client.test_connection():
            logger.warning("Failed to connect to Last.fm - scrobbling may not work")
    
    def start(self, station_name: str) -> bool:
        """
        Start scrobbling a station.
        
        Args:
            station_name: Name of station to scrobble
            
        Returns:
            True if started successfully, False otherwise
        """
        with self._lock:
            if self._status.is_active:
                logger.warning(f"Already scrobbling {self._active_station}, stopping first")
                self.stop()
            
            # Validate station exists
            if station_name not in STATION_FETCHERS:
                error_msg = f"Unknown station: {station_name}"
                logger.error(error_msg)
                self._status.error = error_msg
                return False
            
            # Create fetcher instance
            try:
                fetcher_factory = STATION_FETCHERS[station_name]
                # Handle lambda functions (like fipjazz)
                if callable(fetcher_factory) and not isinstance(fetcher_factory, type):
                    fetcher = fetcher_factory()
                else:
                    fetcher = fetcher_factory()
                
                self._fetcher = fetcher
                self._active_station = station_name
                self._last_track = None
                self._status = ScrobblerStatus(
                    is_active=True,
                    station_name=station_name,
                    error=None
                )
                
                # Start background thread
                self._stop_event.clear()
                self._thread = threading.Thread(target=self._poll_loop, daemon=True)
                self._thread.start()
                
                logger.info(f"Started scrobbling station: {station_name}")
                return True
                
            except Exception as e:
                error_msg = f"Failed to start scrobbling: {e}"
                logger.error(error_msg, exc_info=True)
                self._status.error = error_msg
                return False
    
    def stop(self):
        """Stop scrobbling."""
        with self._lock:
            if not self._status.is_active:
                return
            
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=2.0)
            
            self._status.is_active = False
            self._active_station = None
            self._fetcher = None
            self._consecutive_errors = 0
            logger.info("Stopped scrobbling")
    
    def emergency_stop(self):
        """Emergency stop - immediately halt all scrobbling."""
        logger.warning("EMERGENCY STOP triggered")
        self.stop()
        with self._lock:
            self._status.error = "Emergency stop activated"
    
    def get_status(self) -> ScrobblerStatus:
        """Get current status."""
        with self._lock:
            return ScrobblerStatus(
                is_active=self._status.is_active,
                station_name=self._status.station_name,
                current_track=self._status.current_track,
                last_scrobbled=self._last_track,
                error=self._status.error
            )
    
    def _poll_loop(self):
        """Background polling loop."""
        logger.info(f"Polling loop started for {self._active_station}")
        
        while not self._stop_event.is_set():
            try:
                # Fetch current track
                current_track = self._fetcher.get_current_track()
                
                with self._lock:
                    self._status.current_track = current_track
                    self._status.error = None
                
                if current_track:
                    # Reset error counter on successful fetch
                    with self._lock:
                        self._consecutive_errors = 0
                    
                    # Check if track changed
                    if self._last_track and current_track == self._last_track:
                        logger.debug(f"Track unchanged: {current_track}")
                    else:
                        # Normalize for comparison
                        if self._last_track:
                            last_normalized = (
                                self._last_track.artist.lower().strip(),
                                self._last_track.title.lower().strip()
                            )
                            current_normalized = (
                                current_track.artist.lower().strip(),
                                current_track.title.lower().strip()
                            )
                            if last_normalized == current_normalized:
                                logger.debug(f"Track unchanged (normalized): {current_track}")
                            else:
                                # Scrobble new track
                                self._scrobble_track(current_track)
                        else:
                            # First track, scrobble it
                            self._scrobble_track(current_track)
                
                else:
                    logger.debug(f"No track currently playing on {self._active_station}")
                    # Reset error counter if we got None (not an error, just no track)
                    with self._lock:
                        self._consecutive_errors = 0
                
            except Exception as e:
                error_msg = f"Error polling station: {e}"
                logger.error(error_msg, exc_info=True)
                with self._lock:
                    self._status.error = error_msg
                    self._consecutive_errors += 1
                    
                    # Auto-stop if too many consecutive errors
                    if self.auto_stop_on_errors and self._consecutive_errors >= self.max_consecutive_errors:
                        logger.error(f"Too many consecutive errors ({self._consecutive_errors}). Auto-stopping scrobbler.")
                        self._status.error = f"Auto-stopped after {self._consecutive_errors} consecutive errors"
                        self._stop_event.set()
                        break
            
            # Wait for next poll or stop signal
            self._stop_event.wait(self.poll_interval)
        
        logger.info(f"Polling loop stopped for {self._active_station}")
    
    def _scrobble_track(self, track: TrackInfo):
        """Scrobble a track."""
        try:
            success = self.lastfm_client.scrobble(
                artist=track.artist,
                title=track.title,
                album=track.album
            )
            
            if success:
                self._last_track = track
                logger.info(f"Scrobbled: {track}")
            else:
                logger.warning(f"Failed to scrobble: {track}")
                
        except Exception as e:
            logger.error(f"Error scrobbling track: {e}", exc_info=True)
