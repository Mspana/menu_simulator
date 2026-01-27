"""
Milestone Notifications
Shows text notifications at progress milestones (25%, 50%, 75%, 90%)
"""

import pygame
import time

class MilestoneNotification:
    """A single milestone notification"""
    
    def __init__(self, text, screen_width):
        self.text = text
        self.screen_width = screen_width
        self.created_time = time.time()
        self.duration = 3.0  # Show for 3 seconds
        self.fade_duration = 0.5  # Fade out over 0.5 seconds
        self.start_fade_time = self.created_time + self.duration - self.fade_duration
        self.y = 20  # Top of screen
        self.width = 600  # Long (wide) notification
        self.height = 60  # Not tall
        
    def update(self, current_time):
        """Update notification state"""
        elapsed = current_time - self.created_time
        
        # Check if should start fading
        if elapsed >= self.duration - self.fade_duration:
            # Fading
            fade_elapsed = current_time - self.start_fade_time
            self.alpha = max(0, 255 - int((fade_elapsed / self.fade_duration) * 255))
        else:
            self.alpha = 255
    
    def should_remove(self, current_time):
        """Check if notification should be removed"""
        elapsed = current_time - self.created_time
        return elapsed >= self.duration
    
    def render(self, screen):
        """Render the notification"""
        if self.alpha <= 0:
            return
        
        # Calculate x position (centered horizontally)
        x = (self.screen_width - self.width) // 2
        
        # Create notification surface
        notification = pygame.Surface((self.width, self.height))
        notification.set_alpha(self.alpha)
        notification.fill((50, 100, 150))  # Blue-gray background
        
        # Draw border
        pygame.draw.rect(notification, (100, 150, 200), 
                        pygame.Rect(0, 0, self.width, self.height), 2)
        
        # Draw text
        font = pygame.font.Font(None, 32)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        notification.blit(text_surface, text_rect)
        
        # Draw to screen
        screen.blit(notification, (x, self.y))


class MilestoneNotificationSystem:
    """Manages milestone notifications"""
    
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.notifications = []
        self.milestones_shown = set()  # Track which milestones have been shown
        
        # Milestone messages
        self.milestone_messages = {
            25: "25% Complete! Great progress!",
            50: "50% Complete! Halfway there!",
            75: "75% Complete! Almost done!",
            90: "90% Complete! Final stretch!"
        }
    
    def check_milestones(self, progress):
        """Check if a milestone has been reached and show notification"""
        for milestone in [25, 50, 75, 90]:
            if milestone not in self.milestones_shown and progress >= milestone:
                self.milestones_shown.add(milestone)
                message = self.milestone_messages.get(milestone, f"{milestone}% Complete!")
                notification = MilestoneNotification(message, self.screen_width)
                self.notifications.append(notification)
    
    def update(self, current_time):
        """Update all notifications"""
        for notification in self.notifications:
            notification.update(current_time)
        
        # Remove expired notifications
        self.notifications = [n for n in self.notifications 
                             if not n.should_remove(current_time)]
    
    def render(self, screen):
        """Render all active notifications"""
        for notification in self.notifications:
            notification.render(screen)
