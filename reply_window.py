"""
Reply Window
Window for composing and sending email replies
"""

import pygame
import random
from themed_windows import ThemedWindow

class ReplyWindow(ThemedWindow):
    """Window for composing email replies with typing mechanics"""
    
    def __init__(self, email_data, selected_response, position, assets_path, z_index=0):
        title = f"Reply: {email_data.get('subject', 'Email')[:40]}"
        width = 600
        height = 550  # Increased height to fit send button inside
        
        super().__init__(title, position, width, height, assets_path, z_index)
        self.background_surface.fill((255, 255, 255))
        
        self.email_data = email_data
        self.selected_response = selected_response
        self.target_text = selected_response
        self.typed_text = ""
        self.current_letter_index = 0
        self.is_complete = False
        self.should_close = False
        self.sent_reply = None  # Store the reply text when sent
        
        # Response options (all available responses)
        self.all_responses = email_data.get('responses', [])
        self.selected_response_index = self.all_responses.index(selected_response) if selected_response in self.all_responses else 0
        
        # Track send button pressed state so action happens on mouse release
        self._send_button_pressed = False
        
    def handle_keypress(self, key):
        """Handle keyboard input - each key press types one letter"""
        if self.is_complete:
            return False
        
        # Check if we have more letters to type
        if self.current_letter_index < len(self.target_text):
            # Add next letter (ignore the actual key, just advance)
            self.typed_text += self.target_text[self.current_letter_index]
            self.current_letter_index += 1
            
            # Check if complete
            if self.current_letter_index >= len(self.target_text):
                self.is_complete = True
            return True
        return False
    
    def _handle_content_click(self, pos):
        """Handle clicks within the content area"""
        content_y = self.position[1] + self.titlebar_height
        content_x = self.position[0]
        padding = 20
        
        # Check if click is on a response option
        response_start_y = content_y + 60
        for i, response in enumerate(self.all_responses):
            response_rect = pygame.Rect(
                content_x + padding, 
                response_start_y + i * 50, 
                self.width - padding * 2, 
                40
            )
            if response_rect.collidepoint(pos):
                # Select this response
                self.selected_response_index = i
                self.selected_response = response
                self.target_text = response
                self.typed_text = ""
                self.current_letter_index = 0
                self.is_complete = False
                return True
        
        # Calculate send button position (same as in render method)
        y_offset_calc = padding  # Start with padding
        y_offset_calc += 30  # Title
        y_offset_calc += len(self.all_responses) * 50  # Response options
        y_offset_calc += 20  # Spacing after responses
        y_offset_calc += 30  # Divider
        y_offset_calc += 30  # Typing label
        y_offset_calc += 180  # Text box area (150 for box + 30 for spacing/hint)
        
        # Make sure button is within window bounds
        max_y = content_y + self.height - self.titlebar_height - padding - 35
        send_button_y = min(content_y + y_offset_calc, max_y)
        
        send_button_rect = pygame.Rect(
            content_x + self.width - padding - 100,
            send_button_y,
            100,
            35
        )
        if send_button_rect.collidepoint(pos) and self.is_complete:
            # Mark as pressed; actual send happens on mouse release
            self._send_button_pressed = True
            return True
        
        return False
    
    def handle_release(self, pos):
        """Handle mouse release - trigger send after visual feedback"""
        # Let base class clear drag state
        super().handle_release(pos)
        
        content_y = self.position[1] + self.titlebar_height
        content_x = self.position[0]
        padding = 20
        
        # Recalculate send button rect (same as in _handle_content_click/render)
        y_offset_calc = padding  # Start with padding
        y_offset_calc += 30  # Title
        y_offset_calc += len(self.all_responses) * 50  # Response options
        y_offset_calc += 20  # Spacing after responses
        y_offset_calc += 30  # Divider
        y_offset_calc += 30  # Typing label
        y_offset_calc += 180  # Text box area
        
        max_y = content_y + self.height - self.titlebar_height - padding - 35
        send_button_y = min(content_y + y_offset_calc, max_y)
        
        send_button_rect = pygame.Rect(
            content_x + self.width - padding - 100,
            send_button_y,
            100,
            35
        )
        
        if self._send_button_pressed and send_button_rect.collidepoint(pos) and self.is_complete:
            # Send the reply - store it in email data
            self.sent_reply = self.typed_text
            self.email_data['replied'] = True
            self.email_data['reply_text'] = self.typed_text
            self.should_close = True
        # Always reset pressed state
        self._send_button_pressed = False
    
    def render(self, screen):
        screen.blit(self.background_surface, self.position)
        self.render_titlebar(screen)
        
        content_y = self.position[1] + self.titlebar_height
        content_x = self.position[0]
        padding = 20
        
        font_title = pygame.font.Font(None, 20)
        font_text = pygame.font.Font(None, 18)
        font_small = pygame.font.Font(None, 16)
        
        y_offset = padding
        
        # Title
        title_text = font_title.render("Select a response:", True, (0, 0, 0))
        screen.blit(title_text, (content_x + padding, content_y + y_offset))
        y_offset += 30
        
        # Response options
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
        for i, response in enumerate(self.all_responses):
            response_rect = pygame.Rect(
                content_x + padding, 
                content_y + y_offset, 
                self.width - padding * 2, 
                40
            )
            
            # Base color: selected vs normal
            if i == self.selected_response_index:
                base_color = (220, 235, 255)
            else:
                base_color = (250, 250, 250)
            
            # Click feedback: darken slightly when pressed
            if response_rect.collidepoint(mouse_pos) and mouse_buttons[0]:
                draw_color = tuple(max(0, c - 20) for c in base_color)
            else:
                draw_color = base_color
            
            pygame.draw.rect(screen, draw_color, response_rect)
            pygame.draw.rect(screen, (200, 200, 200), response_rect, 1)
            
            # Response text
            response_text = font_text.render(response, True, (0, 0, 0))
            text_rect = response_text.get_rect(center=response_rect.center)
            screen.blit(response_text, text_rect)
            
            y_offset += 50
        
        y_offset += 20
        
        # Divider
        pygame.draw.line(screen, (200, 200, 200), 
                        (content_x + padding, content_y + y_offset),
                        (content_x + self.width - padding, content_y + y_offset), 1)
        y_offset += 30
        
        # Typing area
        typing_label = font_title.render("Type your reply:", True, (0, 0, 0))
        screen.blit(typing_label, (content_x + padding, content_y + y_offset))
        y_offset += 30
        
        # Text box
        text_box_rect = pygame.Rect(
            content_x + padding,
            content_y + y_offset,
            self.width - padding * 2,
            150
        )
        pygame.draw.rect(screen, (255, 255, 255), text_box_rect)
        pygame.draw.rect(screen, (150, 150, 150), text_box_rect, 2)
        
        # Display typed text
        if self.typed_text:
            # Wrap text for display
            words = self.typed_text.split(' ')
            lines = []
            current_line = ""
            max_width = text_box_rect.width - 10
            
            for word in words:
                test_line = current_line + word + " " if current_line else word + " "
                if font_text.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            
            # Draw lines
            for i, line in enumerate(lines[:8]):  # Max 8 lines
                line_text = font_text.render(line, True, (0, 0, 0))
                screen.blit(line_text, (content_x + padding + 5, content_y + y_offset + 5 + i * 20))
        
        # Show remaining letters to type
        if not self.is_complete:
            remaining = len(self.target_text) - self.current_letter_index
            hint_text = font_small.render(f"Press any key to type... ({remaining} letters remaining)", True, (150, 150, 150))
            screen.blit(hint_text, (content_x + padding, content_y + y_offset + 160))
        
        y_offset += 180
        
        # Send button - position it within the window bounds
        # Make sure it fits within the window height
        max_y = content_y + self.height - self.titlebar_height - padding - 35
        send_button_y = min(content_y + y_offset, max_y)
        
        send_button_rect = pygame.Rect(
            content_x + self.width - padding - 100,
            send_button_y,
            100,
            35
        )
        
        # Button color based on completion, with click feedback
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
        if self.is_complete:
            base_color = (50, 200, 50)  # Green
            text_color = (255, 255, 255)
        else:
            base_color = (200, 200, 200)  # Grey
            text_color = (100, 100, 100)
        
        if send_button_rect.collidepoint(mouse_pos) and mouse_buttons[0]:
            button_color = tuple(max(0, c - 30) for c in base_color)
        else:
            button_color = base_color
        
        pygame.draw.rect(screen, button_color, send_button_rect)
        pygame.draw.rect(screen, (150, 150, 150), send_button_rect, 1)
        
        send_text = font_text.render("Send", True, text_color)
        text_rect = send_text.get_rect(center=send_button_rect.center)
        screen.blit(send_text, text_rect)
        
        # Window border
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)
