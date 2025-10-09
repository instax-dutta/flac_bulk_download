#!/usr/bin/env python3
"""
Extract track titles and artists from Liked_Songs.csv
and create a track_list.txt for downloading
"""

import csv
import re
from pathlib import Path

def clean_artist_name(artist_string):
    """Extract first artist from semicolon-separated list"""
    if not artist_string:
        return "Unknown"
    
    # Split by semicolon and take first artist
    first_artist = artist_string.split(';')[0].strip()
    
    # Clean up any extra whitespace or special characters
    first_artist = re.sub(r'\s+', ' ', first_artist)
    
    return first_artist

def extract_tracks_from_csv(csv_file, output_file):
    """Extract tracks from Liked_Songs.csv and create track_list.txt"""
    
    tracks = []
    duplicates = set()
    
    print(f"Reading {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            track_name = row.get('Track Name', '').strip()
            artist_names = row.get('Artist Name(s)', '').strip()
            
            if not track_name or not artist_names:
                continue
            
            # Get first artist only
            first_artist = clean_artist_name(artist_names)
            
            # Create track entry in format "Title - Artist"
            track_entry = f"{track_name} - {first_artist}"
            
            # Skip duplicates
            if track_entry.lower() in duplicates:
                continue
            
            duplicates.add(track_entry.lower())
            tracks.append(track_entry)
    
    print(f"Extracted {len(tracks)} unique tracks")
    
    # Write to track_list.txt
    with open(output_file, 'w', encoding='utf-8') as f:
        for track in tracks:
            f.write(track + '\n')
    
    print(f"Saved track list to {output_file}")
    return len(tracks)

if __name__ == "__main__":
    csv_file = Path("Daylist_Dumps_.csv")
    output_file = Path("track_list.txt")
    
    if not csv_file.exists():
        print(f"Error: {csv_file} not found!")
        exit(1)
    
    track_count = extract_tracks_from_csv(csv_file, output_file)
    print(f"\n✅ Successfully extracted {track_count} unique tracks")
    print(f"📁 Track list saved to: {output_file}")
