"""Configuration loader for station settings."""

import yaml
import os
from typing import List
from pathlib import Path

try:
    from .scrobbler import StationConfig
except ImportError:
    from scrobbler import StationConfig


def load_config(config_path: str) -> List[StationConfig]:
    """
    Load station configurations from YAML file.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        List of StationConfig objects
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)
    
    stations = []
    
    if 'stations' not in config_data:
        raise ValueError("Configuration file must contain 'stations' key")
    
    for station_data in config_data['stations']:
        # Support environment variable substitution
        station_config = {}
        for key, value in station_data.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                # Environment variable substitution
                env_var = value[2:-1]
                station_config[key] = os.getenv(env_var, value)
            else:
                station_config[key] = value
        
        station = StationConfig(
            name=station_config['name'],
            lastfm_username=station_config['lastfm_username'],
            lastfm_api_key=station_config['lastfm_api_key'],
            lastfm_api_secret=station_config['lastfm_api_secret'],
            lastfm_password_hash=station_config.get('lastfm_password_hash'),
            lastfm_password=station_config.get('lastfm_password'),
            poll_interval=station_config.get('poll_interval', 30),
            enabled=station_config.get('enabled', True)
        )
        
        stations.append(station)
    
    return stations
