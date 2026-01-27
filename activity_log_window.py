"""
Activity Log Window
A dedicated window showing Calvelli's activities and progress
"""

import pygame
import os

class ActivityLogWindow:
    """Window displaying activity log and progress bar"""
    
    def __init__(self, position, width, height, assets_path, z_index=0):
        self.position = list(position)
        self.width = width
        self.height = height
        self.assets_path = assets_path
        self.z_index = z_index
        self.dragging = False
        self.drag_offset = (0, 0)
        self.is_blocked = False
        
        # Activity history
        self.activities = []  # List of (message, timestamp) tuples
        self.max_activities = 50  # Keep last 50 activities
        
        # Load window assets
        self.titlebar_height = 40
        try:
            titlebar_img = pygame.image.load(
                os.path.join(assets_path, "ui", "window_titlebar_background_800x40.png")
            ).convert_alpha()
            if titlebar_img.get_width() != self.width:
                self.titlebar_bg = pygame.transform.scale(titlebar_img, (self.width, 40))
            else:
                self.titlebar_bg = titlebar_img
        except:
            self.titlebar_bg = pygame.Surface((self.width, 40))
            self.titlebar_bg.fill((200, 200, 200))
        
        self.close_icon = pygame.image.load(
            os.path.join(assets_path, "ui", "icon_close_x_20x20.png")
        ).convert_alpha()
        self.minimize_icon = pygame.image.load(
            os.path.join(assets_path, "ui", "icon_minimize_20x20.png")
        ).convert_alpha()
        
        # Button positions
        self.close_button_rect = pygame.Rect(
            self.position[0] + self.width - 25,
            self.position[1] + 10,
            20, 20
        )
        self.minimize_button_rect = pygame.Rect(
            self.position[0] + self.width - 50,
            self.position[1] + 10,
            20, 20
        )
        self.titlebar_rect = pygame.Rect(
            self.position[0],
            self.position[1],
            self.width,
            self.titlebar_height
        )
        
        # Window background - different color (dark blue-gray)
        self.background_surface = pygame.Surface((self.width, self.height))
        self.background_surface.fill((40, 50, 70))
        
        # Progress bar assets
        self.progress_bar_frame = None
        self.progress_bar_fill = None
        self._load_progress_bar_assets()
    
    def _load_progress_bar_assets(self):
        """Load progress bar assets"""
        try:
            ui_path = os.path.join(self.assets_path, "ui")
            frame_img = pygame.image.load(
                os.path.join(ui_path, "progress_bar_frame_600x30.png")
            ).convert_alpha()
            fill_img = pygame.image.load(
                os.path.join(ui_path, "progress_bar_fill_full_600x30.png")
            ).convert_alpha()
            # Scale to fit window width
            bar_width = self.width - 40
            self.progress_bar_frame = pygame.transform.scale(frame_img, (bar_width, 30))
            self.progress_bar_fill = pygame.transform.scale(fill_img, (bar_width, 30))
        except:
            # Fallback: create simple progress bars
            bar_width = self.width - 40
            self.progress_bar_frame = pygame.Surface((bar_width, 30))
            self.progress_bar_frame.fill((200, 200, 200))
            self.progress_bar_fill = pygame.Surface((bar_width, 30))
            self.progress_bar_fill.fill((0, 120, 212))
    
    def add_activity(self, message, progress_increase=None):
        """Add a new activity to the log"""
        import time
        timestamp = time.time()
        self.activities.append((message, timestamp, progress_increase))
        # Keep only the most recent activities
        if len(self.activities) > self.max_activities:
            self.activities.pop(0)
    
    def _update_button_positions(self):
        """Update button positions when window is moved"""
        self.close_button_rect = pygame.Rect(
            self.position[0] + self.width - 25,
            self.position[1] + 10,
            20, 20
        )
        self.minimize_button_rect = pygame.Rect(
            self.position[0] + self.width - 50,
            self.position[1] + 10,
            20, 20
        )
        self.titlebar_rect = pygame.Rect(
            self.position[0],
            self.position[1],
            self.width,
            self.titlebar_height
        )
    
    def handle_click(self, pos):
        """Handle click on window"""
        if self.is_blocked:
            return False
        
        if self.close_button_rect.collidepoint(pos) or self.minimize_button_rect.collidepoint(pos):
            return True
        
        if self.titlebar_rect.collidepoint(pos):
            self.dragging = True
            self.drag_offset = (pos[0] - self.position[0], pos[1] - self.position[1])
            return True
        
        return False
    
    def handle_drag(self, pos):
        """Handle drag"""
        if self.dragging:
            self.position[0] = pos[0] - self.drag_offset[0]
            self.position[1] = pos[1] - self.drag_offset[1]
            self._update_button_positions()
    
    def handle_release(self, pos):
        """Handle mouse release"""
        self.dragging = False
    
    def contains_point(self, pos):
        """Check if point is within window"""
        window_rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        return window_rect.collidepoint(pos)
    
    def render(self, screen, progress):
        """Render the activity log window"""
        # Draw window background
        screen.blit(self.background_surface, self.position)
        
        # Draw titlebar
        screen.blit(self.titlebar_bg, (self.position[0], self.position[1]))
        font = pygame.font.Font(None, 20)
        title_text = font.render("Activity Log", True, (0, 0, 0))  # Black text
        text_y = self.position[1] + (self.titlebar_height - title_text.get_height()) // 2
        screen.blit(title_text, (self.position[0] + 10, text_y))
        screen.blit(self.close_icon, self.close_button_rect.topleft)
        screen.blit(self.minimize_icon, self.minimize_button_rect.topleft)
        
        content_y = self.position[1] + self.titlebar_height + 20
        
        # Draw progress text above bar (centered, red with black outline)
        progress_font = pygame.font.Font(None, 24)
        progress_text = f"Conference Fundraising Progress: {progress:.1f}%"
        
        # Create text with outline
        text_surface = progress_font.render(progress_text, True, (255, 0, 0))  # Red text
        outline_surface = progress_font.render(progress_text, True, (0, 0, 0))  # Black outline
        
        # Calculate centered position
        bar_x = self.position[0] + 20
        bar_width = self.width - 40
        text_x = bar_x + (bar_width - text_surface.get_width()) // 2
        text_y = content_y - 5  # Move text up a little
        
        # Draw outline (offset by 1 pixel in each direction)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    screen.blit(outline_surface, (text_x + dx, text_y + dy))
        
        # Draw main text
        screen.blit(text_surface, (text_x, text_y))
        
        # Draw progress bar (with space below text)
        bar_y = content_y + 15  # Move bar down a little to create space
        screen.blit(self.progress_bar_frame, (bar_x, bar_y))
        
        # Draw progress fill
        progress = min(progress, 100.0)
        fill_width = int(bar_width * (progress / 100.0))
        if fill_width > 0:
            fill_surface = pygame.Surface((fill_width, 30), pygame.SRCALPHA)
            fill_surface.blit(self.progress_bar_fill, (0, 0), (0, 0, fill_width, 30))
            screen.blit(fill_surface, (bar_x, bar_y))
        
        # Draw activity log
        log_start_y = content_y + 70
        log_font = pygame.font.Font(None, 18)
        log_area_height = self.height - self.titlebar_height - 120  # Leave space for progress bar
        
        # Draw activities (most recent at top) - larger cards
        y_offset = log_start_y
        card_height = 40  # Larger cards
        for i, activity_data in enumerate(reversed(self.activities)):
            if y_offset > self.position[1] + self.height - 20:
                break  # Don't draw outside window
            
            # Unpack activity data (handle both old format and new format)
            if len(activity_data) == 3:
                message, timestamp, progress_increase = activity_data
            else:
                message, timestamp = activity_data
                progress_increase = None
            
            # Alternate background for readability (larger cards)
            if i % 2 == 0:
                pygame.draw.rect(screen, (50, 60, 80),
                               pygame.Rect(self.position[0] + 10, y_offset - 2, 
                                         self.width - 20, card_height))
            else:
                pygame.draw.rect(screen, (45, 55, 75),
                               pygame.Rect(self.position[0] + 10, y_offset - 2, 
                                         self.width - 20, card_height))
            
            # Draw activity text (larger font)
            activity_font = pygame.font.Font(None, 22)
            text_surface = activity_font.render(message, True, (255, 255, 255))
            screen.blit(text_surface, (self.position[0] + 15, y_offset + 5))
            
            # Draw progress increase if available (on new line)
            if progress_increase is not None and progress_increase > 0:
                increase_font = pygame.font.Font(None, 18)
                increase_text = increase_font.render(f"Progress increased: +{progress_increase:.1f}%", True, (100, 255, 100))
                screen.blit(increase_text, (self.position[0] + 15, y_offset + 25))
            
            y_offset += card_height + 2
        
        # Draw border
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)
