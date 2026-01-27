"""
Themed Window Classes
Different application-style windows for the game
"""

import pygame
import os
import random
import time

class ThemedWindow:
    """Base class for themed windows"""
    def __init__(self, title, position, width, height, assets_path, z_index=0):
        self.title = title
        self.position = list(position)
        self.width = width
        self.height = height
        self.assets_path = assets_path
        self.z_index = z_index
        self.dragging = False
        self.drag_offset = (0, 0)
        self.is_blocked = False
        
        # Load common assets
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
        
        # Window background
        self.background_surface = pygame.Surface((self.width, self.height))
        self.background_surface.fill((250, 250, 250))
    
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
        
        # Check if click is anywhere within window bounds
        window_rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        if not window_rect.collidepoint(pos):
            return False
        
        # Click is within window - bring to front will be handled by game.py
        # But we still need to handle specific interactions
        
        if self.close_button_rect.collidepoint(pos) or self.minimize_button_rect.collidepoint(pos):
            return True
        
        if self.titlebar_rect.collidepoint(pos):
            self.dragging = True
            self.drag_offset = (pos[0] - self.position[0], pos[1] - self.position[1])
            return True
        
        # Handle content clicks, but still return True to bring window to front
        self._handle_content_click(pos)
        return True
    
    def _handle_content_click(self, pos):
        """Override in subclasses for content-specific clicks"""
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
    
    def render_titlebar(self, screen):
        """Render the titlebar"""
        screen.blit(self.titlebar_bg, (self.position[0], self.position[1]))
        font = pygame.font.Font(None, 20)
        title_text = font.render(self.title, True, (0, 0, 0))  # Black text for visibility
        text_y = self.position[1] + (self.titlebar_height - title_text.get_height()) // 2
        screen.blit(title_text, (self.position[0] + 10, text_y))
        screen.blit(self.close_icon, self.close_button_rect.topleft)
        screen.blit(self.minimize_icon, self.minimize_button_rect.topleft)
    
    def render(self, screen):
        """Render the window - override in subclasses"""
        screen.blit(self.background_surface, self.position)
        self.render_titlebar(screen)
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)


class FTLWindow(ThemedWindow):
    """FTL game screenshot window"""
    def __init__(self, position, width, height, assets_path, z_index=0):
        super().__init__("FTL: Faster Than Light", position, width, height, assets_path, z_index)
        # Load FTL screenshot
        ftl_path = os.path.join(assets_path, "menus", "ftl.png")
        self.ftl_image = pygame.image.load(ftl_path).convert()
        # Scale to fit window
        self.ftl_image = pygame.transform.scale(self.ftl_image, (width, height - self.titlebar_height))
    
    def render(self, screen):
        screen.blit(self.background_surface, self.position)
        self.render_titlebar(screen)
        # Draw FTL screenshot in content area
        screen.blit(self.ftl_image, (self.position[0], self.position[1] + self.titlebar_height))
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)


class ZomboidWindow(ThemedWindow):
    """Project Zomboid menu window with cycling screenshots"""
    def __init__(self, position, width, height, assets_path, z_index=0):
        super().__init__("Project Zomboid", position, width, height, assets_path, z_index)
        # Load all zomboid screenshots
        self.zomboid_images = []
        for i in range(1, 5):
            zomboid_path = os.path.join(assets_path, "menus", f"zomboid{i}.png")
            img = pygame.image.load(zomboid_path).convert()
            img = pygame.transform.scale(img, (width, height - self.titlebar_height))
            self.zomboid_images.append(img)
        self.current_image = 0
        self.cycle_timer = 0
        self.cycle_interval = 3000  # Change every 3 seconds
    
    def update(self, dt):
        """Update cycling (dt is in milliseconds)"""
        self.cycle_timer += dt
        if self.cycle_timer >= self.cycle_interval:
            self.cycle_timer = 0
            self.current_image = (self.current_image + 1) % len(self.zomboid_images)
    
    def render(self, screen):
        screen.blit(self.background_surface, self.position)
        self.render_titlebar(screen)
        # Draw current zomboid screenshot
        screen.blit(self.zomboid_images[self.current_image], 
                   (self.position[0], self.position[1] + self.titlebar_height))
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)


