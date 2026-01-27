"""
Menu Window System
Handles overlapping windows, drag and drop, and menu items
"""

import pygame
import os

class MenuItem:
    """A draggable item within a menu window"""
    def __init__(self, image_filename, position, assets_path):
        self.image_filename = image_filename
        self.assets_path = assets_path
        self.image = pygame.image.load(
            os.path.join(assets_path, image_filename)
        ).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.dragging = False
        self.drag_offset = (0, 0)
        self.original_menu = None  # Track which menu this item belongs to
    
    def handle_click(self, pos):
        """Check if item was clicked (pos is window-relative)"""
        if self.rect.collidepoint(pos):
            self.dragging = True
            # Store offset relative to click position (for window-relative dragging)
            self.drag_offset = (pos[0] - self.rect.x, pos[1] - self.rect.y)
            return True
        return False
    
    def handle_drag(self, pos):
        """Update position while dragging"""
        if self.dragging:
            # If dragging started, pos is already in the correct coordinate system
            # (global if called from game, relative if called from menu)
            self.rect.x = pos[0] - self.drag_offset[0]
            self.rect.y = pos[1] - self.drag_offset[1]
    
    def handle_release(self, pos):
        """Stop dragging"""
        self.dragging = False
    
    def render(self, screen, offset=(0, 0)):
        """Render the menu item"""
        screen.blit(self.image, (self.rect.x + offset[0], self.rect.y + offset[1]))

class MenuWindow:
    """A window that can contain menu items and be dragged around"""
    def __init__(self, title, position, width, height, assets_path, z_index=0):
        self.title = title
        self.position = list(position)
        self.width = width
        self.height = height
        self.assets_path = assets_path
        self.z_index = z_index
        self.items = []
        self.dragging = False
        self.drag_offset = (0, 0)
        self.is_blocked = False  # Blocked by Discord interruption
        
        # Load window assets
        # Use only the background, not the overlay (which may have text baked in)
        try:
            titlebar_img = pygame.image.load(
                os.path.join(assets_path, "window_titlebar_background_800x40.png")
            ).convert_alpha()
            # Scale to match window width
            if titlebar_img.get_width() != self.width:
                self.titlebar_bg = pygame.transform.scale(titlebar_img, (self.width, 40))
            else:
                self.titlebar_bg = titlebar_img
        except:
            # Fallback: create a simple Windows-style titlebar
            self.titlebar_bg = pygame.Surface((self.width, 40))
            # Windows 10/11 style blue gradient
            for y in range(40):
                color_val = int(240 - (y / 40) * 20)  # Slight gradient
                pygame.draw.line(self.titlebar_bg, (color_val, color_val, color_val), (0, y), (self.width, y))
        
        self.close_icon = pygame.image.load(
            os.path.join(assets_path, "icon_close_x_20x20.png")
        ).convert_alpha()
        self.minimize_icon = pygame.image.load(
            os.path.join(assets_path, "icon_minimize_20x20.png")
        ).convert_alpha()
        
        # Calculate button positions
        self.titlebar_height = 40
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
        
        # Window content area
        self.content_rect = pygame.Rect(
            self.position[0],
            self.position[1] + self.titlebar_height,
            self.width,
            self.height - self.titlebar_height
        )
        
        # Window background (simple gray with subtle border effect)
        self.background_surface = pygame.Surface((self.width, self.height))
        self.background_surface.fill((250, 250, 250))
        # Add subtle inner border
        pygame.draw.rect(self.background_surface, (220, 220, 220), 
                        pygame.Rect(0, 0, self.width, self.height), 1)
    
    def add_item(self, item):
        """Add a menu item to this window"""
        item.original_menu = self
        self.items.append(item)
    
    def handle_click(self, pos):
        """Handle click on this window"""
        if self.is_blocked:
            return False
        
        # Check if click is anywhere within window bounds first
        window_rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        if not window_rect.collidepoint(pos):
            return False
        
        # Click is within window - bring to front will be handled by game.py
        # But we still need to handle specific interactions
        
        # Check close button
        if self.close_button_rect.collidepoint(pos):
            # Don't actually close, just return True to indicate click was handled
            return True
        
        # Check minimize button
        if self.minimize_button_rect.collidepoint(pos):
            # Could implement minimize here
            return True
        
        # Click is within window - bring to front will be handled by game.py
        # But we still need to handle specific interactions
        
        # Check titlebar for dragging
        if self.titlebar_rect.collidepoint(pos):
            self.dragging = True
            self.drag_offset = (pos[0] - self.position[0], pos[1] - self.position[1])
            return True
        
        # Check items (relative to window position)
        window_relative_pos = (
            pos[0] - self.position[0],
            pos[1] - self.position[1] - self.titlebar_height
        )
        for item in self.items:
            if item.handle_click(window_relative_pos):
                return True
        
        # Click was within window but not on any specific element - still bring to front
        return True
        window_rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        return window_rect.collidepoint(pos)
    
    def handle_drag(self, pos):
        """Handle drag on this window (pos is global)"""
        if self.dragging:
            self.position[0] = pos[0] - self.drag_offset[0]
            self.position[1] = pos[1] - self.drag_offset[1]
            # Update button positions
            self._update_button_positions()
        
        # Handle item dragging - convert to window-relative for items
        window_relative_pos = (
            pos[0] - self.position[0],
            pos[1] - self.position[1] - self.titlebar_height
        )
        for item in self.items:
            if item.dragging:
                # Item is being dragged, but we need to track it in global coords
                # So we'll handle it at the game level instead
                pass
            else:
                item.handle_drag(window_relative_pos)
    
    def handle_release(self, pos):
        """Handle mouse release"""
        self.dragging = False
        
        # Release any dragging items
        window_relative_pos = (
            pos[0] - self.position[0],
            pos[1] - self.position[1] - self.titlebar_height
        )
        for item in self.items:
            if item.dragging:
                item.handle_release(window_relative_pos)
    
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
        self.content_rect = pygame.Rect(
            self.position[0],
            self.position[1] + self.titlebar_height,
            self.width,
            self.height - self.titlebar_height
        )
    
    def contains_point(self, pos):
        """Check if point is within this window"""
        window_rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        return window_rect.collidepoint(pos)
    
    def render(self, screen):
        """Render the window"""
        # Draw window background
        screen.blit(self.background_surface, self.position)
        
        # Draw titlebar background
        screen.blit(self.titlebar_bg, (self.position[0], self.position[1]))
        
        # Draw title text (with better styling)
        font = pygame.font.Font(None, 20)
        title_text = font.render(self.title, True, (255, 255, 255))
        # Center vertically in titlebar
        text_y = self.position[1] + (self.titlebar_height - title_text.get_height()) // 2
        screen.blit(title_text, (self.position[0] + 10, text_y))
        
        # Draw buttons
        screen.blit(self.close_icon, self.close_button_rect.topleft)
        screen.blit(self.minimize_icon, self.minimize_button_rect.topleft)
        
        # Draw items
        item_offset = (self.position[0], self.position[1] + self.titlebar_height)
        for item in self.items:
            item.render(screen, item_offset)
        
        # Draw window border
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)
