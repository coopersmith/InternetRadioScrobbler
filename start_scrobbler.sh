#!/bin/bash
# Start the radio scrobbler service

cd "$(dirname "$0")"
source venv/bin/activate

# Run the scrobbler
python3 main.py -c config/stations.yaml -l INFO --log-file logs/scrobbler.log