class InventoryWindow(ThemedWindow):
    """Game-style inventory menu"""
    def __init__(self, position, width, height, assets_path, z_index=0):
        super().__init__("Inventory", position, width, height, assets_path, z_index)
        # Inventory grid: 6 columns, 4 rows
        self.grid_cols = 6
        self.grid_rows = 4
        self.slot_size = 60
        self.slot_padding = 5
        self.grid_start_x = 20
        self.grid_start_y = 60
        
        # Load some menu cards as inventory items
        self.items = []
        ui_path = os.path.join(assets_path, "ui")
        card_files = [
            "menu_card_01_form_150x100.png",
            "menu_card_02_list_150x100.png",
            "menu_card_03_sheet_150x100.png",
        ]
        for i, card_file in enumerate(card_files[:3]):
            try:
                img = pygame.image.load(os.path.join(ui_path, card_file)).convert_alpha()
                img = pygame.transform.scale(img, (self.slot_size - 10, self.slot_size - 10))
                self.items.append({
                    'image': img,
                    'slot': (i % self.grid_cols, i // self.grid_cols)
                })
            except:
                pass
    
    def render(self, screen):
        screen.blit(self.background_surface, self.position)
        self.render_titlebar(screen)
        
        # Draw inventory grid
        content_y = self.position[1] + self.titlebar_height
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                slot_x = self.position[0] + self.grid_start_x + col * (self.slot_size + self.slot_padding)
                slot_y = content_y + self.grid_start_y + row * (self.slot_size + self.slot_padding)
                # Draw slot background
                pygame.draw.rect(screen, (220, 220, 220), 
                               pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size))
                pygame.draw.rect(screen, (180, 180, 180), 
                               pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size), 2)
        
        # Draw items
        for item in self.items:
            col, row = item['slot']
            slot_x = self.position[0] + self.grid_start_x + col * (self.slot_size + self.slot_padding) + 5
            slot_y = content_y + self.grid_start_y + row * (self.slot_size + self.slot_padding) + 5
            screen.blit(item['image'], (slot_x, slot_y))
        
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)


