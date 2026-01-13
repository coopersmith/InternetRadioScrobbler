// Personal Radio Scrobbler Frontend

let pollInterval = null;
const STATUS_POLL_INTERVAL = 3000; // Poll status every 3 seconds

// DOM elements
const stationSelect = document.getElementById('station-select');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const emergencyStopBtn = document.getElementById('emergency-stop-btn');
const statusText = document.getElementById('status-text');
const statusDot = document.querySelector('.status-dot');
const currentTrackDiv = document.getElementById('current-track');
const lastScrobbledDiv = document.getElementById('last-scrobbled');
const errorMessage = document.getElementById('error-message');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadStations();
    setupEventListeners();
    startStatusPolling();
});

function setupEventListeners() {
    startBtn.addEventListener('click', handleStart);
    stopBtn.addEventListener('click', handleStop);
    emergencyStopBtn.addEventListener('click', handleEmergencyStop);
    stationSelect.addEventListener('change', () => {
        // Enable start button when station is selected
        startBtn.disabled = !stationSelect.value;
    });
}

async function loadStations() {
    try {
        const response = await fetch('/api/stations');
        const data = await response.json();
        
        // Clear loading option
        stationSelect.innerHTML = '<option value="">Select a station...</option>';
        
        // Add stations
        data.stations.forEach(station => {
            const option = document.createElement('option');
            option.value = station;
            option.textContent = formatStationName(station);
            stationSelect.appendChild(option);
        });
        
        stationSelect.disabled = false;
        startBtn.disabled = false;
        
    } catch (error) {
        console.error('Failed to load stations:', error);
        showError('Failed to load stations. Please refresh the page.');
    }
}

function formatStationName(station) {
    // Convert "fipjazz" to "FIP Jazz", "superfly" to "Superfly", etc.
    return station
        .replace(/fip/g, 'FIP ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
}

async function handleStart() {
    const station = stationSelect.value;
    if (!station) {
        showError('Please select a station');
        return;
    }
    
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ station }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateUI();
        } else {
            showError(data.error || 'Failed to start scrobbling');
        }
    } catch (error) {
        console.error('Failed to start:', error);
        showError('Failed to start scrobbling. Please try again.');
    }
}

async function handleStop() {
    try {
        const response = await fetch('/api/stop', {
            method: 'POST',
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateUI();
        }
    } catch (error) {
        console.error('Failed to stop:', error);
        showError('Failed to stop scrobbling. Please try again.');
    }
}

async function handleEmergencyStop() {
    if (!confirm('Are you sure you want to EMERGENCY STOP? This will immediately halt all scrobbling.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/emergency-stop', {
            method: 'POST',
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Emergency stop activated! All scrobbling has been halted.');
            updateUI();
        }
    } catch (error) {
        console.error('Failed to emergency stop:', error);
        showError('Failed to emergency stop. Please try again.');
    }
}

function startStatusPolling() {
    // Poll status every few seconds
    pollInterval = setInterval(updateStatus, STATUS_POLL_INTERVAL);
    updateStatus(); // Initial update
}

function stopStatusPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        // Update status indicator
        if (data.is_active) {
            statusDot.classList.remove('inactive');
            statusDot.classList.add('active');
            statusText.textContent = `Scrobbling: ${formatStationName(data.station_name)}`;
            stopBtn.disabled = false;
            emergencyStopBtn.disabled = false;
            startBtn.disabled = true;
            stationSelect.disabled = true;
        } else {
            statusDot.classList.remove('active');
            statusDot.classList.add('inactive');
            statusText.textContent = 'Not scrobbling';
            stopBtn.disabled = true;
            emergencyStopBtn.disabled = true;
            startBtn.disabled = !stationSelect.value;
            stationSelect.disabled = false;
        }
        
        // Update current track
        if (data.current_track && data.current_track.artist && data.current_track.title) {
            document.getElementById('track-artist').textContent = data.current_track.artist;
            document.getElementById('track-title').textContent = data.current_track.title;
            currentTrackDiv.classList.remove('hidden');
        } else {
            currentTrackDiv.classList.add('hidden');
        }
        
        // Update last scrobbled
        if (data.last_scrobbled && data.last_scrobbled.artist && data.last_scrobbled.title) {
            document.getElementById('scrobbled-artist').textContent = data.last_scrobbled.artist;
            document.getElementById('scrobbled-title').textContent = data.last_scrobbled.title;
            lastScrobbledDiv.classList.remove('hidden');
        } else {
            lastScrobbledDiv.classList.add('hidden');
        }
        
        // Clear error if status is good
        if (!data.error) {
            hideError();
        }
        
    } catch (error) {
        console.error('Failed to update status:', error);
    }
}

function updateUI() {
    // Trigger immediate status update
    updateStatus();
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}
