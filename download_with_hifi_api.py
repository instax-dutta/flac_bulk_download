#!/usr/bin/env python3
"""
Spotify Playlist to FLAC Downloader

Download tracks from track_list.txt using the Hifi REST API.
Converts Spotify playlists to FLAC lossless music files.

API: https://tidal.401658.xyz
Format: FLAC Lossless (16-bit, 44.1 kHz)

Usage:
  python3 download_flac_tracks.py
  
Features:
- Automatically processes all tracks from track_list.txt
- Downloads in FLAC LOSSLESS format (up to 24-bit, 192 kHz)
- 2.5 minute timeout per track
- Removes successfully downloaded tracks immediately
- Saves failed tracks to track_list_failed.txt with error details
- No account or subscription required

Requirements:
- Python 3.7+
- Internet connection
- CSV file exported from Spotify playlist (use Exportify)
"""

from __future__ import annotations

import requests
import sys
import time
import base64
import json
from pathlib import Path
from typing import List, Tuple, Optional
import urllib.parse

# Hifi API configuration
HIFI_API_BASE = "https://tidal.401658.xyz"
QUALITY = "LOSSLESS"  # Options: HI_RES_LOSSLESS, HI_RES, LOSSLESS, HIGH, LOW
TIMEOUT_PER_TRACK = 150  # 2.5 minutes


def read_track_list(path: Path) -> List[str]:
    """Read all tracks from track_list.txt"""
    if not path.exists():
        return []
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    return lines


def remove_track_from_file(path: Path, track: str) -> None:
    """Remove a single track from track_list.txt immediately"""
    all_lines = path.read_text(encoding="utf-8").splitlines()
    remaining = [l for l in all_lines if l.strip() != track]
    path.write_text("\n".join(remaining) + ("\n" if remaining else ""), encoding="utf-8")


def append_failure(path: Path, track: str, error: str) -> None:
    """Append a failed track with error message to track_list_failed.txt"""
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{track}\n")
        if error:
            f.write(f"  Error: {error}\n")
        f.write("\n")


def search_track(query: str) -> Optional[dict]:
    """
    Search for a track using the hifi API.
    Returns track info with ID if found, None otherwise.
    """
    try:
        # Use the /search/ endpoint
        url = f"{HIFI_API_BASE}/search/"
        params = {"s": query}
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract first track from results
        if data and "items" in data and len(data["items"]) > 0:
            track_info = data["items"][0]
            return {
                "id": track_info.get("id"),
                "title": track_info.get("title"),
                "artist": track_info.get("artist", {}).get("name", "Unknown"),
                "duration": track_info.get("duration"),
            }
        return None
        
    except Exception as e:
        print(f"       Search error: {str(e)[:100]}")
        return None


