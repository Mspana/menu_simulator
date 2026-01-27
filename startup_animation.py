"""
Startup Animation
Handles the screen turning on, login animation, and fade in
"""

import pygame
import time
import math
import random

class StartupAnimation:
    """Manages the startup animation sequence"""
    
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.start_time = time.time()
        self.current_phase = "screen_on"  # "screen_on", "logging_in", "fade_in"
        self.phase_start_time = time.time()
        
        # Screen on animation
        self.screen_on_duration = 0.5  # 0.5 seconds
        self.screen_brightness = 0.0
        
        # Logging in animation
        self.logging_in_duration = 2.0  # 2 seconds
        self.spinner_angle = 0.0
        self.spinner_radius = 30
        self.spinner_center = (self.width // 2, self.height // 2)
        
        # Random login message
        login_messages = [
            "taking a cup hit",
            "menu simulating",
            "going inflight",
            "taking a call from mama velli",
            "responding quarterly",
            "malding"
        ]
        self.login_message = random.choice(login_messages)
        
        # Fade in animation
        self.fade_in_duration = 1.0  # 1 second
        self.fade_alpha = 255  # Start fully opaque (overlay)
        
        # Create overlay for fade
        self.overlay = pygame.Surface((self.width, self.height))
        self.overlay.fill((0, 0, 0))
        
    def update(self, dt):
        """Update animation state
        dt: time since last update in seconds
        """
        current_time = time.time()
        elapsed = current_time - self.phase_start_time
        
        if self.current_phase == "screen_on":
            # Brighten screen from black
            progress = min(elapsed / self.screen_on_duration, 1.0)
            self.screen_brightness = progress
            
            if progress >= 1.0:
                self.current_phase = "logging_in"
                self.phase_start_time = current_time
        
        elif self.current_phase == "logging_in":
            # Rotate spinner
            self.spinner_angle += 3.0  # Rotate 3 degrees per frame
            
            if elapsed >= self.logging_in_duration:
                self.current_phase = "fade_in"
                self.phase_start_time = current_time
        
        elif self.current_phase == "fade_in":
            # Fade out overlay
            progress = min(elapsed / self.fade_in_duration, 1.0)
            self.fade_alpha = int(255 * (1.0 - progress))
            
            if progress >= 1.0:
                return True  # Animation complete
        
        return False
    
    def is_complete(self):
        """Check if animation is complete"""
        return self.current_phase == "fade_in" and self.fade_alpha <= 0
    
    def render(self, game_background):
        """Render the animation"""
        if self.current_phase == "screen_on":
            # Draw black screen that brightens
            brightness = int(255 * self.screen_brightness)
            self.screen.fill((brightness, brightness, brightness))
        
        elif self.current_phase == "logging_in":
            # Draw white screen with spinner
            self.screen.fill((255, 255, 255))
            
            # Draw login message text
            font = pygame.font.Font(None, 36)
            text = font.render(self.login_message + "...", True, (100, 100, 100))
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 50))
            self.screen.blit(text, text_rect)
            
            # Draw spinner (circle with rotating dots)
            center_x, center_y = self.spinner_center
            num_dots = 8
            for i in range(num_dots):
                angle = math.radians(self.spinner_angle + (i * 360 / num_dots))
                dot_x = center_x + self.spinner_radius * math.cos(angle)
                dot_y = center_y + self.spinner_radius * math.sin(angle)
                
                # Fade dots based on position
                dot_alpha = int(255 * (0.3 + 0.7 * (i / num_dots)))
                dot_color = (100, 100, 100)
                pygame.draw.circle(self.screen, dot_color, (int(dot_x), int(dot_y)), 5)
        
        elif self.current_phase == "fade_in":
            # Draw game background
            self.screen.blit(game_background, (0, 0))
            
            # Draw fading overlay
            if self.fade_alpha > 0:
                self.overlay.set_alpha(self.fade_alpha)
                self.screen.blit(self.overlay, (0, 0))