class OutlookWindow(ThemedWindow):
    """Microsoft Outlook email client"""
    def __init__(self, position, width, height, assets_path, z_index=0):
        super().__init__("Microsoft Outlook", position, width, height, assets_path, z_index)
        self.background_surface.fill((255, 255, 255))
        
        # Email list (will be populated with incoming emails)
        self.emails = []
        self.selected_email_index = None
        self.scroll_offset = 0
        self.max_visible_emails = 8
        self.viewing_email = None  # Currently viewing full email content (deprecated, using new window)
        self.blink_timer = 0  # For blinking urgent emails
        self.email_to_open = None  # Email to open in new window
        
        # Import email content
        from messages_content import (
            REGULAR_EMAIL_SENDERS, 
            REGULAR_EMAIL_SUBJECTS,
            CONGRATULATORY_EMAILS,
            REGULAR_EMAILS
        )
        
        self.email_senders = REGULAR_EMAIL_SENDERS
        self.email_subjects = REGULAR_EMAIL_SUBJECTS
        self.regular_emails = REGULAR_EMAILS
        self.congratulatory_emails = CONGRATULATORY_EMAILS
        self.congratulatory_sent = set()  # Track which congratulatory emails have been sent
        
        # Start with empty inbox (no initial emails)
    
    def _add_email(self, timestamp):
        """Add a new regular email to the inbox"""
        from datetime import datetime
        from messages_content import REGULAR_EMAILS
        
        # Pick a random email template from the loaded emails
        if REGULAR_EMAILS:
            email_template = random.choice(REGULAR_EMAILS)
        else:
            # Fallback if no emails loaded
            email_template = {
                "sender": random.choice(self.email_senders),
                "subject": random.choice(self.email_subjects),
                "message": "Email content not available.",
                "responses": ["OK", "Thanks", "Got it"]
            }
        
        # Format time
        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%I:%M %p")
        
        email = {
            "subject": email_template["subject"],
            "from": email_template["sender"],
            "time": time_str,
            "timestamp": timestamp,
            "read": False,
            "type": "regular",
            "message": email_template.get("message", ""),
            "responses": email_template.get("responses", [])
        }
        
        # Add to beginning (newest first)
        self.emails.insert(0, email)
        
        # Limit to 50 emails
        if len(self.emails) > 50:
            self.emails.pop()
    
    def _add_congratulatory_email(self, email_template, timestamp):
        """Add a congratulatory email about Calvelli's work"""
        from datetime import datetime
        
        # Format time
        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%I:%M %p")
        
        email = {
            "subject": email_template["subject"],
            "from": email_template["sender"],
            "time": time_str,
            "timestamp": timestamp,
            "read": False,
            "type": "congratulatory",
            "message": email_template["message"],
            "responses": email_template["responses"],
            "urgent": True,
            "blinking": True  # Start blinking
        }
        
        # Add to beginning (newest first)
        self.emails.insert(0, email)
        
        # Limit to 50 emails
        if len(self.emails) > 50:
            self.emails.pop()
    
    def _handle_content_click(self, pos):
        """Handle clicks on email list and email view"""
        content_y = self.position[1] + self.titlebar_height
        sidebar_width = 150
        
        # If viewing an email, check for back button or response clicks
        if self.viewing_email:
            email_area_x = self.position[0] + sidebar_width + 10
            email_area_y = content_y + 10
            
            # Back button
            if (email_area_x + 10 <= pos[0] <= email_area_x + 150 and
                email_area_y + 10 <= pos[1] <= email_area_y + 30):
                self.viewing_email = None
                return True
            
            # Response buttons
            if 'responses' in self.viewing_email:
                response_start_y = email_area_y + 200  # Approximate
                for i, response in enumerate(self.viewing_email['responses']):
                    response_rect = pygame.Rect(email_area_x + 10, response_start_y + i * 35, 
                                               self.width - sidebar_width - 20, 30)
                    if response_rect.collidepoint(pos):
                        # Response clicked (could add functionality here)
                        self.viewing_email = None  # Close email view after responding
                        return True
            
            return False
        
        # Otherwise, handle email list clicks
        list_x = self.position[0] + sidebar_width + 10
        list_y = content_y + 10
        
        # Check if click is in email list area
        if list_x <= pos[0] <= self.position[0] + self.width - 10:
            if list_y <= pos[1] <= content_y + self.height - self.titlebar_height:
                # Calculate which email was clicked
                email_index = int((pos[1] - list_y) / 60) + self.scroll_offset
                if 0 <= email_index < len(self.emails):
                    self.selected_email_index = email_index
                    self.emails[email_index]['read'] = True
                    # Stop blinking if urgent
                    if self.emails[email_index].get('urgent') and self.emails[email_index].get('blinking'):
                        self.emails[email_index]['blinking'] = False
                    # Signal to open email in new window
                    self.email_to_open = self.emails[email_index]
                    return True
        return False
    
    def update(self, dt):
        """Update window (for blinking animation)"""
        self.blink_timer += dt
    
    def render(self, screen):
        screen.blit(self.background_surface, self.position)
        self.render_titlebar(screen)
        
        content_y = self.position[1] + self.titlebar_height
        
        # Draw folder sidebar
        sidebar_width = 150
        pygame.draw.rect(screen, (240, 240, 240), 
                        pygame.Rect(self.position[0], content_y, sidebar_width, self.height - self.titlebar_height))
        pygame.draw.line(screen, (200, 200, 200), 
                        (self.position[0] + sidebar_width, content_y),
                        (self.position[0] + sidebar_width, content_y + self.height - self.titlebar_height), 2)
        
        # Draw folder list
        font = pygame.font.Font(None, 18)
        folders = ["Inbox", "Sent", "Drafts", "Trash"]
        for i, folder in enumerate(folders):
            text = font.render(folder, True, (0, 0, 0))
            screen.blit(text, (self.position[0] + 10, content_y + 20 + i * 30))
        
        # Draw inbox count
        unread_count = sum(1 for email in self.emails if not email.get('read', False))
        if unread_count > 0:
            count_text = font.render(f"({unread_count})", True, (0, 120, 212))
            screen.blit(count_text, (self.position[0] + 80, content_y + 20))
        
        # Note: Email viewing is now done in separate windows, so we don't render inline view
        
        # Draw email list
        list_x = self.position[0] + sidebar_width + 10
        list_y = content_y + 10
        font_small = pygame.font.Font(None, 14)
        font_subject = pygame.font.Font(None, 16)
        
        # Show visible emails based on scroll
        visible_emails = self.emails[self.scroll_offset:self.scroll_offset + self.max_visible_emails]
        
        for i, email in enumerate(visible_emails):
            email_y = list_y + i * 60
            email_index = self.scroll_offset + i
            
            # Highlight selected email
            if email_index == self.selected_email_index:
                pygame.draw.rect(screen, (220, 235, 255), 
                               pygame.Rect(list_x, email_y, self.width - sidebar_width - 20, 55))
            elif i % 2 == 0:
                pygame.draw.rect(screen, (250, 250, 250), 
                               pygame.Rect(list_x, email_y, self.width - sidebar_width - 20, 55))
            
            # Reply indicator (small arrow icon in top left)
            if email.get('replied', False):
                # Draw a small reply arrow symbol
                reply_icon_size = 12
                reply_icon_x = list_x + 5
                reply_icon_y = email_y + 5
                # Simple arrow shape pointing right
                pygame.draw.polygon(screen, (100, 150, 100), [
                    (reply_icon_x, reply_icon_y),
                    (reply_icon_x + reply_icon_size, reply_icon_y + reply_icon_size // 2),
                    (reply_icon_x, reply_icon_y + reply_icon_size)
                ])
            
            # Unread indicator (blue dot) - offset if reply icon is present
            unread_dot_x = list_x + 8 if not email.get('replied', False) else list_x + 20
            if not email.get('read', False):
                pygame.draw.circle(screen, (0, 120, 212), (unread_dot_x, email_y + 27), 4)
            
            # URGENT indicator (orange, blinking)
            if email.get('urgent', False):
                # Blinking animation
                blink_on = int(self.blink_timer / 500) % 2 == 0  # Blink every 500ms
                if email.get('blinking', False) and blink_on:
                    # Draw orange highlight
                    urgent_rect = pygame.Rect(list_x, email_y, self.width - sidebar_width - 20, 55)
                    urgent_surface = pygame.Surface((urgent_rect.width, urgent_rect.height))
                    urgent_surface.set_alpha(100)
                    urgent_surface.fill((255, 165, 0))  # Orange
                    screen.blit(urgent_surface, urgent_rect.topleft)
                    
                    # Draw URGENT label
                    urgent_font = pygame.font.Font(None, 12)
                    urgent_text = urgent_font.render("URGENT", True, (255, 100, 0))
                    screen.blit(urgent_text, (list_x + self.width - sidebar_width - 60, email_y + 35))
            
            # Subject - offset if reply icon is present
            subject_x = list_x + 15 if not email.get('replied', False) else list_x + 25
            subject_color = (0, 0, 0) if email.get('read', False) else (0, 0, 0)
            subject_text = font_subject.render(email['subject'], True, subject_color)
            screen.blit(subject_text, (subject_x, email_y + 5))
            
            # From
            from_text = font_small.render(email['from'], True, (100, 100, 100))
            screen.blit(from_text, (list_x + 15, email_y + 25))
            
            # Time
            time_text = font_small.render(email['time'], True, (150, 150, 150))
            screen.blit(time_text, (list_x + self.width - sidebar_width - 80, email_y + 5))
        
        # Scroll indicators
        if self.scroll_offset > 0:
            # Up arrow
            pygame.draw.polygon(screen, (150, 150, 150), 
                              [(list_x + self.width - sidebar_width - 30, list_y),
                               (list_x + self.width - sidebar_width - 20, list_y - 5),
                               (list_x + self.width - sidebar_width - 10, list_y)])
        
        if self.scroll_offset + self.max_visible_emails < len(self.emails):
            # Down arrow
            bottom_y = list_y + self.max_visible_emails * 60
            pygame.draw.polygon(screen, (150, 150, 150), 
                              [(list_x + self.width - sidebar_width - 30, bottom_y),
                               (list_x + self.width - sidebar_width - 20, bottom_y + 5),
                               (list_x + self.width - sidebar_width - 10, bottom_y)])
        
        
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)
    
    def _render_email_view(self, screen, content_y, sidebar_width):
        """Render the full email view with message and response options"""
        # Draw email content area
        email_area_x = self.position[0] + sidebar_width + 10
        email_area_y = content_y + 10
        email_area_width = self.width - sidebar_width - 20
        
        # Background for email view
        pygame.draw.rect(screen, (255, 255, 255), 
                        pygame.Rect(email_area_x, email_area_y, email_area_width, 
                                   self.height - self.titlebar_height - 20))
        
        # Back button
        back_font = pygame.font.Font(None, 16)
        back_text = back_font.render("← Back to Inbox", True, (0, 120, 212))
        screen.blit(back_text, (email_area_x + 10, email_area_y + 10))
        
        # Email header
        header_y = email_area_y + 40
        font_subject = pygame.font.Font(None, 20)
        font_sender = pygame.font.Font(None, 16)
        
        subject_text = font_subject.render(self.viewing_email['subject'], True, (0, 0, 0))
        screen.blit(subject_text, (email_area_x + 10, header_y))
        
        from_text = font_sender.render(f"From: {self.viewing_email['from']}", True, (100, 100, 100))
        screen.blit(from_text, (email_area_x + 10, header_y + 25))
        
        time_text = font_sender.render(f"Time: {self.viewing_email['time']}", True, (100, 100, 100))
        screen.blit(time_text, (email_area_x + 10, header_y + 45))
        
        # Divider
        pygame.draw.line(screen, (200, 200, 200), 
                        (email_area_x + 10, header_y + 70),
                        (email_area_x + email_area_width - 10, header_y + 70), 1)
        
        # Email message
        message_y = header_y + 85
        font_message = pygame.font.Font(None, 16)
        # Wrap message text
        message = self.viewing_email['message']
        words = message.split(' ')
        lines = []
        current_line = ""
        max_width = email_area_width - 40
        
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
        
        for i, line in enumerate(lines[:15]):  # Max 15 lines
            line_text = font_message.render(line, True, (0, 0, 0))
            screen.blit(line_text, (email_area_x + 20, message_y + i * 20))
        
        # Response options
        if 'responses' in self.viewing_email:
            response_y = message_y + len(lines) * 20 + 30
            response_label = font_subject.render("Quick Reply:", True, (0, 0, 0))
            screen.blit(response_label, (email_area_x + 10, response_y))
            
            response_y += 30
            for i, response in enumerate(self.viewing_email['responses']):
                response_rect = pygame.Rect(email_area_x + 10, response_y + i * 35, 
                                           email_area_width - 20, 30)
                # Hover effect could be added here
                pygame.draw.rect(screen, (240, 240, 240), response_rect)
                pygame.draw.rect(screen, (200, 200, 200), response_rect, 1)
                
                response_text = font_message.render(response, True, (0, 0, 0))
                text_rect = response_text.get_rect(center=response_rect.center)
                screen.blit(response_text, text_rect)


