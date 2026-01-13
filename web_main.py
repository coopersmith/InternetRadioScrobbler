#!/usr/bin/env python3
"""Entry point for personal radio scrobbler web interface."""

import argparse
import os
import sys
import signal
import yaml
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from web_app import app
from src.personal_scrobbler import PersonalScrobbler
from src.utils import setup_logging


def load_personal_config(config_path=None):
    """Load personal scrobbler configuration."""
    if config_path is None:
        config_path = 'config/personal_scrobbler.yaml'
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Please copy config/personal_scrobbler.yaml.example to {config_path} and fill in your credentials."
        )
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Support environment variable substitution
    lastfm_config = config.get('lastfm', {})
    for key in ['username', 'api_key', 'api_secret', 'password', 'password_hash']:
        value = lastfm_config.get(key)
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            lastfm_config[key] = os.getenv(env_var, value)
    
    return {
        'lastfm': lastfm_config,
        'poll_interval': config.get('poll_interval', 30),
        'server': config.get('server', {
            'host': '0.0.0.0',
            'port': 5000
        })
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Personal Radio Scrobbler Web Interface'
    )
    parser.add_argument(
        '-c', '--config',
        default=None,
        help='Path to configuration file (default: config/personal_scrobbler.yaml)'
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
        # Load configuration - support environment variables for Railway deployment
        config = None
        if os.getenv('LASTFM_USERNAME'):
            # Use environment variables (Railway deployment)
            logger.info("Loading configuration from environment variables")
            lastfm_config = {
                'username': os.getenv('LASTFM_USERNAME'),
                'api_key': os.getenv('LASTFM_API_KEY'),
                'api_secret': os.getenv('LASTFM_API_SECRET'),
                'password': os.getenv('LASTFM_PASSWORD'),
                'password_hash': os.getenv('LASTFM_PASSWORD_HASH'),
            }
            config = {
                'lastfm': lastfm_config,
                'poll_interval': int(os.getenv('POLL_INTERVAL', '30')),
                'server': {
                    'host': os.getenv('HOST', '0.0.0.0'),
                    'port': int(os.getenv('PORT', '5000'))
                }
            }
        else:
            # Use config file (local development)
            logger.info(f"Loading configuration from {args.config or 'config/personal_scrobbler.yaml'}")
            config = load_personal_config(args.config)
        
        # Initialize personal scrobbler
        lastfm_config = config['lastfm']
        scrobbler = PersonalScrobbler(
            lastfm_username=lastfm_config['username'],
            lastfm_api_key=lastfm_config['api_key'],
            lastfm_api_secret=lastfm_config['api_secret'],
            lastfm_password=lastfm_config.get('password'),
            lastfm_password_hash=lastfm_config.get('password_hash'),
            poll_interval=config['poll_interval']
        )
        
        # Set global scrobbler instance for Flask routes
        import web_app
        web_app.scrobbler = scrobbler
        
        # Get server config
        # Railway and other platforms use PORT environment variable
        server_config = config['server']
        host = server_config.get('host', '0.0.0.0')
        port = int(os.getenv('PORT', server_config.get('port', 5000)))
        
        logger.info(f"Starting web server on {host}:{port}")
        logger.info(f"Access the interface at http://localhost:{port}")
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Shutting down...")
            scrobbler.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run Flask app
        app.run(host=host, port=port, debug=False)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        if 'scrobbler' in locals():
            scrobbler.stop()
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
