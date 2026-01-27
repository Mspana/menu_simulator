"""
Discord Interruption System
Handles Calvelli's Discord messages that interrupt gameplay
"""

import pygame
import random
import os

class DiscordInterrupt:
    """Manages Discord interruptions from Calvelli"""
    
    def __init__(self, assets_path):
        self.assets_path = assets_path
        self.active = False
        self.current_message = ""
        self.target_menu = None
        self.popup_rect = None
        self.close_button_rect = None
        self.screen_width = 1920
        self.screen_height = 1080
        
        # Generate Discord-style popup background programmatically
        self.popup_image = self._generate_popup_background()
        self.popup_width = 500
        self.popup_height = 200
        
        # Message variations
        self.messages = [
            "Hey Matt, can you check the budget spreadsheet?",
            "Matt, did you send those emails yet?",
            "Hey, we need to update the sponsor list",
            "Matt, when are you going to finish the donation forms?",
            "Can you look at the calendar? We have a meeting soon",
            "Hey, the tasks list needs updating",
            "Matt, are you there? We need to discuss the conference",
            "Can you check the contact info? Something's wrong",
            "Hey Matt, I need your help with something",
            "Matt, we're running out of time on this"
        ]
        
        # Timing
        self.time_since_last_interrupt = 0
        self.interrupt_interval = random.randint(30000, 60000)  # 30-60 seconds in milliseconds
        self.last_interrupt_time = pygame.time.get_ticks()
    
    def _generate_popup_background(self):
        """Generate a Discord-style popup background"""
        # Create surface for smaller popup (not fullscreen)
        popup_width = 500
        popup_height = 200
        bg = pygame.Surface((popup_width, popup_height))
        
        # Discord dark theme background (#36393F or similar)
        bg.fill((54, 57, 63))
        
        # Add some subtle texture/noise
        for _ in range(1000):
            x = random.randint(0, popup_width - 1)
            y = random.randint(0, popup_height - 1)
            # Subtle noise
            noise = random.randint(-5, 5)
            current = bg.get_at((x, y))
            new_color = (
                max(0, min(255, current[0] + noise)),
                max(0, min(255, current[1] + noise)),
                max(0, min(255, current[2] + noise))
            )
            bg.set_at((x, y), new_color)
        
        return bg
    
    def update(self, menus, sounds):
        """Update interruption system"""
        current_time = pygame.time.get_ticks()
        
        if self.active:
            # Interruption is active, keep all menus blocked
            for menu in menus:
                menu.is_blocked = True
            return
        
        # Unblock menus when not active
        for menu in menus:
            menu.is_blocked = False
        
        # Check if it's time for a new interruption
        time_passed = current_time - self.last_interrupt_time
        if time_passed >= self.interrupt_interval:
            self._trigger_interruption(menus, sounds)
            self.last_interrupt_time = current_time
            self.interrupt_interval = random.randint(30000, 60000)  # Next interruption in 30-60s
    
    def _trigger_interruption(self, menus, sounds):
        """Trigger a new Discord interruption"""
        if not menus:
            return
        
        self.active = True
        self.current_message = random.choice(self.messages)
        
        # Block ALL menus when popup is active
        for menu in menus:
            menu.is_blocked = True
        
        # Smaller popup centered on screen
        popup_x = (self.screen_width - self.popup_width) // 2
        popup_y = (self.screen_height - self.popup_height) // 2
        self.popup_rect = pygame.Rect(popup_x, popup_y, self.popup_width, self.popup_height)
        
        # Close button in top right of popup
        self.close_button_rect = pygame.Rect(
            popup_x + self.popup_width - 30,
            popup_y + 10,
            20, 20
        )
        
        # Play Discord notification sound
        if sounds and 'discord' in sounds:
            sounds['discord'].play()
    
    def handle_click(self, pos, menus=None):
        """Handle click on Discord popup"""
        if not self.active:
            return False
        
        # Check if close button was clicked
        if self.close_button_rect and self.close_button_rect.collidepoint(pos):
            self._close_interruption(menus)
            return True
        
        # Any click on the popup is handled (blocks interaction with menus)
        if self.popup_rect and self.popup_rect.collidepoint(pos):
            return True
        
        return False
    
    def _close_interruption(self, menus=None):
        """Close the current interruption"""
        self.active = False
        # Unblock all menus
        if menus:
            for menu in menus:
                menu.is_blocked = False
        self.target_menu = None
        self.popup_rect = None
        self.close_button_rect = None
    
    def is_active(self):
        """Check if an interruption is currently active"""
        return self.active
    
    def render(self, screen):
        """Render the Discord popup (smaller window)"""
        if not self.active or not self.popup_rect:
            return
        
        # Draw semi-transparent overlay for the whole screen (dims background)
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw popup background
        screen.blit(self.popup_image, self.popup_rect.topleft)
        
        # Draw border around popup
        pygame.draw.rect(screen, (100, 100, 100), self.popup_rect, 2)
        
        # Draw message text (centered in popup)
        font = pygame.font.Font(None, 24)
        # Wrap text if needed
        words = self.current_message.split(' ')
        lines = []
        current_line = ""
        max_width = self.popup_width - 40  # Margins
        for word in words:
            test_line = current_line + word + " " if current_line else word + " "
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        
        # Draw lines (centered in popup)
        total_height = len(lines) * 30
        start_y = self.popup_rect.y + (self.popup_height - total_height) // 2
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.popup_rect.centerx, start_y + i * 30))
            screen.blit(text_surface, text_rect)
        
        # Draw "Calvelli" label (top left of popup)
        name_font = pygame.font.Font(None, 20)
        name_text = name_font.render("Calvelli", True, (200, 200, 200))
        screen.blit(name_text, (self.popup_rect.x + 15, self.popup_rect.y + 10))
        
        # Draw close button (top right of popup)
        ui_path = os.path.join(self.assets_path, "ui")
        close_icon = pygame.image.load(
            os.path.join(ui_path, "icon_close_x_20x20.png")
        ).convert_alpha()
        screen.blit(close_icon, self.close_button_rect.topleft)
