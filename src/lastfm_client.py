"""Last.fm API client wrapper."""

import logging
import time
from typing import Optional
import pylast

logger = logging.getLogger(__name__)


class LastFMClient:
    """Wrapper around pylast for Last.fm API interactions."""
    
    def __init__(self, username: str, api_key: str, api_secret: str, 
                 password_hash: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Last.fm client.
        
        Args:
            username: Last.fm username
            api_key: Last.fm API key
            api_secret: Last.fm API secret
            password_hash: MD5 hash of password (preferred)
            password: Plain text password (will be hashed if password_hash not provided)
        """
        self.username = username
        self.logger = logging.getLogger(f"{__name__}.{username}")
        
        # Create network object
        self.network = pylast.LastFMNetwork(
            api_key=api_key,
            api_secret=api_secret,
            username=username,
            password_hash=password_hash,
        )
        
        # If password_hash not provided but password is, hash it
        if not password_hash and password:
            import hashlib
            password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
            self.network = pylast.LastFMNetwork(
                api_key=api_key,
                api_secret=api_secret,
                username=username,
                password_hash=password_hash,
            )
        
        self._last_scrobble_time = 0
        self._min_scrobble_interval = 1  # Minimum seconds between scrobbles
    
    def scrobble(self, artist: str, title: str, timestamp: Optional[int] = None, 
                 album: Optional[str] = None) -> bool:
        """
        Scrobble a track to Last.fm.
        
        Args:
            artist: Artist name
            title: Track title
            timestamp: Unix timestamp (defaults to now)
            album: Album name (optional)
            
        Returns:
            True if scrobble was successful, False otherwise
        """
        try:
            # Rate limiting: ensure we don't scrobble too frequently
            current_time = time.time()
            if current_time - self._last_scrobble_time < self._min_scrobble_interval:
                time.sleep(self._min_scrobble_interval - (current_time - self._last_scrobble_time))
            
            if timestamp is None:
                timestamp = int(time.time())
            
            # Scrobble the track
            self.network.scrobble(
                artist=artist,
                title=title,
                timestamp=timestamp,
                album=album if album else None
            )
            
            self._last_scrobble_time = time.time()
            self.logger.info(f"Scrobbled: {artist} - {title}")
            return True
            
        except pylast.WSError as e:
            error_msg = str(e)
            self.logger.error(f"Last.fm API error: {error_msg}")
            # Check for common error types
            if "Invalid API key" in error_msg or "authentication failed" in error_msg.lower():
                self.logger.error("Check your Last.fm API credentials - authentication failed")
            elif "Malformed response" in error_msg:
                self.logger.error("Last.fm API returned malformed response - check credentials and network")
            return False
        except Exception as e:
            self.logger.error(f"Error scrobbling track: {e}", exc_info=True)
            return False
    
    def test_connection(self) -> bool:
        """
        Test the connection to Last.fm API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            user = self.network.get_user(self.username)
            # Try to get user info to verify authentication
            user.get_name()
            self.logger.info(f"Successfully connected to Last.fm as {self.username}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Last.fm: {e}")
            return False
