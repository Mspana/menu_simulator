"""
Ending Screen
Displays stats showing the player did nothing and Calvelli did all the work
"""

import pygame
import random
import math

class EndingScreen:
    """The ending screen that reveals the secret"""
    
    def __init__(self, screen, game_state, assets_path):
        self.screen = screen
        self.game_state = game_state
        self.assets_path = assets_path
        
        # Animation state
        self.animation_time = 0
        self.stats = game_state.get_stats()
        
        # Create programmatic background (gradient)
        self.background = pygame.Surface((1920, 1080))
        self._generate_background()
        
        # Text colors
        self.title_color = (255, 215, 0)  # Gold
        self.text_color = (255, 255, 255)  # White
        self.stats_color = (200, 200, 255)  # Light blue
        self.secret_color = (255, 100, 100)  # Red
        self.accent_color = (100, 200, 255)  # Light blue
        
        # Cheering particles (enhanced)
        self.particles = []
        self._generate_particles()
        
        # Confetti pieces
        self.confetti = []
        self._generate_confetti()
        
        # Title animation
        self.title_scale = 0.0
        self.title_target_scale = 1.0
        
        # Stats reveal animation
        self.stats_revealed = False
        self.stats_alpha = 0
        
        # Secret reveal animation
        self.secret_revealed = False
        self.secret_alpha = 0
    
    def _generate_background(self):
        """Generate a gradient background programmatically"""
        # Dark blue to purple gradient
        for y in range(1080):
            # Gradient from dark blue at top to purple at bottom
            r = int(20 + (y / 1080) * 40)  # 20 to 60
            g = int(30 + (y / 1080) * 20)  # 30 to 50
            b = int(60 + (y / 1080) * 80)  # 60 to 140
            pygame.draw.line(self.background, (r, g, b), (0, y), (1920, y))
        
        # Add some subtle stars/twinkles
        for _ in range(100):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            brightness = random.randint(150, 255)
            pygame.draw.circle(self.background, (brightness, brightness, brightness), (x, y), 1)
    
    def _generate_particles(self):
        """Generate celebration particles"""
        for _ in range(80):
            self.particles.append({
                'x': random.randint(0, 1920),
                'y': random.randint(-200, 0),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(2, 5),
                'size': random.randint(4, 12),
                'color': random.choice([
                    (255, 255, 0),    # Yellow
                    (255, 200, 0),    # Gold
                    (255, 100, 0),    # Orange
                    (255, 255, 255),  # White
                    (100, 255, 100),  # Green
                    (255, 100, 255),  # Magenta
                ]),
                'life': random.randint(100, 200)
            })
    
    def _generate_confetti(self):
        """Generate confetti pieces"""
        for _ in range(150):
            self.confetti.append({
                'x': random.randint(0, 1920),
                'y': random.randint(-100, 0),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(1, 4),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-5, 5),
                'size': random.randint(8, 20),
                'color': random.choice([
                    (255, 0, 0),      # Red
                    (0, 255, 0),      # Green
                    (0, 0, 255),      # Blue
                    (255, 255, 0),    # Yellow
                    (255, 0, 255),    # Magenta
                    (0, 255, 255),    # Cyan
                    (255, 165, 0),    # Orange
                ]),
                'shape': random.choice(['rect', 'circle'])
            })
    
    def update(self):
        """Update ending screen animation"""
        self.animation_time += 1
        
        # Animate title scale (bounce in)
        if self.title_scale < self.title_target_scale:
            self.title_scale += 0.05
            if self.title_scale > self.title_target_scale:
                self.title_scale = self.title_target_scale
        
        # Reveal stats after title animation
        if self.animation_time > 60 and not self.stats_revealed:
            self.stats_alpha = min(255, self.stats_alpha + 5)
            if self.stats_alpha >= 255:
                self.stats_revealed = True
        
        # Reveal secret after stats
        if self.animation_time > 240 and not self.secret_revealed:
            self.secret_alpha = min(255, self.secret_alpha + 3)
            if self.secret_alpha >= 255:
                self.secret_revealed = True
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.15  # Gravity
            particle['life'] -= 1
            
            # Reset if off screen or dead
            if particle['y'] > 1080 or particle['life'] <= 0:
                particle['y'] = random.randint(-200, -50)
                particle['x'] = random.randint(0, 1920)
                particle['vx'] = random.uniform(-3, 3)
                particle['vy'] = random.uniform(2, 5)
                particle['life'] = random.randint(100, 200)
        
        # Update confetti
        for piece in self.confetti:
            piece['x'] += piece['vx']
            piece['y'] += piece['vy']
            piece['rotation'] += piece['rotation_speed']
            
            # Reset if off screen
            if piece['y'] > 1080:
                piece['y'] = random.randint(-100, 0)
                piece['x'] = random.randint(0, 1920)
                piece['vx'] = random.uniform(-2, 2)
                piece['vy'] = random.uniform(1, 4)
    
    def render(self):
        """Render the ending screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw confetti
        for piece in self.confetti:
            # Create a small surface for rotated confetti
            confetti_surf = pygame.Surface((piece['size'], piece['size']), pygame.SRCALPHA)
            if piece['shape'] == 'rect':
                pygame.draw.rect(confetti_surf, piece['color'], (0, 0, piece['size'], piece['size']))
            else:
                pygame.draw.circle(confetti_surf, piece['color'], (piece['size']//2, piece['size']//2), piece['size']//2)
            
            # Rotate and draw
            rotated = pygame.transform.rotate(confetti_surf, piece['rotation'])
            rect = rotated.get_rect(center=(int(piece['x']), int(piece['y'])))
            self.screen.blit(rotated, rect)
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
        
        # Draw title with scale animation
        title_font = pygame.font.Font(None, int(72 * self.title_scale))
        title_text = "CONFERENCE FUNDRAISING COMPLETE!"
        
        # Create title with outline
        title_surface = title_font.render(title_text, True, self.title_color)
        title_outline = title_font.render(title_text, True, (0, 0, 0))
        
        title_rect = title_surface.get_rect(center=(960, 120))
        
        # Draw outline (offset)
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    self.screen.blit(title_outline, (title_rect.x + dx, title_rect.y + dy))
        
        # Draw main text
        self.screen.blit(title_surface, title_rect)
        
        # Draw stats panel (with fade-in)
        if self.stats_alpha > 0:
            # Create stats panel background
            panel_width = 800
            panel_height = 400
            panel_x = (1920 - panel_width) // 2
            panel_y = 250
            
            # Semi-transparent panel
            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel_surface.set_alpha(int(self.stats_alpha * 0.9))
            panel_surface.fill((30, 30, 50))
            pygame.draw.rect(panel_surface, (100, 150, 255), 
                           pygame.Rect(0, 0, panel_width, panel_height), 3)
            
            self.screen.blit(panel_surface, (panel_x, panel_y))
            
            # Stats header
            stats_font = pygame.font.Font(None, 56)
            header_text = "Your Statistics"
            header_surface = stats_font.render(header_text, True, self.text_color)
            header_surface.set_alpha(self.stats_alpha)
            header_rect = header_surface.get_rect(center=(960, panel_y + 50))
            self.screen.blit(header_surface, header_rect)
            
            # Individual stats
            small_font = pygame.font.Font(None, 40)
            stats_y = panel_y + 120
            line_height = 50
            
            stats = [
                f"Items Moved: {self.stats['items_moved']}",
                f"Actual Work Done: {self.stats['actual_work_done']:.1f}%",
                f"Time Spent: {int(self.stats['time_elapsed'] // 60)}m {int(self.stats['time_elapsed'] % 60)}s"
            ]
            
            for stat in stats:
                stat_surface = small_font.render(stat, True, self.stats_color)
                stat_surface.set_alpha(self.stats_alpha)
                stat_rect = stat_surface.get_rect(center=(960, stats_y))
                self.screen.blit(stat_surface, stat_rect)
                stats_y += line_height
            
            stats_y += 20
            
            # Calvelli's work (highlighted)
            calvelli_text = f"Calvelli's Work: {self.stats['calvelli_work_done']:.1f}%"
            calvelli_surface = stats_font.render(calvelli_text, True, self.secret_color)
            calvelli_surface.set_alpha(self.stats_alpha)
            calvelli_rect = calvelli_surface.get_rect(center=(960, stats_y))
            self.screen.blit(calvelli_surface, calvelli_rect)
        
        # The secret reveal (with fade-in)
        if self.secret_alpha > 0:
            secret_font = pygame.font.Font(None, 44)
            secret_lines = [
                "THE SECRET:",
                "",
                "You didn't actually do anything!",
                "Calvelli was doing all the work",
                "while you were a tenured professor.",
                "",
                "Thanks for helping!",
            ]
            
            secret_y = 700
            for i, line in enumerate(secret_lines):
                if line:
                    secret_surface = secret_font.render(line, True, self.secret_color)
                    secret_surface.set_alpha(self.secret_alpha)
                    secret_rect = secret_surface.get_rect(center=(960, secret_y + i * 50))
                    self.screen.blit(secret_surface, secret_rect)
        
        # Exit instruction (always visible)
        exit_font = pygame.font.Font(None, 32)
        exit_text = "Press ESC to exit"
        exit_surface = exit_font.render(exit_text, True, (200, 200, 200))
        exit_rect = exit_surface.get_rect(center=(960, 1050))
        self.screen.blit(exit_surface, exit_rect)
        
        # Cheering emojis at bottom
        cheer_font = pygame.font.Font(None, 64)
        cheer_messages = ["🎉", "🎊", "✨", "👏", "🎈", "🌟"]
        cheer_index = (self.animation_time // 20) % len(cheer_messages)
        cheer_text = cheer_messages[cheer_index] * 15
        cheer_surface = cheer_font.render(cheer_text, True, (255, 255, 0))
        cheer_rect = cheer_surface.get_rect(center=(960, 1000))
        self.screen.blit(cheer_surface, cheer_rect)
