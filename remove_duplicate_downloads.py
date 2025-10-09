#!/usr/bin/env python3
"""
Remove duplicate downloaded tracks in the downloads folder by comparing file content.

Behavior:
- Scans the downloads/ directory for all files
- Computes SHA-256 hash of each file's content
- Keeps the file with the lexicographically smallest name for each unique hash
- Deletes all duplicates

Usage:
  python3 remove_duplicate_downloads.py
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Set


def compute_file_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 hex digest of the file contents."""
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def main() -> int:
    root = Path.cwd()
    downloads_dir = root / "downloads"
    
    if not downloads_dir.exists() or not downloads_dir.is_dir():
        print(f"[ERROR] Downloads directory not found: {downloads_dir}")
        return 2
    
    # Find all files in downloads
    files = [p for p in downloads_dir.iterdir() if p.is_file()]
    
    if not files:
        print("[INFO] No files found in downloads directory.")
        return 0
    
    print(f"[INFO] Found {len(files)} file(s) in downloads/")
    
    # Group files by hash
    hash_to_files: Dict[str, List[Path]] = {}
    
    for file_path in files:
        try:
            file_hash = compute_file_sha256(file_path)
            hash_to_files.setdefault(file_hash, []).append(file_path)
        except Exception as exc:
            print(f"[WARN] Failed to hash {file_path.name}: {exc}")
            continue
    
    # Identify duplicates
    total_dupes = 0
    deleted_count = 0
    
    for file_hash, file_list in hash_to_files.items():
        if len(file_list) <= 1:
            continue
        
        # Sort by name to keep deterministic choice
        sorted_files = sorted(file_list, key=lambda p: p.name)
        keep = sorted_files[0]
        dupes = sorted_files[1:]
        
        print(f"\n[KEEP] {keep.name}")
        for dupe in dupes:
            try:
                dupe.unlink()
                print(f"  [DEL] {dupe.name}")
                deleted_count += 1
                total_dupes += 1
            except Exception as exc:
                print(f"  [ERROR] Failed to delete {dupe.name}: {exc}")
    
    if total_dupes == 0:
        print("\n[INFO] No duplicate files found.")
    else:
        print(f"\n[DONE] Removed {deleted_count} duplicate file(s).")
        print(f"[INFO] Kept {len(hash_to_files)} unique file(s).")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)

