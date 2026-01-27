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
    
    def __init__(self, screen, windows=None):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.start_time = time.time()
        self.current_phase = "screen_on"  # "screen_on", "logging_in", "fade_in", "windows_opening"
        self.phase_start_time = time.time()
        self.windows = windows or []
        
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
        
        # Window opening animation
        self.window_open_duration = 0.5  # 0.5 seconds
        self.window_animations = {}  # Track each window's animation state

        # Post-window white fade animation (white -> normal content)
        self.post_fade_duration = 0.25  # 0.25 seconds
        self.post_fade_alpha = 255
        
        # Initialize window animations
        if self.windows:
            # Taskbar icon position (bottom center, where windows would appear from)
            self.taskbar_icon_y = self.height - 50
            self.taskbar_icon_x = self.width // 2
            
            for i, window in enumerate(self.windows):
                # Store original position
                original_pos = window.position[:]
                original_alpha = getattr(window, 'opening_alpha', 255)
                
                # Start windows at taskbar icon position (small)
                window.opening_start_pos = (self.taskbar_icon_x, self.taskbar_icon_y)
                window.opening_target_pos = original_pos
                window.opening_start_size = (50, 50)  # Small icon size
                window.opening_target_size = (window.width, window.height)
                window.opening_alpha = 0  # Start invisible
                window.opening_progress = 0.0
                
                self.window_animations[id(window)] = {
                    'start_time': None,  # Will be set when animation starts
                    'original_pos': original_pos,
                    'original_alpha': original_alpha
                }
        
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
                # Start window opening animations
                self.current_phase = "windows_opening"
                self.phase_start_time = current_time
                # Initialize window animation start times (staggered slightly)
                for i, window in enumerate(self.windows):
                    window_id = id(window)
                    if window_id in self.window_animations:
                        self.window_animations[window_id]['start_time'] = current_time + (i * 0.05)  # 50ms stagger
        
        elif self.current_phase == "windows_opening":
            # Animate windows opening from taskbar icon
            current_time = time.time()
            all_complete = True
            
            for window in self.windows:
                window_id = id(window)
                if window_id not in self.window_animations:
                    continue
                
                anim_data = self.window_animations[window_id]
                if anim_data['start_time'] is None:
                    continue
                
                window_elapsed = current_time - anim_data['start_time']
                if window_elapsed < 0:
                    all_complete = False
                    continue
                
                progress = min(window_elapsed / self.window_open_duration, 1.0)
                window.opening_progress = progress
                
                # Ease out cubic for smooth animation
                eased_progress = 1.0 - pow(1.0 - progress, 3)
                
                # Interpolate position
                start_x, start_y = window.opening_start_pos
                target_x, target_y = window.opening_target_pos
                window.position[0] = int(start_x + (target_x - start_x) * eased_progress)
                window.position[1] = int(start_y + (target_y - start_y) * eased_progress)
                
                # Interpolate size
                start_w, start_h = window.opening_start_size
                target_w, target_h = window.opening_target_size
                window.width = int(start_w + (target_w - start_w) * eased_progress)
                window.height = int(start_h + (target_h - start_h) * eased_progress)
                
                # Interpolate alpha (fade in)
                window.opening_alpha = int(255 * eased_progress)
                
                if progress < 1.0:
                    all_complete = False
                else:
                    # Animation complete, restore original values
                    window.position = anim_data['original_pos'][:]
                    window.width = window.opening_target_size[0]
                    window.height = window.opening_target_size[1]
                    window.opening_alpha = 255
                    window.opening_progress = 1.0
            
            if all_complete:
                # All windows finished opening; start white fade-out to reveal full content
                self.current_phase = "white_fade"
                self.phase_start_time = current_time
                self.post_fade_alpha = 255
        
        elif self.current_phase == "white_fade":
            # Simple timer; rendering handles the actual fade
            progress = min(elapsed / self.post_fade_duration, 1.0)
            self.post_fade_alpha = int(255 * (1.0 - progress))
            if progress >= 1.0:
                return True  # Entire startup sequence complete
        
        return False
    
    def is_complete(self):
        """Check if animation is complete"""
        if self.current_phase == "white_fade":
            return self.post_fade_alpha <= 0
        if self.current_phase == "windows_opening":
            return all(hasattr(w, 'opening_progress') and w.opening_progress >= 1.0 for w in self.windows)
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
            # Draw game background with fade
            bg_alpha = 255 - self.fade_alpha
            if bg_alpha > 0:
                temp_bg = game_background.copy()
                temp_bg.set_alpha(bg_alpha)
                self.screen.blit(temp_bg, (0, 0))
            
            # Draw fading overlay
            if self.fade_alpha > 0:
                self.overlay.set_alpha(self.fade_alpha)
                self.screen.blit(self.overlay, (0, 0))
        
        elif self.current_phase == "windows_opening":
            # Draw game background (fully visible)
            self.screen.blit(game_background, (0, 0))
            
            # Draw windows with opening animation
            for window in sorted(self.windows, key=lambda w: w.z_index):
                # Create a temporary surface for the window with alpha
                window_surface = pygame.Surface((window.width, window.height), pygame.SRCALPHA)
                
                # Render window content to temporary surface
                # Scale background surface to current window size
                scaled_bg = pygame.transform.scale(window.background_surface, (window.width, window.height))
                window_surface.blit(scaled_bg, (0, 0))
                
                # Render titlebar
                titlebar_rect = pygame.Rect(0, 0, window.width, window.titlebar_height)
                pygame.draw.rect(window_surface, (200, 200, 200), titlebar_rect)
                font = pygame.font.Font(None, 20)
                title_text = font.render(window.title, True, (0, 0, 0))
                text_y = (window.titlebar_height - title_text.get_height()) // 2
                window_surface.blit(title_text, (10, text_y))
                
                # Render window border
                pygame.draw.rect(window_surface, (180, 180, 180), 
                               pygame.Rect(0, 0, window.width, window.height), 2)
                
                # Apply alpha based on opening progress
                window_surface.set_alpha(window.opening_alpha)
                
                # Blit to screen at animated position
                self.screen.blit(window_surface, window.position)
        
        elif self.current_phase == "white_fade":
            # Draw full game background and full window contents,
            # then overlay a fading white screen for a smooth transition
            self.screen.blit(game_background, (0, 0))
            
            # Draw windows with their normal render so content is visible
            for window in sorted(self.windows, key=lambda w: w.z_index):
                # Temporarily ensure full alpha for normal rendering
                if hasattr(window, "opening_alpha"):
                    window.opening_alpha = 255
                # Some windows (like ActivityLogWindow) need special handling
                if hasattr(window, "render_for_startup"):
                    window.render_for_startup(self.screen)
                else:
                    window.render(self.screen)
            
            # White overlay fading out
            if self.post_fade_alpha > 0:
                white_overlay = pygame.Surface((self.width, self.height))
                white_overlay.fill((255, 255, 255))
                white_overlay.set_alpha(self.post_fade_alpha)
                self.screen.blit(white_overlay, (0, 0))