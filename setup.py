#!/usr/bin/env python3
"""
Setup script for Spotify Playlist to FLAC Downloader
"""

import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def main():
    print("🎵 Spotify Playlist to FLAC Downloader Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install requirements
    if not install_requirements():
        return 1
    
    print("\n🚀 Setup complete!")
    print("\nNext steps:")
    print("1. Export your Spotify playlist as CSV using Exportify (https://exportify.net/)")
    print("2. Save the CSV file as 'playlist.csv' in this directory")
    print("3. Run: python3 extract_tracks_from_csv.py")
    print("4. Run: python3 download_flac_tracks.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
