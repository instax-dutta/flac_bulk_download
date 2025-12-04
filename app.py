import os
import sys
import subprocess
import threading
import asyncio
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

import config
from state import state
from async_downloader import AsyncDownloader
from extract_tracks import extract_tracks

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.BASE_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure directories exist
config.DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

def run_async_process():
    """Wrapper to run the async downloader in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        downloader = AsyncDownloader()
        # We pass use_tqdm=False to avoid console bar interference
        loop.run_until_complete(downloader.process_queue(use_tqdm=False))
    except Exception as e:
        print(f"Async process error: {e}")
        state.add_log(f"Critical Error: {e}")
        state.is_downloading = False
    finally:
        loop.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.csv'):
        # Save with original filename to avoid overwriting
        filename = secure_filename(file.filename)
        save_path = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(save_path)
        
        # Extract tracks
        try:
            from extract_tracks import extract_tracks_from_file
            new_tracks = extract_tracks_from_file(save_path)
            
            if new_tracks:
                state.add_tracks_to_queue(new_tracks)
                
                # Persist to track_list.txt (append)
                with open(config.TRACK_LIST_PATH, 'a', encoding='utf-8') as f:
                    f.write('\n' + '\n'.join(new_tracks))
                
                state.add_log(f"Queued {len(new_tracks)} tracks from {filename}")
            else:
                state.add_log(f"No valid tracks found in {filename}")
                
            # Cleanup uploaded CSV
            save_path.unlink()
            
        except Exception as e:
            state.add_log(f"Error processing {filename}: {e}")
            
    return redirect(url_for('index'))

@app.route('/start-download', methods=['POST'])
def start_download():
    if state.is_downloading:
        return jsonify({'status': 'already_running', 'message': 'Download already in progress'})
    
    if not state.queue:
        return jsonify({'status': 'empty_queue', 'message': 'Queue is empty. Upload a playlist first.'})
    
    # Start background thread
    thread = threading.Thread(target=run_async_process)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/cleanup', methods=['POST'])
def cleanup_duplicates():
    try:
        # Run the cleanup script
        result = subprocess.run(
            [sys.executable, "remove_duplicate_downloads.py"], 
            capture_output=True, 
            text=True
        )
        output = result.stdout
        # Parse output for simple stats
        if "Removed" in output:
            msg = "Cleanup complete. Duplicates removed."
        elif "No duplicate" in output:
            msg = "No duplicates found."
        else:
            msg = "Cleanup finished."
            
        state.add_log(msg)
        return jsonify({'status': 'success', 'message': msg})
    except Exception as e:
        state.add_log(f"Cleanup failed: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/status')
def get_status():
    return jsonify({
        'is_downloading': state.is_downloading,
        'total': state.total_tracks,
        'completed': state.completed_tracks,
        'success': state.success_count,
        'failed': state.fail_count,
        'current_track': state.current_track,
        'logs': state.recent_logs
    })

@app.route('/files')
def list_files():
    files = []
    if config.DOWNLOADS_DIR.exists():
        files = [f.name for f in config.DOWNLOADS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]
        files.sort()
    return jsonify(files)

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(config.DOWNLOADS_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    print("Starting Web Interface on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
