#!/bin/bash
# Simple launcher for the radio scrobbler (no Docker needed)

cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
fi

# Create logs directory
mkdir -p logs

# Run the scrobbler
echo "Starting radio scrobbler..."
echo "Logs will be written to logs/scrobbler.log"
echo "Press Ctrl+C to stop"
echo ""

python3 main.py -c config/stations.yaml -l INFO --log-file logs/scrobbler.log
