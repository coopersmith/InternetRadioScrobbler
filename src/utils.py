"""Utility functions."""

import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def md5_hash(text: str) -> str:
    """Generate MD5 hash of a string."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None):
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
        log_file: Optional file path for logging
    """
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers
    )
