"""
Game State Management
Tracks fundraising progress and game statistics
"""

import time

class GameState:
    """Manages the game state including progress and statistics"""
    
    def __init__(self):
        self.progress = 0.0  # 0-100%
        self.items_moved = 0  # Player's "work" (actually doesn't affect progress)
        self.start_time = time.time()
        self.last_update = time.time()
        
        # Secret: Progress increases automatically (Calvelli's work)
        self.auto_progress_rate = 0.05  # Progress per second (takes ~33 minutes to complete)
        self.progress_increment = 0.0
    
    def update(self):
        """Update game state (called every frame)"""
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time
        
        # Secret mechanic: Progress increases automatically
        # This represents Calvelli doing the actual work
        if self.progress < 100.0:
            self.progress += self.auto_progress_rate * delta_time
            self.progress = min(self.progress, 100.0)
    
    def increase_progress(self, amount):
        """Increase progress by a specific amount (from Calvelli's activities)"""
        self.progress += amount
        self.progress = min(self.progress, 100.0)
    
    def on_menu_interaction(self):
        """Called when player interacts with menus"""
        # Player thinks they're making progress, but they're not
        # This is just for show - the real progress is automatic
        self.items_moved += 1
    
    def get_stats(self):
        """Get game statistics for ending screen"""
        elapsed_time = time.time() - self.start_time
        return {
            'items_moved': self.items_moved,
            'progress': self.progress,
            'time_elapsed': elapsed_time,
            'actual_work_done': 0.0,  # Player did nothing
            'calvelli_work_done': 100.0  # Calvelli did everything
        }
