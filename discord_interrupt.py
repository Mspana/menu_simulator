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
        # Create surface for fullscreen popup
        bg = pygame.Surface((self.screen_width, self.screen_height))
        
        # Discord dark theme background (#36393F or similar)
        bg.fill((54, 57, 63))
        
        # Add some subtle texture/noise
        for _ in range(5000):
            x = random.randint(0, self.screen_width - 1)
            y = random.randint(0, self.screen_height - 1)
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
        
        # Fullscreen popup
        self.popup_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        
        # Close button in top right of screen
        self.close_button_rect = pygame.Rect(
            self.screen_width - 40,
            20,
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
        """Render the Discord popup (fullscreen)"""
        if not self.active or not self.popup_rect:
            return
        
        # Draw fullscreen popup background
        screen.blit(self.popup_image, (0, 0))
        
        # Draw semi-transparent overlay for better text visibility
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(100)  # Less opaque since background is already dark
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw message text (centered, larger for fullscreen)
        font = pygame.font.Font(None, 48)
        # Wrap text if needed
        words = self.current_message.split(' ')
        lines = []
        current_line = ""
        max_width = self.screen_width - 200  # Margins
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
        
        # Draw lines (centered vertically)
        total_height = len(lines) * 60
        start_y = (self.screen_height - total_height) // 2
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, start_y + i * 60))
            screen.blit(text_surface, text_rect)
        
        # Draw "Calvelli" label (top left, larger)
        name_font = pygame.font.Font(None, 36)
        name_text = name_font.render("Calvelli", True, (200, 200, 200))
        screen.blit(name_text, (50, 50))
        
        # Draw close button (top right, larger)
        ui_path = os.path.join(self.assets_path, "ui")
        close_icon = pygame.image.load(
            os.path.join(ui_path, "icon_close_x_20x20.png")
        ).convert_alpha()
        # Scale close button for better visibility
        close_icon = pygame.transform.scale(close_icon, (40, 40))
        self.close_button_rect = pygame.Rect(
            self.screen_width - 60,
            20,
            40, 40
        )
        screen.blit(close_icon, self.close_button_rect.topleft)
        
        # Draw instruction text
        instruction_font = pygame.font.Font(None, 32)
        instruction_text = instruction_font.render("Click the X to close", True, (150, 150, 150))
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        screen.blit(instruction_text, instruction_rect)
