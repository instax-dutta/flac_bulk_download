# FLAC Automation Scripts

Collection of scripts to automate downloading FLAC music tracks.

## 📁 Project Structure

```
flac_automation/
├── track_list.txt                    # Main list of tracks to download
├── downloads/                         # Downloaded FLAC files
├── raw data/                          # Original CSV files and utilities
├── auto_download_binimum.py          # Download from music.binimum.org
├── download_tracks_hifi.py           # Download using hifi (RECOMMENDED)
├── remove_duplicate_downloads.py     # Clean duplicate files
└── track_list_failed.txt            # Failed downloads with error messages
```

## 🎵 Download Tracks with hifi (RECOMMENDED)

### Setup

1. Install hifi:
```bash
git clone https://github.com/sachinsenal0x64/hifi.git
cd hifi
# Follow installation instructions in the repo
# Ensure 'hifi' command is in your PATH
```

2. Run the downloader:
```bash
python3 download_tracks_hifi.py
```

### Features

✅ **FLAC Lossless Format** - Automatically downloads in highest quality  
✅ **Immediate Removal** - Tracks removed from list after successful download  
✅ **Fallback Handling** - Tries 5 different command formats  
✅ **Error Logging** - Failed tracks saved to `track_list_failed.txt` with reasons  
✅ **2.5 Min Timeout** - Skips stuck downloads automatically  
✅ **Progress Tracking** - Shows download status in real-time  

## 🌐 Alternative: Download from music.binimum.org

```bash
python3 auto_download_binimum.py
```

- Uses Selenium browser automation
- Visual browser mode (non-headless)
- Processes all tracks automatically
- 2.5 minute timeout per track

## 🧹 Remove Duplicate Downloads

```bash
python3 remove_duplicate_downloads.py
```

Compares file content (SHA-256) and removes duplicates while keeping one copy.

## 📝 File Formats

### track_list.txt
```
Allah Duhai Hai - Amit Mishra
Control - Armaan Malik
Hate The Way - Rameet Sandhu
...
```

### track_list_failed.txt
```
Some Song - Artist Name
  Error: Timeout (150s)

Another Song - Artist Name
  Error: Not found
...
```

## 🔧 Scripts Overview

| Script | Purpose | Format | Auto-Remove |
|--------|---------|--------|-------------|
| `download_tracks_hifi.py` | **Main downloader** (hifi) | FLAC | ✅ Yes |
| `auto_download_binimum.py` | Browser automation | FLAC | ❌ No |
| `remove_duplicate_downloads.py` | Cleanup | - | - |

## 💡 Tips

- **Resume downloads**: Just run the script again - it only processes remaining tracks
- **Retry failed**: Copy tracks from `track_list_failed.txt` back to `track_list.txt`
- **Monitor progress**: Watch the downloads/ folder for new FLAC files
- **Interrupt safely**: Ctrl+C will stop gracefully and save progress

## 🚀 Quick Start

```bash
# 1. Ensure hifi is installed
hifi --help

# 2. Run downloader
python3 download_tracks_hifi.py

# 3. Clean duplicates
python3 remove_duplicate_downloads.py
```

---
**Total Tracks**: Check `track_list.txt` line count  
**Downloaded**: Check `downloads/` folder  
**Failed**: Check `track_list_failed.txt`

