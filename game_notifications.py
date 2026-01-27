"""
Game Notifications System
Handles FTL and Zomboid notifications with clickable yellow circles
"""

import pygame
import random
import time

class GameNotification:
    """A notification for FTL or Zomboid that requires clicking circles"""
    
    def __init__(self, game_type, window):
        self.game_type = game_type  # "ftl" or "zomboid"
        self.window = window  # Reference to the FTL or Zomboid window
        self.active = False
        self.circles_clicked = 0
        self.total_circles = 3
        self.circle_positions = []
        self.completion_message = ""
        self.completion_timer = 0
        self.completion_duration = 3000  # 3 seconds in milliseconds
        self.fade_alpha = 255
        
        # Generate random circle positions
        self._generate_circle_positions()
    
    def _generate_circle_positions(self):
        """Generate random positions for yellow circles within the window"""
        if not self.window:
            return
        
        content_y = self.window.position[1] + self.window.titlebar_height + 50  # Below instruction bar
        content_x = self.window.position[0] + 20
        available_width = self.window.width - 40
        available_height = self.window.height - self.window.titlebar_height - 100
        
        for _ in range(self.total_circles):
            x = content_x + random.randint(50, available_width - 50)
            y = content_y + random.randint(50, available_height - 50)
            self.circle_positions.append({
                'pos': (x, y),
                'clicked': False,
                'radius': 25
            })
    
    def activate(self):
        """Activate the notification"""
        self.active = True
        self.circles_clicked = 0
        self.completion_message = ""
        self.completion_timer = 0
        self.fade_alpha = 255
        # Reset circle states
        for circle in self.circle_positions:
            circle['clicked'] = False
        # Regenerate positions
        self._generate_circle_positions()
    
    def handle_click(self, pos):
        """Handle click on circles"""
        if not self.active or self.completion_message:
            return False
        
        for circle in self.circle_positions:
            if circle['clicked']:
                continue
            
            circle_x, circle_y = circle['pos']
            distance = ((pos[0] - circle_x) ** 2 + (pos[1] - circle_y) ** 2) ** 0.5
            
            if distance <= circle['radius']:
                circle['clicked'] = True
                self.circles_clicked += 1
                
                # Check if all circles clicked
                if self.circles_clicked >= self.total_circles:
                    if self.game_type == "ftl":
                        self.completion_message = "Great job!"
                    else:  # zomboid
                        self.completion_message = "You menu simulated!"
                    self.completion_timer = pygame.time.get_ticks()
                
                return True
        return False
    
    def update(self):
        """Update notification state"""
        if not self.active:
            return
        
        # Update fade for completion message
        if self.completion_message:
            elapsed = pygame.time.get_ticks() - self.completion_timer
            if elapsed > self.completion_duration:
                # Fade out
                fade_elapsed = elapsed - self.completion_duration
                fade_duration = 500  # 0.5 seconds fade
                if fade_elapsed < fade_duration:
                    self.fade_alpha = max(0, 255 - int((fade_elapsed / fade_duration) * 255))
                else:
                    # Deactivate after fade
                    self.active = False
                    self.completion_message = ""
                    self.fade_alpha = 255
    
    def render(self, screen):
        """Render the notification"""
        if not self.active or not self.window:
            return
        
        content_y = self.window.position[1] + self.window.titlebar_height
        
        # Draw instruction bar at top
        instruction_bar = pygame.Rect(
            self.window.position[0],
            content_y,
            self.window.width,
            40
        )
        pygame.draw.rect(screen, (240, 240, 240), instruction_bar)
        pygame.draw.line(screen, (200, 200, 200),
                        (self.window.position[0], content_y + 40),
                        (self.window.position[0] + self.window.width, content_y + 40), 2)
        
        # Draw instruction text
        font_instruction = pygame.font.Font(None, 20)
        if self.completion_message:
            instruction_text = font_instruction.render(self.completion_message, True, (0, 0, 0))
            instruction_text.set_alpha(self.fade_alpha)
        else:
            instruction_text = font_instruction.render("Click the yellow circles!", True, (0, 0, 0))
        
        text_rect = instruction_text.get_rect(center=(self.window.position[0] + self.window.width // 2, content_y + 20))
        screen.blit(instruction_text, text_rect)
        
        # Draw yellow circles (if not completed)
        if not self.completion_message:
            for circle in self.circle_positions:
                if not circle['clicked']:
                    circle_x, circle_y = circle['pos']
                    pygame.draw.circle(screen, (255, 255, 0), (circle_x, circle_y), circle['radius'])
                    pygame.draw.circle(screen, (200, 200, 0), (circle_x, circle_y), circle['radius'], 3)


class GameNotificationSystem:
    """Manages game notifications for FTL and Zomboid"""
    
    def __init__(self):
        self.active_notifications = {}  # game_type -> GameNotification
    
    def trigger_notification(self, game_type, window):
        """Trigger a notification for a game window"""
        notification = GameNotification(game_type, window)
        notification.activate()
        self.active_notifications[game_type] = notification
    
    def handle_click(self, pos):
        """Handle clicks on notifications"""
        for notification in self.active_notifications.values():
            if notification.handle_click(pos):
                return True
        return False
    
    def update(self):
        """Update all active notifications"""
        for notification in list(self.active_notifications.values()):
            notification.update()
            if not notification.active:
                # Remove completed notifications
                for game_type, notif in list(self.active_notifications.items()):
                    if notif == notification:
                        del self.active_notifications[game_type]
                        break
    
    def render(self, screen):
        """Render all active notifications"""
        for notification in self.active_notifications.values():
            notification.render(screen)
