"""
Calvelli Activity Log
Shows random things Calvelli has done, which increase progress
"""

import pygame
import random
from messages_content import CALVELLI_ACTIVITIES

class CalvelliLog:
    """Manages the activity log showing what Calvelli has done"""
    
    def __init__(self):
        self.activities = CALVELLI_ACTIVITIES
        
        self.current_log = None
        self.log_start_time = 0
        self.log_duration = 3000  # Show log for 3 seconds
        self.last_log_time = 0  # Will be set on first update
        self.log_interval = random.randint(5000, 15000)  # 5-15 seconds
        self.progress_increase = 0  # Amount to increase progress
        self.progress_applied = False  # Track if progress has been applied
        self.initialized = False
        self.should_send_email = False
        self.email_delay = 0
        self.email_delay_start = 0
    
    def update(self, current_time_ms):
        """Update the log system"""
        # Initialize on first update
        if not self.initialized:
            self.last_log_time = current_time_ms
            self.initialized = True
            return
        
        # Check if it's time for a new log
        time_since_last = current_time_ms - self.last_log_time
        
        if self.current_log is None:
            # No log currently showing, check if it's time for a new one
            if time_since_last >= self.log_interval:
                self._show_new_log(current_time_ms)
                self.last_log_time = current_time_ms
                self.log_interval = random.randint(5000, 15000)  # Next log in 5-15s
        else:
            # Log is showing, check if it should disappear
            if current_time_ms - self.log_start_time >= self.log_duration:
                self.current_log = None
                self.progress_increase = 0
                self.progress_applied = False
    
    def should_trigger_email(self, current_time_ms):
        """Check if it's time to trigger a congratulatory email notification"""
        if not self.should_send_email:
            return False
        
        current_time_s = current_time_ms / 1000.0
        elapsed = current_time_s - self.email_delay_start
        
        if elapsed >= self.email_delay:
            self.should_send_email = False
            return True
        return False
    
    def _show_new_log(self, current_time_ms):
        """Show a new random activity log"""
        self.current_log = random.choice(self.activities)
        self.log_start_time = current_time_ms
        # Random progress increase between 5-12.5%
        self.progress_increase = random.uniform(5.0, 12.5)
        self.progress_applied = False  # Track if we've applied the progress
        # Signal that a congratulatory email should be sent
        self.should_send_email = True
        self.email_delay = random.uniform(1.0, 3.0)  # 1-3 seconds delay
        self.email_delay_start = current_time_ms / 1000.0  # Convert to seconds
    
    def get_progress_increase(self):
        """Get the progress increase (only once per log)"""
        if not self.progress_applied and self.progress_increase > 0:
            self.progress_applied = True
            return self.progress_increase
        return 0
    
    def render(self, screen):
        """Render the log in the top left (below progress bar)"""
        if self.current_log is None:
            return
        
        # Position below progress bar (progress bar is at y=20, height ~30, so start at y=70)
        log_x = 20
        log_y = 70
        
        # Create background panel
        font = pygame.font.Font(None, 28)
        text_surface = font.render(self.current_log, True, (255, 255, 255))
        
        # Panel dimensions
        padding = 15
        panel_width = text_surface.get_width() + padding * 2
        panel_height = text_surface.get_height() + padding * 2
        
        # Draw semi-transparent background
        panel = pygame.Surface((panel_width, panel_height))
        panel.set_alpha(240)
        panel.fill((40, 40, 40))
        screen.blit(panel, (log_x, log_y))
        
        # Draw border
        pygame.draw.rect(screen, (100, 100, 100), 
                        pygame.Rect(log_x, log_y, panel_width, panel_height), 2)
        
        # Draw text
        screen.blit(text_surface, (log_x + padding, log_y + padding))
