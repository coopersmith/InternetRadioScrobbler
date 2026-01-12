#!/usr/bin/env python3
"""Main entry point for the radio scrobbler service."""

import argparse
import sys
from pathlib import Path

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from scrobbler import RadioScrobbler
from config_loader import load_config
from utils import setup_logging


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Radio Scrobbler - Scrobble tracks from radio stations to Last.fm'
    )
    parser.add_argument(
        '-c', '--config',
        default=None,
        help='Path to configuration file (default: config/stations.yaml or STATIONS_CONFIG env var)'
    )
    parser.add_argument(
        '-l', '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--log-file',
        help='Optional log file path'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = getattr(sys.modules['logging'], args.log_level)
    setup_logging(level=log_level, log_file=args.log_file)
    
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        logger.info(f"Loading configuration from {args.config}")
        stations = load_config(args.config)
        
        if not stations:
            logger.error("No stations configured")
            return 1
        
        logger.info(f"Loaded {len(stations)} station(s)")
        
        # Create scrobbler
        scrobbler = RadioScrobbler(stations)
        
        if not scrobbler.stations:
            logger.error("No enabled stations found")
            return 1
        
        logger.info(f"Starting scrobbler with {len(scrobbler.stations)} station(s)")
        
        # Run forever
        scrobbler.run_forever()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
