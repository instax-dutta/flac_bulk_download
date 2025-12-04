import csv
from pathlib import Path
import config
from utils import print_success, print_info, print_error

def find_csv_file() -> Path:
    """Find the first CSV file in the directory"""
    # 1. Check configured default
    default = config.BASE_DIR / config.DEFAULT_CSV_NAME
    if default.exists():
        return default
    
    # 2. Search for any .csv
    csvs = list(config.BASE_DIR.glob("*.csv"))
    if csvs:
        return csvs[0]
        
    return None

def extract_tracks_from_file(csv_path: Path) -> list[str]:
    """Extract tracks from a specific CSV file and return them as a list."""
    if not csv_path.exists():
        print_error(f"CSV file not found: {csv_path}")
        return []

    print_info(f"Processing: {csv_path.name}")
    tracks = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
            # Sniff format or just assume header
            reader = csv.DictReader(f)
            
            if not reader.fieldnames:
                return []

            # Normalize headers to lower case for easier matching
            header_map = {h: h.lower().strip() for h in reader.fieldnames}
            
            # Find track and artist columns
            track_col = next((h for h in reader.fieldnames if 'track' in header_map[h] and 'name' in header_map[h]), None)
            artist_col = next((h for h in reader.fieldnames if 'artist' in header_map[h] and 'name' in header_map[h]), None)
            
            if not track_col or not artist_col:
                print_error(f"Could not identify Track/Artist columns in {csv_path.name}")
                return []

            for row in reader:
                title = row.get(track_col, '').strip()
                artist_raw = row.get(artist_col, '').strip()
                
                if title and artist_raw:
                    # Take first artist (split by ; or ,)
                    artist = artist_raw.replace(';', ',').split(',')[0].strip()
                    tracks.append(f"{title} - {artist}")

        # Remove duplicates within this file
        unique_tracks = sorted(list(set(tracks)))
        return unique_tracks

    except Exception as e:
        print_error(f"Failed to parse CSV: {e}")
        return []

def extract_tracks():
    """Legacy wrapper for main.py CLI usage"""
    csv_path = find_csv_file()
    if not csv_path:
        print_error("No CSV file found!")
        return

    tracks = extract_tracks_from_file(csv_path)
    if tracks:
        # Write to file for CLI usage
        with open(config.TRACK_LIST_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(tracks))
        print_success(f"Extracted {len(tracks)} unique tracks to {config.TRACK_LIST_PATH.name}")

if __name__ == "__main__":
    extract_tracks()
