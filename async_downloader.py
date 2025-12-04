import sys
import asyncio
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

import aiofiles
from tqdm.asyncio import tqdm

import config
from state import state
from utils import print_error, print_info, print_success, print_warning, setup_logging

# Setup logging
setup_logging(config.LOG_FILE)

class AsyncDownloader:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_DOWNLOADS)
        self.success_count = 0
        self.fail_count = 0
        self.check_hifi_installed()

    def check_hifi_installed(self):
        """Verify spotdl tool is available"""
        # Since we installed it in venv, it should be in PATH or we can find it
        if not shutil.which(config.HIFI_PATH):
            # Try finding it in venv/bin explicitly if not in PATH
            venv_bin = Path("venv/bin/spotdl")
            if venv_bin.exists():
                config.HIFI_PATH = str(venv_bin)
            else:
                msg = f"'{config.HIFI_PATH}' tool not found. Please run setup.py again."
                print_error(msg)
                state.add_log(f"Error: {msg}")
                raise FileNotFoundError(msg)

    async def _run_hifi_command(self, args: List[str]) -> Tuple[bool, str]:
        """Run spotdl command asynchronously"""
        try:
            # spotdl writes progress to stdout/stderr. We capture it.
            process = await asyncio.create_subprocess_exec(
                config.HIFI_PATH, *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=config.TIMEOUT_PER_TRACK
            )
            
            output = stdout.decode() + stderr.decode()
            
            if process.returncode == 0:
                return True, output
            
            return False, output
            
        except asyncio.TimeoutError:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    async def _attempt_download(self, query: str, quality_name: str, quality_arg: str) -> Tuple[bool, str]:
        """Helper to attempt download with specific quality"""
        # spotdl download "query" --output-format m4a --output "downloads"
        cmd = [
            "download", 
            query, 
            "--output-format", quality_arg,
            "--output", str(config.DOWNLOADS_DIR)
        ]
        
        success, output = await self._run_hifi_command(cmd)
        
        if success:
            return True, "Success"
        else:
            # Clean up error message
            return False, output.strip()

    async def download_track(self, track: str, progress_bar: Optional[tqdm] = None) -> bool:
        """
        Download a single track using spotdl.
        """
        async with self.semaphore:
            # Update state
            state.current_track = track
            
            # Rate limiting delay
            await asyncio.sleep(config.RATE_LIMIT_DELAY)
            
            if progress_bar:
                progress_bar.set_description(f"Downloading: {track[:30]}...")
            
            # 1. Try Preferred Quality
            # For spotdl, 'm4a' is usually best native. 'flac' is converted.
            # If user wants FLAC, we use 'flac'.
            target_format = config.PREFERRED_QUALITY # e.g. 'm4a' or 'flac'
            
            success, msg = await self._attempt_download(track, "preferred", target_format)
            if success:
                self.success_count += 1
                state.success_count += 1
                state.add_log(f"Success: {track}")
                return True
            
            # 2. Fallback (if preferred failed, maybe try mp3?)
            # spotdl usually fails due to not finding song, not due to format.
            # But if we want to be safe:
            if config.ALLOW_QUALITY_FALLBACK and target_format != "mp3":
                if progress_bar:
                    progress_bar.set_description(f"Retrying (MP3): {track[:30]}...")
                state.add_log(f"Retrying (MP3): {track}")
                success, msg = await self._attempt_download(track, "fallback", "mp3")
                if success:
                    print_warning(f"Downloaded '{track}' in MP3 (Fallback)")
                    self.success_count += 1
                    state.success_count += 1
                    state.add_log(f"Success (MP3): {track}")
                    return True
            
            # Failed
            self.fail_count += 1
            state.fail_count += 1
            # Extract meaningful error from spotdl output if possible
            error_msg = msg.split('\n')[-1] if msg else "Unknown error"
            state.add_log(f"Failed: {track} - {error_msg[:100]}")
            await self._log_failure(track, msg)
            return False

    async def _log_failure(self, track: str, reason: str):
        """Log failed track to file"""
        async with aiofiles.open(config.TRACK_LIST_FAILED_PATH, mode='a', encoding='utf-8') as f:
            await f.write(f"{track} | Reason: {reason}\n")

    async def process_queue(self, use_tqdm: bool = True):
        """Main processing loop consuming from state.queue"""
        # Ensure downloads dir exists
        config.DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        
        print_info(f"Starting queue processor...")
        state.is_downloading = True
        state.add_log("Download processor started.")

        if use_tqdm:
            progress_bar = tqdm(total=state.total_tracks, unit="track", dynamic_ncols=True)
        else:
            progress_bar = None

        while True:
            # Check if we should stop? (Maybe add a stop flag in state later)
            
            # Get next track
            track = state.pop_next_track()
            
            if not track:
                # Queue empty
                # If we are in CLI mode, we might want to exit.
                # If in Web mode, we might want to wait a bit or exit thread?
                # For now, let's wait a bit and if still empty, exit.
                # Actually, user wants "keep adding more". 
                # But the thread needs to know when to stop or sleep.
                # Let's sleep briefly and check again, or exit if "done".
                # For simplicity: If queue is empty, we finish this batch.
                # The web app can restart the thread if new items are added.
                break

            # Update progress bar total if queue grew
            if progress_bar:
                if state.total_tracks > progress_bar.total:
                    progress_bar.total = state.total_tracks
                    progress_bar.refresh()

            # Download
            await self.download_track(track, progress_bar)
            
            state.completed_tracks += 1
            if progress_bar:
                progress_bar.update(1)

        if progress_bar:
            progress_bar.close()
        
        state.is_downloading = False
        state.add_log("Queue empty. Processing finished.")
        
        # Summary
        print("\n" + "="*50)
        print_success(f"Batch Finished! Success: {self.success_count}, Failed: {self.fail_count}")

        if self.fail_count > 0:
            print_warning(f"Check {config.TRACK_LIST_FAILED_PATH.name} for failures.")
        print("="*50)

        # Cleanup: Remove successful tracks from list?
        # The user might want to keep them or remove them. 
        # The original script removed them. Let's keep that behavior but maybe safer.
        # For now, I won't auto-delete to be safe, or I'll ask the user in main.py.

if __name__ == "__main__":
    import sys
    downloader = AsyncDownloader()
    try:
        asyncio.run(downloader.process_track_list())
    except KeyboardInterrupt:
        print_warning("\nStopped by user.")
        sys.exit(0)
