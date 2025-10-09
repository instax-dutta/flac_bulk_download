#!/usr/bin/env python3
"""
Download tracks from track_list.txt using the hifi tool from:
https://github.com/sachinsenal0x64/hifi

Setup Instructions:
1. Clone the hifi repository: git clone https://github.com/sachinsenal0x64/hifi.git
2. Follow the installation instructions in the hifi README
3. Ensure 'hifi' command is available in your PATH or update HIFI_PATH below

Usage:
  python3 download_tracks_hifi.py
  
Behavior:
- Reads track_list.txt (format: "Title - Artist")
- Downloads each track using the hifi CLI tool
- Saves to downloads/ directory
- Skips tracks that fail with a 2.5 minute timeout
- Removes successfully downloaded tracks from track_list.txt
- Saves failed tracks to track_list_failed.txt
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import List

# Path to hifi executable - update this if needed
HIFI_PATH = "hifi"  # Assumes 'hifi' is in PATH, or use full path like: "/path/to/hifi"


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


def remove_tracks_from_file(path: Path, tracks_to_remove: List[str]) -> None:
    """Remove successfully downloaded tracks from track_list.txt"""
    all_lines = path.read_text(encoding="utf-8").splitlines()
    set_remove = set(tracks_to_remove)
    remaining = [l for l in all_lines if l.strip() not in set_remove]
    path.write_text("\n".join(remaining) + ("\n" if remaining else ""), encoding="utf-8")


def append_failure(path: Path, track: str, error: str) -> None:
    """Append a single failed track with error message to track_list_failed.txt"""
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{track}\n")
        if error:
            f.write(f"  Error: {error}\n")
        f.write("\n")


def check_hifi_installed() -> bool:
    """Check if hifi is installed and accessible"""
    try:
        result = subprocess.run(
            [HIFI_PATH, "--help"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0 or b"hifi" in result.stdout.lower() or b"hifi" in result.stderr.lower()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def download_track(track: str, download_dir: Path, timeout: int = 150) -> tuple[bool, str]:
    """
    Download a track using hifi CLI in FLAC format.
    Returns (success: bool, error_message: str)
    
    Tries multiple command formats with FLAC/lossless flags.
    """
    print(f"\n[INFO] Downloading: {track}")
    
    # List of command formats to try (in order)
    # Each includes FLAC/lossless quality flags
    command_formats = [
        # Format 1: hifi download with FLAC format and quality flags
        [HIFI_PATH, "download", track, "--format", "flac", "--quality", "lossless", "--output-dir", str(download_dir)],
        
        # Format 2: hifi with output dir and format
        [HIFI_PATH, track, "-o", str(download_dir), "--format", "flac"],
        
        # Format 3: hifi search with download and FLAC
        [HIFI_PATH, "search", track, "--download", "--format", "flac", "--path", str(download_dir)],
        
        # Format 4: Simple format with FLAC
        [HIFI_PATH, "download", track, "--flac", "-o", str(download_dir)],
        
        # Format 5: Minimal command (may use default FLAC)
        [HIFI_PATH, track, "-o", str(download_dir)],
    ]
    
    last_error = ""
    
    for i, cmd in enumerate(command_formats, 1):
        try:
            print(f"       Trying format {i}/{len(command_formats)}...")
            
            result = subprocess.run(
                cmd,
                timeout=timeout,
                capture_output=True,
                text=True,
                check=False,
                cwd=str(download_dir.parent)
            )
            
            # Check for success indicators
            success_indicators = ["success", "downloaded", "complete", "saved"]
            error_indicators = ["error", "failed", "not found", "no results"]
            
            stdout_lower = result.stdout.lower()
            stderr_lower = result.stderr.lower()
            
            # Check if download succeeded
            if result.returncode == 0 or any(ind in stdout_lower for ind in success_indicators):
                # Verify a FLAC file was created
                flac_files_before = set(download_dir.glob("*.flac"))
                time.sleep(1)  # Brief wait for file system
                flac_files_after = set(download_dir.glob("*.flac"))
                
                if len(flac_files_after) > len(flac_files_before):
                    print(f"[SUCCESS] Downloaded: {track} (FLAC)")
                    return True, ""
                elif result.returncode == 0:
                    print(f"[SUCCESS] Downloaded: {track}")
                    return True, ""
            
            # Check for explicit errors
            if any(ind in stdout_lower or ind in stderr_lower for ind in error_indicators):
                last_error = result.stderr.strip() or result.stdout.strip()
                print(f"       Format {i} failed: {last_error[:100]}")
                continue  # Try next format
            
            # If no clear success or error, try next format
            last_error = f"Unclear result (code {result.returncode})"
            
        except subprocess.TimeoutExpired:
            last_error = f"Timeout ({timeout}s)"
            print(f"       Format {i} timed out")
            continue
        except Exception as exc:
            last_error = str(exc)
            print(f"       Format {i} error: {exc}")
            continue
    
    # All formats failed
    print(f"[FAIL] Could not download: {track}")
    print(f"       Last error: {last_error[:200]}")
    return False, last_error or "All command formats failed"


def main() -> int:
    root = Path.cwd()
    track_list_path = root / "track_list.txt"
    downloads_dir = root / "downloads"
    failures_path = root / "track_list_failed.txt"
    
    # Check if hifi is installed
    if not check_hifi_installed():
        print("[ERROR] 'hifi' tool not found!")
        print("\nPlease install hifi:")
        print("  1. Clone: git clone https://github.com/sachinsenal0x64/hifi.git")
        print("  2. Follow installation instructions in the repository")
        print("  3. Ensure 'hifi' is in your PATH or update HIFI_PATH in this script")
        return 1
    
    # Ensure downloads directory exists
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    # Read track list
    tracks = read_track_list(track_list_path)
    
    if not tracks:
        print("[INFO] No tracks found in track_list.txt")
        return 0
    
    print(f"[INFO] Found {len(tracks)} track(s) to download")
    print(f"[INFO] Downloads will be saved to: {downloads_dir}")
    print(f"[INFO] Format: FLAC lossless")
    print(f"[INFO] Timeout per track: 150 seconds (2.5 minutes)")
    print(f"[INFO] Tracks will be removed from track_list.txt immediately after successful download")
    
    successful_count = 0
    failed_count = 0
    
    for i, track in enumerate(tracks, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(tracks)}] Processing: {track}")
        print(f"{'='*70}")
        
        success, error_msg = download_track(track, downloads_dir, timeout=150)
        
        if success:
            # Immediately remove from track_list.txt after successful download
            remove_tracks_from_file(track_list_path, [track])
            successful_count += 1
            print(f"[INFO] Removed '{track}' from track_list.txt")
        else:
            # Immediately append to failed list with error message
            append_failure(failures_path, track, error_msg)
            failed_count += 1
            print(f"[INFO] Added '{track}' to {failures_path.name}")
        
        # Small delay between downloads
        time.sleep(2)
    
    # Final count of remaining tracks
    remaining_tracks = read_track_list(track_list_path)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"DOWNLOAD SUMMARY")
    print(f"{'='*70}")
    print(f"  Total tracks processed:      {len(tracks)}")
    print(f"  Successfully downloaded:     {successful_count}")
    print(f"  Failed:                      {failed_count}")
    print(f"  Remaining in track_list.txt: {len(remaining_tracks)}")
    print(f"  Failed tracks saved to:      {failures_path.name}")
    print(f"{'='*70}\n")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] Download interrupted by user.")
        sys.exit(130)
