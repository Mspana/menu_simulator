"""
Email View Window
A separate window for displaying full email content
"""

import pygame
from themed_windows import ThemedWindow

class EmailViewWindow(ThemedWindow):
    """Window for displaying full email content"""
    
    def __init__(self, email_data, position, assets_path, z_index=0):
        # Create window title from email subject
        title = email_data.get('subject', 'Email')[:50]  # Limit title length
        width = 700
        height = 600
        
        super().__init__(title, position, width, height, assets_path, z_index)
        self.background_surface.fill((255, 255, 255))
        
        self.email_data = email_data
        self.scroll_offset = 0
        self.max_scroll = 0
        self.should_close = False
        self.reply_to_open = None  # Signal to open reply window
        
    def _handle_content_click(self, pos):
        """Handle clicks within the content area"""
        content_y = self.position[1] + self.titlebar_height
        content_x = self.position[0]
        padding = 20
        
        # Check if click is on Reply button (for congratulatory emails)
        if 'responses' in self.email_data:
            # Calculate Reply button position (top right of content area)
            reply_button_rect = pygame.Rect(
                content_x + self.width - padding - 100,
                content_y + padding,
                100,
                30
            )
            if reply_button_rect.collidepoint(pos):
                # Open reply window with first response as default
                self.reply_to_open = self.email_data['responses'][0]
                return True
        
        return False
    
    def render(self, screen):
        screen.blit(self.background_surface, self.position)
        self.render_titlebar(screen)
        
        content_y = self.position[1] + self.titlebar_height
        content_x = self.position[0]
        padding = 20
        
        # Email header
        font_title = pygame.font.Font(None, 24)
        font_label = pygame.font.Font(None, 16)
        font_message = pygame.font.Font(None, 18)
        
        y_offset = padding
        
        # Subject
        subject_text = font_title.render(self.email_data.get('subject', 'No Subject'), True, (0, 0, 0))
        screen.blit(subject_text, (content_x + padding, content_y + y_offset))
        y_offset += 35
        
        # From
        from_label = font_label.render("From:", True, (100, 100, 100))
        screen.blit(from_label, (content_x + padding, content_y + y_offset))
        from_text = font_label.render(self.email_data.get('from', 'Unknown'), True, (0, 0, 0))
        screen.blit(from_text, (content_x + padding + 50, content_y + y_offset))
        y_offset += 25
        
        # Time
        time_label = font_label.render("Time:", True, (100, 100, 100))
        screen.blit(time_label, (content_x + padding, content_y + y_offset))
        time_text = font_label.render(self.email_data.get('time', ''), True, (0, 0, 0))
        screen.blit(time_text, (content_x + padding + 50, content_y + y_offset))
        y_offset += 30
        
        # Divider
        pygame.draw.line(screen, (200, 200, 200), 
                        (content_x + padding, content_y + y_offset),
                        (content_x + self.width - padding, content_y + y_offset), 1)
        y_offset += 20
        
        # Email message
        if 'message' in self.email_data:
            # Wrap message text
            message = self.email_data['message']
            words = message.split(' ')
            lines = []
            current_line = ""
            max_width = self.width - padding * 2
            
            for word in words:
                test_line = current_line + word + " " if current_line else word + " "
                if font_message.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            
            # Draw message lines
            for i, line in enumerate(lines):
                if content_y + y_offset + i * 22 < content_y + self.height - 200:  # Leave space for reply
                    line_text = font_message.render(line, True, (0, 0, 0))
                    screen.blit(line_text, (content_x + padding, content_y + y_offset + i * 22))
            
            y_offset += len(lines) * 22 + 30
        else:
            # Regular email - show placeholder
            placeholder = font_message.render("Email content not available", True, (150, 150, 150))
            screen.blit(placeholder, (content_x + padding, content_y + y_offset))
            y_offset += 30
        
        # Show reply if email has been replied to
        if self.email_data.get('replied', False) and self.email_data.get('reply_text'):
            y_offset += 20
            # Divider before reply
            pygame.draw.line(screen, (200, 200, 200), 
                            (content_x + padding, content_y + y_offset),
                            (content_x + self.width - padding, content_y + y_offset), 1)
            y_offset += 20
            
            # Reply header
            reply_label = font_title.render("Your Reply:", True, (0, 120, 212))
            screen.blit(reply_label, (content_x + padding, content_y + y_offset))
            y_offset += 30
            
            # Reply text (wrapped)
            reply_text = self.email_data['reply_text']
            reply_words = reply_text.split(' ')
            reply_lines = []
            current_line = ""
            max_width = self.width - padding * 2
            
            for word in reply_words:
                test_line = current_line + word + " " if current_line else word + " "
                if font_message.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        reply_lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                reply_lines.append(current_line.strip())
            
            # Draw reply lines with different background
            reply_bg_rect = pygame.Rect(
                content_x + padding - 5,
                content_y + y_offset - 5,
                self.width - padding * 2 + 10,
                len(reply_lines) * 22 + 10
            )
            pygame.draw.rect(screen, (240, 250, 240), reply_bg_rect)  # Light green background
            pygame.draw.rect(screen, (200, 220, 200), reply_bg_rect, 1)  # Border
            
            for i, line in enumerate(reply_lines):
                if content_y + y_offset + i * 22 < content_y + self.height - 100:
                    line_text = font_message.render(line, True, (0, 0, 0))
                    screen.blit(line_text, (content_x + padding, content_y + y_offset + i * 22))
            
            y_offset += len(reply_lines) * 22 + 10
        
        # Reply button (for congratulatory emails)
        if 'responses' in self.email_data:
            reply_button_rect = pygame.Rect(
                content_x + self.width - padding - 100,
                content_y + padding,
                100,
                30
            )
            
            # Button background
            pygame.draw.rect(screen, (0, 120, 212), reply_button_rect)
            pygame.draw.rect(screen, (0, 100, 180), reply_button_rect, 1)
            
            # Reply text
            reply_font = pygame.font.Font(None, 16)
            reply_text = reply_font.render("Reply", True, (255, 255, 255))
            text_rect = reply_text.get_rect(center=reply_button_rect.center)
            screen.blit(reply_text, text_rect)
        
        # Window border
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)
