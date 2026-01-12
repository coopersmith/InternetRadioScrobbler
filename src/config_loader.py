"""Configuration loader for station settings."""

import yaml
import os
import json
from typing import List, Optional
from pathlib import Path

try:
    from .scrobbler import StationConfig
except ImportError:
    from scrobbler import StationConfig


def load_config(config_path: Optional[str] = None) -> List[StationConfig]:
    """
    Load station configurations from YAML file or environment variables.
    
    Priority:
    1. Environment variable STATIONS_CONFIG (JSON or YAML string)
    2. Config file path (default: config/stations.yaml)
    
    Args:
        config_path: Path to YAML configuration file (optional)
        
    Returns:
        List of StationConfig objects
    """
    # First, try environment variable (for cloud deployment)
    stations_json = os.getenv('STATIONS_CONFIG')
    if stations_json:
        try:
            # Try JSON first
            config_data = json.loads(stations_json)
            return _parse_config_data(config_data)
        except json.JSONDecodeError:
            # Try as YAML string
            try:
                config_data = yaml.safe_load(stations_json)
                return _parse_config_data(config_data)
            except Exception as e:
                raise ValueError(f"Failed to parse STATIONS_CONFIG environment variable: {e}")
    
    # Fall back to config file
    if config_path is None:
        config_path = 'config/stations.yaml'
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Either create the file or set STATIONS_CONFIG environment variable."
        )
    
    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return _parse_config_data(config_data)


def _parse_config_data(config_data: dict) -> List[StationConfig]:
    """Parse configuration data into StationConfig objects."""
    stations = []
    
    if 'stations' not in config_data:
        raise ValueError("Configuration must contain 'stations' key")
    
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