class MessagesWindow(ThemedWindow):
    """Mac Messages app interface"""
    def __init__(self, position, width, height, assets_path, z_index=0):
        super().__init__("Messages", position, width, height, assets_path, z_index)
        self.background_surface.fill((255, 255, 255))
        
        # Contacts and their messages
        self.conversations = {
            "seong-ah": ["Hey Matt!", "How's the conference planning going?"],
            "jar": ["Matt, we need to talk", "About the budget"],
            "halle": ["Hi!", "Can you check the schedule?"],
            "mama velli": ["Sweetie", "How are you doing?"],
            "fleece": ["Yo", "Conference stuff ready?"]
        }
        self.selected_contact = "seong-ah"
        self.sidebar_width = 200
    
    def _handle_content_click(self, pos):
        """Handle clicks on contact list"""
        content_y = self.position[1] + self.titlebar_height
        # Check if click is in sidebar
        if self.position[0] <= pos[0] <= self.position[0] + self.sidebar_width:
            contacts = list(self.conversations.keys())
            for i, contact in enumerate(contacts):
                contact_y = content_y + 10 + i * 50
                if content_y + 10 + i * 50 <= pos[1] <= content_y + 10 + (i + 1) * 50:
                    self.selected_contact = contact
                    return True
        return False
    
    def render(self, screen):
        screen.blit(self.background_surface, self.position)
        self.render_titlebar(screen)
        
        content_y = self.position[1] + self.titlebar_height
        
        # Draw contact list sidebar
        sidebar_width = 200
        pygame.draw.rect(screen, (245, 245, 245), 
                        pygame.Rect(self.position[0], content_y, sidebar_width, self.height - self.titlebar_height))
        pygame.draw.line(screen, (220, 220, 220), 
                        (self.position[0] + sidebar_width, content_y),
                        (self.position[0] + sidebar_width, content_y + self.height - self.titlebar_height), 2)
        
        # Draw contact list
        font = pygame.font.Font(None, 20)
        contacts = list(self.conversations.keys())
        for i, contact in enumerate(contacts):
            contact_y = content_y + 10 + i * 50
            # Highlight selected
            if contact == self.selected_contact:
                pygame.draw.rect(screen, (200, 220, 255), 
                               pygame.Rect(self.position[0] + 5, contact_y, sidebar_width - 10, 45))
            
            # Contact name
            name_text = font.render(contact, True, (0, 0, 0))
            screen.blit(name_text, (self.position[0] + 15, contact_y + 10))
            
            # Preview
            preview_font = pygame.font.Font(None, 14)
            preview = self.conversations[contact][-1][:30] + "..."
            preview_text = preview_font.render(preview, True, (120, 120, 120))
            screen.blit(preview_text, (self.position[0] + 15, contact_y + 30))
        
        # Draw message area
        msg_x = self.position[0] + sidebar_width + 10
        msg_y = content_y + 10
        
        # Draw messages
        font_msg = pygame.font.Font(None, 18)
        messages = self.conversations[self.selected_contact]
        for i, msg in enumerate(messages):
            msg_y_pos = msg_y + i * 50
            # Message bubble (alternate sides)
            if i % 2 == 0:
                # Received (gray, left)
                bubble_rect = pygame.Rect(msg_x, msg_y_pos, 300, 40)
                pygame.draw.rect(screen, (230, 230, 230), bubble_rect)
                pygame.draw.rect(screen, (200, 200, 200), bubble_rect, 1)
            else:
                # Sent (blue, right)
                bubble_rect = pygame.Rect(self.width - 320, msg_y_pos, 300, 40)
                pygame.draw.rect(screen, (0, 120, 255), bubble_rect)
            
            msg_text = font_msg.render(msg, True, (0, 0, 0) if i % 2 == 0 else (255, 255, 255))
            text_rect = msg_text.get_rect(center=bubble_rect.center)
            screen.blit(msg_text, text_rect)
        
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)


