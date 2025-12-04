import os
from pathlib import Path

# Base Direc# Paths
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
TRACK_LIST_PATH = BASE_DIR / "track_list.txt"
TRACK_LIST_FAILED_PATH = BASE_DIR / "failed_tracks.txt"
LOG_FILE = BASE_DIR / "download.log"

# Tool Configuration
# We are using spotdl which is installed in the venv
HIFI_PATH = "spotdl" 

# Download Settings
MAX_CONCURRENT_DOWNLOADS = 3
RATE_LIMIT_DELAY = 1.0  # Seconds between downloads
TIMEOUT_PER_TRACK = 300  # 5 minutes
MAX_RETRIES = 3               # Number of retries per track

# Quality Settings
ALLOW_QUALITY_FALLBACK = False  # User requested: "only downgrade when maximum frequency is not available" -> actually user said "only downgrade when max not available", implying True.
# Wait, user said: "ensure the most highest possible quality is being downloaded only downgrade when maximum frequency is not availble"
# So Fallback IS allowed, but only if Lossless fails.
ALLOW_QUALITY_FALLBACK = True 

# Supported Audio Formats (for cleanup/checking)
AUDIO_EXTENSIONS = {".flac", ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".opus"}

# CSV Import Settings
DEFAULT_CSV_NAME = "playlist.csv"
