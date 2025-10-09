# 🎵 Spotify Playlist to FLAC Downloader

A Python tool to bulk download FLAC lossless music tracks from Spotify playlists for free using the Hifi API.

## ✨ Features

- **FLAC Lossless Quality**: Downloads tracks in 16-bit, 44.1 kHz FLAC format
- **Bulk Processing**: Handles entire playlists with hundreds of tracks
- **Automatic CSV Processing**: Extracts track information from Spotify export files
- **Smart Error Handling**: Continues processing even if some tracks fail
- **Progress Tracking**: Real-time progress updates and failure logging
- **No Account Required**: Uses free Hifi API (no Tidal subscription needed)
- **🌐 Web App Coming Soon**: User-friendly web interface for easy playlist management

## 🚀 Quick Start

### Step 1: Export Your Spotify Playlist

**🎯 Recommended: Use [Exportify](https://exportify.net/)**

[Exportify](https://exportify.net/) is the easiest and most reliable way to export your Spotify playlists:

1. **Visit [Exportify.net](https://exportify.net/)**
2. **Log in with your Spotify account** (secure OAuth authentication)
3. **Select your playlist** from the dropdown menu
4. **Click "Export"** to download the CSV file
5. **Save the file** as `playlist.csv` in this directory

**Alternative methods:**
- [Spotify Playlist Exporter](https://spotify-playlist-exporter.herokuapp.com/)
- Manual export from Spotify Web Player

### Step 2: Extract Track List

```bash
python3 extract_tracks_from_csv.py
```

This will:
- Read your `playlist.csv` file
- Extract track names and artists
- Create `track_list.txt` with format: "Song Title - Artist Name"
- Remove duplicates automatically

### Step 3: Download FLAC Tracks

```bash
python3 download_flac_tracks.py
```

This will:
- Process all tracks from `track_list.txt`
- Download each track in FLAC lossless quality
- Save files to `downloads/` directory
- Remove successfully downloaded tracks from the list
- Log failed downloads to `track_list_failed.txt`

## 📁 File Structure

```
flac_bulk_download/
├── extract_tracks_from_csv.py    # Extract tracks from CSV export
├── download_flac_tracks.py       # Main downloader (API-based)
├── download_tracks_hifi_cli.py   # Alternative CLI-based downloader
├── remove_duplicates.py          # Remove duplicate tracks
├── app.py                        # Web interface (optional)
├── requirements.txt              # Python dependencies
├── setup.py                      # Easy setup script
├── playlist.csv                  # Your exported Spotify playlist
├── track_list.txt               # Generated track list
├── track_list_failed.txt        # Failed downloads log
└── downloads/                   # Downloaded FLAC files
```

## 🛠️ Installation

### Prerequisites

- Python 3.7 or higher
- Internet connection

### Setup

1. **Clone this repository:**
```bash
   git clone https://github.com/instax-dutta/flac_bulk_download.git
   cd flac_bulk_download
   ```

2. **Install dependencies:**
   ```bash
   python3 setup.py
   ```
   Or manually:
```bash
   pip install -r requirements.txt
   ```

3. **Export your Spotify playlist:**
   - Use [Exportify](https://exportify.net/) to export your playlist as CSV
   - Save the CSV file as `playlist.csv` in this directory

## 📖 Usage Examples

### Basic Usage

```bash
# Extract tracks from your exported playlist
python3 extract_tracks_from_csv.py

# Download all tracks in FLAC format
python3 download_flac_tracks.py
```

### Advanced Usage

```bash
# Remove duplicate tracks before downloading
python3 remove_duplicates.py

# Use alternative CLI-based downloader (requires hifi tool)
python3 download_tracks_hifi_cli.py

# Start web interface for easier management
python3 app.py
```

## 🎯 Supported Export Formats

The tool works with CSV files exported from:

- **[Exportify](https://exportify.net/)** (recommended): Secure, reliable, and easy to use
- **Spotify Playlist Exporter**: https://spotify-playlist-exporter.herokuapp.com/
- **Spotify Web Player** (manual export)

### Required CSV Columns

Your CSV file should contain these columns:
- `Track Name` - The song title
- `Artist Name(s)` - Artist name(s), semicolon-separated for multiple artists

## 🔧 Configuration

### Download Quality

Edit `download_flac_tracks.py` to change quality:

```python
QUALITY = "LOSSLESS"  # Options: HI_RES_LOSSLESS, HI_RES, LOSSLESS, HIGH, LOW
```

### Timeout Settings

```python
TIMEOUT_PER_TRACK = 150  # 2.5 minutes per track
```

## 📊 Output

### Successful Downloads

- **Format**: FLAC lossless (16-bit, 44.1 kHz)
- **Location**: `downloads/` directory
- **Naming**: `Artist - Song Title.flac`

### Failed Downloads

- **Log File**: `track_list_failed.txt`
- **Format**: Track name + error message
- **Retry**: Re-run the script to retry failed downloads

## 🚨 Troubleshooting

### Common Issues

1. **"No tracks found in track_list.txt"**
   - Make sure you've run `extract_tracks_from_csv.py` first
   - Check that your CSV file is named `playlist.csv`

2. **"Track not available on Tidal"**
   - Some tracks may not be available on Tidal
   - Check `track_list_failed.txt` for details

3. **Download timeouts**
   - Increase `TIMEOUT_PER_TRACK` in the script
   - Check your internet connection

4. **API rate limiting**
   - The script includes delays between requests
   - If issues persist, increase the delay in the script

### Getting Help

- Check the `track_list_failed.txt` file for specific error messages
- Ensure your CSV file has the correct format
- Verify your internet connection

## ⚖️ Legal Notice

This tool is for educational and personal use only. Please respect copyright laws and the terms of service of the platforms involved. The authors are not responsible for any misuse of this software.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Hifi API](https://tidal.401658.xyz) for providing free access to Tidal's music library
- **[Exportify](https://exportify.net/)** for making Spotify playlist export easy and secure
- The open-source community for inspiration and support

## 🌐 Web App Coming Soon

We're working on a user-friendly web interface that will make the entire process even easier:

- **🎯 Drag & Drop**: Simply drag your CSV file to start processing
- **📊 Real-time Progress**: Visual progress bars and download statistics
- **🎵 Playlist Preview**: See your tracks before downloading
- **⚙️ Settings Panel**: Configure quality, timeouts, and other options
- **📱 Mobile Friendly**: Works on all devices
- **☁️ Cloud Processing**: No need to install anything locally

**Stay tuned for updates!** ⭐ Star this repository to get notified when the web app launches.

## 📈 Stats

- **Supported Formats**: FLAC Lossless, HI-RES, MQA
- **Quality**: Up to 24-bit, 192 kHz
- **File Sizes**: 30-140 MB per track (depending on quality)
- **Success Rate**: ~85-95% (varies by playlist content)

---

**Happy downloading! 🎵**

*Remember to support artists by purchasing their music when possible.*