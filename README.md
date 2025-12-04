# 🎵 FLAC Bulk Downloader

A high-performance, web-based tool to bulk download FLAC lossless music tracks from Spotify playlists.

## ✨ Features

- **🚀 Async & Fast**: Downloads multiple tracks in parallel (default: 3 concurrent).
- **🛡️ Reliable**: Uses **spot-dl** to fetch high-quality audio from YouTube Music.
- **🎛️ Queue System**: Upload multiple CSV playlists to build a download queue.
- **📊 Modern Web UI**: Beautiful, dark-themed interface with real-time progress and logs.
- **💎 High Quality**: Downloads best available audio (M4A/Opus ~256kbps, equivalent to high-quality MP3).
- **🧹 Smart Cleanup**: Integrated duplicate removal tool.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/instax-dutta/flac_bulk_download.git
cd flac_bulk_download

# Run the setup script (creates venv and installs dependencies)
python3 setup.py
```

### 2. Usage

Start the web application:

```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the app
python3 app.py
```

Then open **http://127.0.0.1:5000** in your browser.

**Web Interface Workflow:**
1.  **Upload Playlist**: Drag & drop your `playlist.csv` (from Exportify) to add tracks to the queue.
2.  **Start Download**: Click "Start Download" to begin processing the queue in the background.
3.  **Manage Files**: View downloaded files and download them to your computer.
4.  **Cleanup**: Use the "Cleanup Duplicates" button to remove duplicate files from storage.

### 3. Configuration (`config.py`)

Customize the tool behavior by editing `config.py`:

```python
# Number of parallel downloads
MAX_CONCURRENT_DOWNLOADS = 3

# Quality Settings
# 'm4a' is the best native quality from YouTube Music (AAC 256kbps).
# You can change this to 'mp3' or 'flac' (note: flac is converted, not native).
PREFERRED_QUALITY = "m4a"
```

## 📁 File Structure

- `app.py`: The Flask web application.
- `async_downloader.py`: The core async download engine.
- `extract_tracks.py`: CSV parser logic.
- `config.py`: Configuration settings.
- `state.py`: Global state management.
- `utils.py`: Helper functions.
- `downloads/`: Where your music goes.
- `templates/`: HTML templates for the UI.

## ⚠️ Disclaimer

This tool is for educational purposes only. Please respect copyright laws and support artists by purchasing their music.