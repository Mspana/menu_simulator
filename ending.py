"""
Ending Screen
Displays stats showing the player did nothing and Calvelli did all the work
"""

import pygame
import os

class EndingScreen:
    """The ending screen that reveals the secret"""
    
    def __init__(self, screen, game_state, assets_path):
        self.screen = screen
        self.game_state = game_state
        self.assets_path = assets_path
        
        # Load ending background
        bg_path = os.path.join(assets_path, "backgrounds", "ending_celebration_background_1920x1080.png")
        self.background = pygame.image.load(bg_path).convert()
        
        # Animation state
        self.animation_time = 0
        self.stats = game_state.get_stats()
        
        # Text colors
        self.title_color = (255, 255, 0)  # Yellow
        self.text_color = (255, 255, 255)  # White
        self.stats_color = (255, 200, 0)  # Gold
        self.secret_color = (255, 100, 100)  # Red
        
        # Cheering particles (simple)
        self.particles = []
        self._generate_particles()
    
    def _generate_particles(self):
        """Generate celebration particles"""
        import random
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, 1920),
                'y': random.randint(0, 1080),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-3, -1),
                'size': random.randint(3, 8),
                'color': random.choice([
                    (255, 255, 0),
                    (255, 200, 0),
                    (255, 100, 0),
                    (255, 255, 255)
                ])
            })
    
    def update(self):
        """Update ending screen animation"""
        self.animation_time += 1
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravity
            
            # Reset if off screen
            if particle['y'] > 1080:
                particle['y'] = -10
                particle['x'] = pygame.time.get_ticks() % 1920
    
    def render(self):
        """Render the ending screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
        
        # Draw title (with animation)
        title_font = pygame.font.Font(None, 72)
        title_text = "CONFERENCE FUNDRAISING COMPLETE!"
        title_surface = title_font.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(960, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Draw stats
        stats_font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 36)
        
        stats_y = 300
        line_height = 60
        
        # Stats header
        header_text = "Your Statistics:"
        header_surface = stats_font.render(header_text, True, self.text_color)
        header_rect = header_surface.get_rect(center=(960, stats_y))
        self.screen.blit(header_surface, header_rect)
        
        stats_y += line_height * 2
        
        # Individual stats
        stats = [
            f"Items Moved: {self.stats['items_moved']}",
            f"Actual Work Done: {self.stats['actual_work_done']:.1f}%",
            f"Time Spent: {int(self.stats['time_elapsed'] // 60)}m {int(self.stats['time_elapsed'] % 60)}s"
        ]
        
        for stat in stats:
            stat_surface = small_font.render(stat, True, self.stats_color)
            stat_rect = stat_surface.get_rect(center=(960, stats_y))
            self.screen.blit(stat_surface, stat_rect)
            stats_y += line_height
        
        stats_y += line_height
        
        # Calvelli's work
        calvelli_text = f"Calvelli's Work: {self.stats['calvelli_work_done']:.1f}%"
        calvelli_surface = stats_font.render(calvelli_text, True, self.secret_color)
        calvelli_rect = calvelli_surface.get_rect(center=(960, stats_y))
        self.screen.blit(calvelli_surface, calvelli_rect)
        
        stats_y += line_height * 2
        
        # The secret reveal
        if self.animation_time > 180:  # Show after 3 seconds
            secret_font = pygame.font.Font(None, 40)
            secret_lines = [
                "THE SECRET:",
                "",
                "You didn't actually do anything!",
                "Calvelli was doing all the work",
                "while you were clicking menus.",
                "",
                "Thanks for 'helping'!",
                "",
                "Press ESC to exit"
            ]
            
            for i, line in enumerate(secret_lines):
                if line:
                    secret_surface = secret_font.render(line, True, self.secret_color)
                    secret_rect = secret_surface.get_rect(center=(960, stats_y + i * 45))
                    self.screen.blit(secret_surface, secret_rect)
        
        # Cheering text animation
        cheer_font = pygame.font.Font(None, 56)
        cheer_messages = ["🎉", "🎊", "✨", "👏", "🎈"]
        cheer_index = (self.animation_time // 30) % len(cheer_messages)
        cheer_text = cheer_messages[cheer_index] * 10
        cheer_surface = cheer_font.render(cheer_text, True, (255, 255, 0))
        cheer_rect = cheer_surface.get_rect(center=(960, 1000))
        self.screen.blit(cheer_surface, cheer_rect)
