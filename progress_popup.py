"""
Progress Popup Animation
Shows +number popup animation over progress bar when progress increases
"""

import pygame
import time

class ProgressPopup:
    """A single progress popup animation"""
    
    def __init__(self, amount, position):
        self.amount = amount
        self.position = position  # (x, y) position on progress bar
        self.created_time = time.time()
        self.duration = 1.5  # Total animation duration
        self.start_scale = 0.5
        self.end_scale = 1.5
        self.start_alpha = 255
        self.end_alpha = 0
        
    def update(self, current_time):
        """Update animation state"""
        elapsed = current_time - self.created_time
        self.progress = min(elapsed / self.duration, 1.0)
    
    def should_remove(self, current_time):
        """Check if popup should be removed"""
        elapsed = current_time - self.created_time
        return elapsed >= self.duration
    
    def render(self, screen):
        """Render the popup"""
        if self.progress >= 1.0:
            return
        
        # Calculate scale (fade in and grow)
        if self.progress < 0.3:
            # Fade in and grow
            phase = self.progress / 0.3
            scale = self.start_scale + (1.0 - self.start_scale) * phase
            alpha = int(self.start_alpha * phase)
        else:
            # Fade out and continue growing
            phase = (self.progress - 0.3) / 0.7
            scale = 1.0 + (self.end_scale - 1.0) * phase
            alpha = int(self.start_alpha * (1.0 - phase))
        
        # Create text
        font = pygame.font.Font(None, int(32 * scale))
        text = font.render(f"+{self.amount:.1f}%", True, (50, 200, 50))  # Green
        
        # Create surface with alpha
        text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        text_surface.set_alpha(alpha)
        text_surface.blit(text, (0, 0))
        
        # Calculate position (centered above progress bar)
        text_rect = text_surface.get_rect(center=(self.position[0], self.position[1] - 20))
        screen.blit(text_surface, text_rect)


class ProgressPopupSystem:
    """Manages progress popup animations"""
    
    def __init__(self):
        self.popups = []
        self.last_progress = 0.0
    
    def check_progress_increase(self, current_progress, progress_bar_center):
        """Check if progress increased and create popup"""
        increase = current_progress - self.last_progress
        if increase > 0.01:  # Only show popup for meaningful increases
            popup = ProgressPopup(increase, progress_bar_center)
            self.popups.append(popup)
            self.last_progress = current_progress
    
    def update(self, current_time):
        """Update all popups"""
        for popup in self.popups:
            popup.update(current_time)
        
        # Remove expired popups
        self.popups = [p for p in self.popups if not p.should_remove(current_time)]
    
    def render(self, screen):
        """Render all active popups"""
        for popup in self.popups:
            popup.render(screen)
