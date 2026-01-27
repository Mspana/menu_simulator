"""
Start Screen
The initial screen before the game starts
"""

import pygame
import sys
import time
import math

class StartScreen:
    """The start screen shown before the game begins"""
    
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clicked = False
        self.start_time = time.time()
        
        # Create gradient background
        self.background = pygame.Surface((self.width, self.height))
        self._draw_gradient_background()
        
        # Fonts (larger main menu typography)
        self.title_font = pygame.font.Font(None, 128)
        self.subtitle_font = pygame.font.Font(None, 44)
        self.instruction_font = pygame.font.Font(None, 36)
        self.tagline_font = pygame.font.Font(None, 24)
        
        # Animation state
        self.pulse_phase = 0.0
        self.glow_phase = 0.0
        
    def _draw_gradient_background(self):
        """Draw a gradient background from dark blue to darker blue"""
        for y in range(self.height):
            # Gradient from (15, 20, 35) at top to (5, 10, 20) at bottom
            ratio = y / self.height
            r = int(15 - (10 * ratio))
            g = int(20 - (10 * ratio))
            b = int(35 - (15 * ratio))
            pygame.draw.line(self.background, (r, g, b), (0, y), (self.width, y))
        
        # Add some subtle grid pattern
        grid_color = (10, 15, 25)
        grid_spacing = 50
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(self.background, grid_color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(self.background, grid_color, (0, y), (self.width, y), 1)
        
    def handle_click(self, pos):
        """Handle click - any click starts the game"""
        self.clicked = True
        return True
    
    def handle_keypress(self, key):
        """Handle keypress - any key starts the game"""
        if key == pygame.K_SPACE or key == pygame.K_RETURN:
            self.clicked = True
            return True
        return False
    
    def is_done(self):
        """Check if start screen is done"""
        return self.clicked
    
    def render(self):
        """Render the start screen"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Update animation phases
        self.pulse_phase = elapsed * 2.0  # Pulse animation
        self.glow_phase = elapsed * 1.5  # Glow animation
        
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw decorative corner elements
        corner_size = 200
        corner_thickness = 3
        corner_color = (100, 150, 200)
        
        # Top-left corner
        pygame.draw.line(self.screen, corner_color, (50, 50), (50 + corner_size, 50), corner_thickness)
        pygame.draw.line(self.screen, corner_color, (50, 50), (50, 50 + corner_size), corner_thickness)
        
        # Top-right corner
        pygame.draw.line(self.screen, corner_color, (self.width - 50, 50), (self.width - 50 - corner_size, 50), corner_thickness)
        pygame.draw.line(self.screen, corner_color, (self.width - 50, 50), (self.width - 50, 50 + corner_size), corner_thickness)
        
        # Bottom-left corner
        pygame.draw.line(self.screen, corner_color, (50, self.height - 50), (50 + corner_size, self.height - 50), corner_thickness)
        pygame.draw.line(self.screen, corner_color, (50, self.height - 50), (50, self.height - 50 - corner_size), corner_thickness)
        
        # Bottom-right corner
        pygame.draw.line(self.screen, corner_color, (self.width - 50, self.height - 50), (self.width - 50 - corner_size, self.height - 50), corner_thickness)
        pygame.draw.line(self.screen, corner_color, (self.width - 50, self.height - 50), (self.width - 50, self.height - 50 - corner_size), corner_thickness)
        
        # Title with glow effect
        title_y = self.height // 2 - 120
        pulse_offset = math.sin(self.pulse_phase) * 3  # Subtle pulsing
        
        # Glow effect (multiple layers)
        glow_intensity = int(50 + 30 * math.sin(self.glow_phase))
        for i in range(3):
            glow_alpha = glow_intensity // (i + 1)
            glow_color = (glow_alpha, glow_alpha, glow_alpha + 50)
            title_glow = self.title_font.render("Menu Simulator", True, glow_color)
            glow_rect = title_glow.get_rect(center=(self.width // 2 + i, title_y + i + pulse_offset))
            self.screen.blit(title_glow, glow_rect)
        
        # Main title
        title_text = self.title_font.render("Menu Simulator", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, title_y + pulse_offset))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle with underline
        subtitle_y = title_y + 80
        subtitle_text = self.subtitle_font.render("Fundraising for a Conference", True, (180, 200, 255))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, subtitle_y))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Underline
        underline_y = subtitle_y + 25
        underline_width = subtitle_text.get_width() + 40
        underline_x = self.width // 2 - underline_width // 2
        pygame.draw.line(self.screen, (100, 150, 200), 
                        (underline_x, underline_y), 
                        (underline_x + underline_width, underline_y), 2)
        
        # Tagline
        tagline_y = subtitle_y + 60
        tagline_text = self.tagline_font.render("A game about clicking menus while someone else does the work", True, (120, 140, 160))
        tagline_rect = tagline_text.get_rect(center=(self.width // 2, tagline_y))
        self.screen.blit(tagline_text, tagline_rect)
        
        # Instructions with pulsing effect
        instruction_y = self.height // 2 + 150
        instruction_alpha = int(150 + 50 * math.sin(self.pulse_phase))
        instruction_color = (instruction_alpha, instruction_alpha, instruction_alpha)
        
        instruction_text = self.instruction_font.render("Click anywhere or press SPACE to start", True, instruction_color)
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, instruction_y))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Decorative line above instructions
        line_y = instruction_y - 40
        line_width = 300
        line_x = self.width // 2 - line_width // 2
        line_alpha = int(100 + 30 * math.sin(self.pulse_phase))
        line_color = (line_alpha, line_alpha, line_alpha)
        pygame.draw.line(self.screen, line_color, (line_x, line_y), (line_x + line_width, line_y), 1)
        
        # Keyboard hint
        hint_y = instruction_y + 50
        hint_text = self.tagline_font.render("Press ESC to exit at any time", True, (80, 90, 100))
        hint_rect = hint_text.get_rect(center=(self.width // 2, hint_y))
        self.screen.blit(hint_text, hint_rect)
        
        # Version/credit text at bottom
        credit_y = self.height - 60
        version_text = self.tagline_font.render("Menu Simulator v1.0", True, (60, 70, 80))
        version_rect = version_text.get_rect(center=(self.width // 2, credit_y))
        self.screen.blit(version_text, version_rect)
        
        # Author credit just below
        author_y = credit_y + 20
        author_text = self.tagline_font.render("A game by gblwrks", True, (80, 90, 100))
        author_rect = author_text.get_rect(center=(self.width // 2, author_y))
        self.screen.blit(author_text, author_rect)
