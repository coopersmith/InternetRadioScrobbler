"""Station fetchers for various radio stations."""

try:
    from .base import BaseStationFetcher, TrackInfo
except ImportError:
    from base import BaseStationFetcher, TrackInfo

__all__ = ['BaseStationFetcher', 'TrackInfo']
