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
        self.blink_timer = 0  # For blinking orange outline
        self.blink_speed = 500  # Milliseconds per blink cycle
        
        # Generate random circle positions
        self._generate_circle_positions()
    
    def _generate_circle_positions(self):
        """Generate random positions for yellow circles within the window (relative to window)"""
        if not self.window:
            return
        
        # Store positions relative to window, not absolute screen positions
        instruction_box_height = 50  # Updated to match render height
        padding = 20
        content_y_offset = self.window.titlebar_height + padding + instruction_box_height + padding
        content_x_offset = padding
        available_width = self.window.width - (padding * 2)
        available_height = self.window.height - self.window.titlebar_height - content_y_offset - padding
        
        for _ in range(self.total_circles):
            rel_x = content_x_offset + random.randint(50, max(50, available_width - 50))
            rel_y = content_y_offset + random.randint(50, max(50, available_height - 50))
            self.circle_positions.append({
                'rel_pos': (rel_x, rel_y),  # Relative to window position
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
        if not self.active or self.completion_message or not self.window:
            return False
        
        for circle in self.circle_positions:
            if circle['clicked']:
                continue
            
            # Calculate absolute position from relative position
            rel_x, rel_y = circle['rel_pos']
            circle_x = self.window.position[0] + rel_x
            circle_y = self.window.position[1] + rel_y
            
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
        
        # Update blink timer for orange outline
        if not self.completion_message:
            self.blink_timer = pygame.time.get_ticks()
        
        # Update fade for completion message
        if self.completion_message:
            elapsed = pygame.time.get_ticks() - self.completion_timer
            if elapsed >= self.completion_duration:
                # Fade out after 3 seconds
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
        
        # Draw blinking orange outline around window (only if not completed)
        if not self.completion_message:
            blink_phase = (pygame.time.get_ticks() // self.blink_speed) % 2
            if blink_phase == 0:  # Visible phase
                # Draw orange outline around entire window
                outline_rect = pygame.Rect(
                    self.window.position[0] - 3,
                    self.window.position[1] - 3,
                    self.window.width + 6,
                    self.window.height + 6
                )
                pygame.draw.rect(screen, (255, 165, 0), outline_rect, 4)  # Orange outline
        
        content_y = self.window.position[1] + self.window.titlebar_height
        
        # Draw instruction box (smaller, not touching top/sides, orange)
        padding = 20  # Padding from sides and top
        instruction_box_width = self.window.width - (padding * 2)
        instruction_box_height = 50  # Increased to fit two lines of text
        instruction_box_x = self.window.position[0] + padding
        instruction_box_y = content_y + padding
        
        instruction_box = pygame.Rect(
            instruction_box_x,
            instruction_box_y,
            instruction_box_width,
            instruction_box_height
        )
        pygame.draw.rect(screen, (255, 165, 0), instruction_box)  # Orange background
        pygame.draw.rect(screen, (200, 120, 0), instruction_box, 2)  # Darker orange border
        
        # Draw instruction text
        font_instruction = pygame.font.Font(None, 20)
        font_play = pygame.font.Font(None, 26)  # Larger font for "Play [Game]"
        if self.completion_message:
            instruction_text = font_instruction.render(self.completion_message, True, (0, 0, 0))
            instruction_text.set_alpha(self.fade_alpha)
            text_rect = instruction_text.get_rect(center=instruction_box.center)
            screen.blit(instruction_text, text_rect)
        else:
            # Draw "Play [Game]" on first line (larger font)
            game_name = "FTL" if self.game_type == "ftl" else "Zomboid"
            play_text = font_play.render(f"Play {game_name}", True, (0, 0, 0))
            play_rect = play_text.get_rect(center=(instruction_box.centerx, instruction_box.y + 15))
            screen.blit(play_text, play_rect)
            
            # Draw "Click the yellow circles!" on second line
            circles_text = font_instruction.render("Click the yellow circles!", True, (0, 0, 0))
            circles_rect = circles_text.get_rect(center=(instruction_box.centerx, instruction_box.y + 32))
            screen.blit(circles_text, circles_rect)
        
        # Draw yellow circles (if not completed)
        if not self.completion_message:
            for circle in self.circle_positions:
                if not circle['clicked']:
                    # Calculate absolute position from relative position
                    rel_x, rel_y = circle['rel_pos']
                    circle_x = self.window.position[0] + rel_x
                    circle_y = self.window.position[1] + rel_y
                    pygame.draw.circle(screen, (255, 255, 0), (circle_x, circle_y), circle['radius'])
                    pygame.draw.circle(screen, (200, 200, 0), (circle_x, circle_y), circle['radius'], 3)


class GameNotificationSystem:
    """Manages game notifications for FTL and Zomboid"""
    
    def __init__(self):
        self.active_notifications = {}  # game_type -> GameNotification
    
    def trigger_notification(self, game_type, window, menus_list=None):
        """Trigger a notification for a game window"""
        notification = GameNotification(game_type, window)
        notification.activate()
        self.active_notifications[game_type] = notification
        
        # Bring window to front
        if menus_list:
            max_z = max([m.z_index for m in menus_list], default=0)
            window.z_index = max_z + 1
    
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