class SlackWindow(ThemedWindow):
    """Slack workspace interface"""
    def __init__(self, position, width, height, assets_path, z_index=0):
        super().__init__("Slack", position, width, height, assets_path, z_index)
        self.background_surface.fill((255, 255, 255))
        
        self.channels = ["# general", "# conference-planning", "# fundraising", "# random"]
        self.messages = [
            {"channel": "# general", "user": "calvelli", "text": "Hey team, status update?"},
            {"channel": "# conference-planning", "user": "matt", "text": "Working on it..."},
            {"channel": "# fundraising", "user": "calvelli", "text": "Need those numbers"},
        ]
        self.selected_channel = "# general"
    
    def render(self, screen):
        screen.blit(self.background_surface, self.position)
        self.render_titlebar(screen)
        
        content_y = self.position[1] + self.titlebar_height
        
        # Draw channel sidebar
        sidebar_width = 180
        pygame.draw.rect(screen, (60, 60, 60), 
                        pygame.Rect(self.position[0], content_y, sidebar_width, self.height - self.titlebar_height))
        
        # Draw channels
        font = pygame.font.Font(None, 18)
        for i, channel in enumerate(self.channels):
            channel_y = content_y + 20 + i * 35
            if channel == self.selected_channel:
                pygame.draw.rect(screen, (80, 80, 80), 
                               pygame.Rect(self.position[0] + 5, channel_y, sidebar_width - 10, 30))
            
            channel_text = font.render(channel, True, (200, 200, 200))
            screen.blit(channel_text, (self.position[0] + 15, channel_y + 5))
        
        # Draw message area
        msg_x = self.position[0] + sidebar_width + 10
        msg_y = content_y + 10
        
        # Draw messages for selected channel
        font_small = pygame.font.Font(None, 14)
        font_msg = pygame.font.Font(None, 16)
        channel_messages = [m for m in self.messages if m['channel'] == self.selected_channel]
        
        for i, msg in enumerate(channel_messages):
            msg_y_pos = msg_y + i * 50
            # User name
            user_text = font_small.render(msg['user'], True, (100, 100, 200))
            screen.blit(user_text, (msg_x, msg_y_pos))
            
            # Message text
            text_text = font_msg.render(msg['text'], True, (0, 0, 0))
            screen.blit(text_text, (msg_x, msg_y_pos + 20))
        
        # Draw user list sidebar (right)
        user_sidebar_width = 150
        user_sidebar_x = self.width - user_sidebar_width
        pygame.draw.rect(screen, (240, 240, 240), 
                        pygame.Rect(self.position[0] + user_sidebar_x, content_y, 
                                  user_sidebar_width, self.height - self.titlebar_height))
        
        users = ["calvelli", "matt", "seong-ah"]
        for i, user in enumerate(users):
            user_text = font_small.render(user, True, (0, 0, 0))
            screen.blit(user_text, (self.position[0] + user_sidebar_x + 10, content_y + 20 + i * 30))
        
        pygame.draw.rect(screen, (180, 180, 180), 
                        pygame.Rect(self.position[0], self.position[1], self.width, self.height), 2)
