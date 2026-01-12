#!/bin/bash
# Run scrobbler in background (no Docker needed)

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

# Check if already running
if pgrep -f "python3 main.py" > /dev/null; then
    echo "Scrobbler is already running!"
    exit 1
fi

# Run in background
echo "Starting radio scrobbler in background..."
nohup python3 main.py -c config/stations.yaml -l INFO --log-file logs/scrobbler.log > /dev/null 2>&1 &

echo "Scrobbler started! PID: $!"
echo "View logs: tail -f logs/scrobbler.log"
echo "Stop: pkill -f 'python3 main.py'"
