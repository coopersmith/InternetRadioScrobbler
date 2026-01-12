# Running on a Work Computer (No Docker)

Since Docker may not be available on work computers, here are simple alternatives:

## Quick Start (No Admin Rights Needed)

### Option 1: Run in Foreground (See what's happening)
```bash
cd /Users/coopersmith/radio-scrobbler
./run.sh
```

### Option 2: Run in Background (Keeps running)
```bash
cd /Users/coopersmith/radio-scrobbler
./run_background.sh
```

### Option 3: Manual Start
```bash
cd /Users/coopersmith/radio-scrobbler
source venv/bin/activate
python3 main.py -c config/stations.yaml -l INFO --log-file logs/scrobbler.log
```

## Managing the Background Process

**View logs:**
```bash
tail -f logs/scrobbler.log
```

**Check if running:**
```bash
pgrep -f "python3 main.py"
```

**Stop the scrobbler:**
```bash
pkill -f "python3 main.py"
```

## Auto-Start on Login (macOS)

If you want it to start automatically when you log in:

1. Create a Launch Agent:
```bash
mkdir -p ~/Library/LaunchAgents
```

2. Create `~/Library/LaunchAgents/com.radioscrobbler.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.radioscrobbler</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/coopersmith/radio-scrobbler/run_background.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

3. Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.radioscrobbler.plist
```

## Resource Usage

The scrobbler is lightweight:
- **CPU**: Minimal (< 1% when idle)
- **Memory**: ~50-100 MB
- **Network**: Small HTTP requests every 30 seconds
- **Disk**: Logs grow slowly (~1 MB per day)

## Troubleshooting

**If Python isn't available:**
- Check with: `python3 --version`
- If missing, you may need IT to install Python (or use Homebrew if allowed)

**If virtual environment fails:**
- Try: `python3 -m venv venv` manually
- Install dependencies: `pip install -r requirements.txt`

**If network requests fail:**
- Check if work firewall blocks `onlineradiobox.com` or `last.fm`
- May need to use VPN or request firewall exception

## Advantages Over Docker

- ✅ No admin rights needed
- ✅ No IT approval required
- ✅ Uses existing Python installation
- ✅ Easier to debug and modify
- ✅ Lower resource usage
- ✅ Works with work network restrictions
