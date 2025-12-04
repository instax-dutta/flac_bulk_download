import threading
import time
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AppState:
    is_downloading: bool = False
    total_tracks: int = 0
    completed_tracks: int = 0
    success_count: int = 0
    fail_count: int = 0
    current_track: str = ""
    recent_logs: List[str] = field(default_factory=list)
    queue: List[str] = field(default_factory=list)
    
    def reset(self):
        # Don't clear the queue on reset, just the stats
        self.is_downloading = False
        self.completed_tracks = 0
        self.success_count = 0
        self.fail_count = 0
        self.current_track = ""
        # self.recent_logs = [] # Keep logs too? Maybe clear logs on new start if idle.

    def add_tracks_to_queue(self, new_tracks: List[str]):
        # Add only unique tracks that are not already in queue
        current_set = set(self.queue)
        added_count = 0
        for t in new_tracks:
            if t not in current_set:
                self.queue.append(t)
                current_set.add(t)
                added_count += 1
        
        self.total_tracks = len(self.queue)
        if added_count > 0:
            self.add_log(f"Added {added_count} tracks to queue.")

    def pop_next_track(self) -> Optional[str]:
        if self.queue:
            return self.queue.pop(0)
        return None

    def add_log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        self.recent_logs.insert(0, f"[{timestamp}] {message}")
        if len(self.recent_logs) > 50:
            self.recent_logs.pop()

# Global state instance
state = AppState()