def download_track_by_query(query: str, download_dir: Path) -> Tuple[bool, str]:
    """
    Download a track directly using the /song/ endpoint with query.
    Decodes the manifest to get the actual FLAC URL.
    Returns (success, error_message)
    """
    try:
        # Use /song/ endpoint which searches and provides track info + manifest
        url = f"{HIFI_API_BASE}/song/"
        params = {"q": query, "quality": QUALITY}
        
        print(f"       Fetching from API...")
        
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        
        # Get JSON response - it's a list with track info and manifest
        data = response.json()
        
        if not isinstance(data, list) or len(data) < 2:
            return False, "Invalid API response format"
        
        # First element has song info
        song_info = data[0]
        track_title = song_info.get("title", query)
        artist_name = "Unknown"
        if "artist" in song_info:
            artist_name = song_info["artist"].get("name", "Unknown")
        
        # Second element has the manifest
        manifest_data = data[1]
        manifest_b64 = manifest_data.get("manifest")
        
        if not manifest_b64:
            return False, "No manifest in API response"
        
        # Decode the base64 manifest
        try:
            manifest_json = base64.b64decode(manifest_b64).decode("utf-8")
            manifest = json.loads(manifest_json)
        except Exception as e:
            return False, f"Failed to decode manifest: {str(e)[:50]}"
        
        # Extract the FLAC URL from manifest
        track_url = None
        if "urls" in manifest and isinstance(manifest["urls"], list) and len(manifest["urls"]) > 0:
            track_url = manifest["urls"][0]
        
        if not track_url:
            return False, "No URL found in manifest"
        
        # Download the actual FLAC file
        print(f"       Downloading: {track_title} by {artist_name}")
        audio_response = requests.get(track_url, timeout=TIMEOUT_PER_TRACK, stream=True)
        audio_response.raise_for_status()
        
        # Save to file
        safe_filename = f"{artist_name} - {track_title}".replace("/", "_").replace("\\", "_").replace('"', "'")
        safe_filename = safe_filename[:200]  # Limit filename length
        file_path = download_dir / f"{safe_filename}.flac"
        
        # Write file in chunks
        total_size = 0
        with file_path.open("wb") as f:
            for chunk in audio_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)
        
        # Verify file was downloaded
        if total_size > 10000:  # At least 10KB
            print(f"       ✓ Saved: {file_path.name} ({total_size / 1024 / 1024:.1f} MB)")
            return True, ""
        else:
            file_path.unlink(missing_ok=True)
            return False, f"Downloaded file too small ({total_size} bytes)"
            
    except requests.exceptions.Timeout:
        return False, f"Download timeout ({TIMEOUT_PER_TRACK}s)"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return False, "Track not available on Tidal"
        return False, f"HTTP {e.response.status_code}: {str(e)[:80]}"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {str(e)[:100]}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)[:100]}"


def process_track(track: str, download_dir: Path) -> Tuple[bool, str]:
    """
    Process a single track using direct query download.
    Returns (success, error_message)
    """
    print(f"\n[DOWNLOAD] {track}")
    
    # Use direct query download (simpler, one API call)
    success, error = download_track_by_query(track, download_dir)
    
    if success:
        print(f"[SUCCESS] ✓ Downloaded (FLAC LOSSLESS)")
        return True, ""
    else:
        return False, error


def main() -> int:
    root = Path.cwd()
    track_list_path = root / "track_list.txt"
    downloads_dir = root / "downloads"
    failures_path = root / "track_list_failed.txt"
    
    # Ensure downloads directory exists
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    # Read track list
    tracks = read_track_list(track_list_path)
    
    if not tracks:
        print("[INFO] No tracks found in track_list.txt")
        return 0
    
    print(f"{'='*70}")
    print(f"HIFI API DOWNLOADER")
    print(f"{'='*70}")
    print(f"API: {HIFI_API_BASE}")
    print(f"Format: FLAC {QUALITY}")
    print(f"Tracks to process: {len(tracks)}")
    print(f"Timeout per track: {TIMEOUT_PER_TRACK}s (2.5 minutes)")
    print(f"Downloads folder: {downloads_dir}")
    print(f"{'='*70}\n")
    
    successful_count = 0
    failed_count = 0
    
    for i, track in enumerate(tracks, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(tracks)}] Processing: {track}")
        print(f"{'='*70}")
        
        success, error_msg = process_track(track, downloads_dir)
        
        if success:
            # Immediately remove from track_list.txt
            remove_track_from_file(track_list_path, track)
            successful_count += 1
            print(f"[INFO] ✓ Removed from track_list.txt")
        else:
            # Immediately append to failed list
            append_failure(failures_path, track, error_msg)
            failed_count += 1
            print(f"[FAIL] ✗ Added to {failures_path.name}")
            print(f"       Reason: {error_msg}")
        
        # Small delay between tracks
        time.sleep(2)
    
    # Final summary
    remaining_tracks = read_track_list(track_list_path)
    
    print(f"\n{'='*70}")
    print(f"DOWNLOAD SUMMARY")
    print(f"{'='*70}")
    print(f"  Total tracks processed:      {len(tracks)}")
    print(f"  Successfully downloaded:     {successful_count}")
    print(f"  Failed:                      {failed_count}")
    print(f"  Remaining in track_list.txt: {len(remaining_tracks)}")
    print(f"  Downloads folder:            {downloads_dir}")
    print(f"  Failed tracks saved to:      {failures_path.name}")
    print(f"{'='*70}\n")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] Download interrupted by user.")
        sys.exit(130)

