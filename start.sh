#!/bin/bash
# Railway start script - determines which service to run based on RAILWAY_SERVICE env var

if [ "$RAILWAY_SERVICE" = "web" ]; then
    echo "Starting web interface..."
    python3 web_main.py
else
    echo "Starting automated scrobbler..."
    python3 main.py -c config/stations.yaml -l INFO --log-file logs/scrobbler.log
fi
