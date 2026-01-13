"""Flask web application for personal radio scrobbler."""

import logging
from typing import Optional
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

try:
    from src.personal_scrobbler import PersonalScrobbler, ScrobblerStatus
    from src.scrobbler import STATION_FETCHERS
except ImportError:
    from personal_scrobbler import PersonalScrobbler, ScrobblerStatus
    from scrobbler import STATION_FETCHERS

logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static')
CORS(app)  # Enable CORS for API endpoints

# Global scrobbler instance (initialized in web_main.py)
# This will be set by web_main.py before starting the Flask app
scrobbler: Optional[PersonalScrobbler] = None


@app.route('/')
def index():
    """Serve main HTML interface."""
    return render_template('index.html')


@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Get list of available stations."""
    stations = list(STATION_FETCHERS.keys())
    return jsonify({
        'stations': sorted(stations),
        'count': len(stations)
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current scrobbler status."""
    if scrobbler is None:
        return jsonify({
            'error': 'Scrobbler not initialized'
        }), 500
    
    status = scrobbler.get_status()
    
    return jsonify({
        'is_active': status.is_active,
        'station_name': status.station_name,
        'current_track': {
            'artist': status.current_track.artist if status.current_track else None,
            'title': status.current_track.title if status.current_track else None,
        } if status.current_track else None,
        'last_scrobbled': {
            'artist': status.last_scrobbled.artist if status.last_scrobbled else None,
            'title': status.last_scrobbled.title if status.last_scrobbled else None,
        } if status.last_scrobbled else None,
        'error': status.error
    })


@app.route('/api/start', methods=['POST'])
def start_scrobbling():
    """Start scrobbling a station."""
    if scrobbler is None:
        return jsonify({
            'error': 'Scrobbler not initialized'
        }), 500
    
    data = request.get_json()
    if not data or 'station' not in data:
        return jsonify({
            'error': 'Missing station parameter'
        }), 400
    
    station_name = data['station']
    
    success = scrobbler.start(station_name)
    
    if success:
        return jsonify({
            'success': True,
            'message': f'Started scrobbling {station_name}'
        })
    else:
        status = scrobbler.get_status()
        return jsonify({
            'success': False,
            'error': status.error or 'Failed to start scrobbling'
        }), 400


@app.route('/api/stop', methods=['POST'])
def stop_scrobbling():
    """Stop scrobbling."""
    if scrobbler is None:
        return jsonify({
            'error': 'Scrobbler not initialized'
        }), 500
    
    scrobbler.stop()
    
    return jsonify({
        'success': True,
        'message': 'Stopped scrobbling'
    })


@app.route('/api/emergency-stop', methods=['POST'])
def emergency_stop():
    """Emergency stop - immediately halt all scrobbling."""
    if scrobbler is None:
        return jsonify({
            'error': 'Scrobbler not initialized'
        }), 500
    
    scrobbler.emergency_stop()
    
    return jsonify({
        'success': True,
        'message': 'Emergency stop activated - all scrobbling halted'
    })


if __name__ == '__main__':
    # This is for development only
    # Production should use web_main.py
    app.run(debug=True, host='0.0.0.0', port=5000)
