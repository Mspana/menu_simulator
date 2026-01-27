"""
Messages Notification System
Shows Messages (iMessage) notifications in the top right that stack and slide up
"""

import pygame
import random
import time

class MessagesNotification:
    """A single Messages notification"""
    
    def __init__(self, contact, message, timestamp):
        self.contact = contact
        self.message = message
        self.timestamp = timestamp
        self.created_time = time.time()
        self.duration = 5.0  # Show for 5 seconds
        self.is_dismissing = False
        self.dismiss_start_time = 0
        self.dismiss_duration = 0.3  # Slide out animation duration
        self.x_offset = 0  # For sliding animation (slides right)
        self.message_data = {"contact": contact, "message": message}
        self.rect = None  # Will be set during render for click detection
        
    def update(self, current_time):
        """Update notification state"""
        elapsed = current_time - self.created_time
        
        # Check if it's time to dismiss
        if not self.is_dismissing and elapsed >= self.duration:
            self.is_dismissing = True
            self.dismiss_start_time = current_time
        
        # Update slide animation
        if self.is_dismissing:
            dismiss_elapsed = current_time - self.dismiss_start_time
            progress = min(dismiss_elapsed / self.dismiss_duration, 1.0)
            # Slide right (positive offset)
            self.x_offset = progress * 400  # Slide right 400 pixels
    
    def should_remove(self):
        """Check if notification should be removed"""
        if self.is_dismissing:
            dismiss_elapsed = time.time() - self.dismiss_start_time
            return dismiss_elapsed >= self.dismiss_duration
        return False
    
    def render(self, screen, x, y, width):
        """Render the notification"""
        # Calculate actual x position with offset
        actual_x = x + int(self.x_offset)
        
        # Don't render if completely off screen
        if actual_x > 1920:
            return
        
        # Notification dimensions
        height = 70
        padding = 12
        
        # Create notification surface
        notification = pygame.Surface((width, height))
        notification.set_alpha(240)
        notification.fill((255, 255, 255))
        
        # Draw border (Messages blue)
        pygame.draw.rect(notification, (0, 120, 255), 
                        pygame.Rect(0, 0, width, height), 2)
        
        # Draw Messages icon (simple blue circle)
        icon_size = 20
        icon_x = padding
        icon_y = (height - icon_size) // 2
        pygame.draw.circle(notification, (0, 120, 255), 
                          (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2)
        
        # Draw contact and message
        font_title = pygame.font.Font(None, 20)
        font_message = pygame.font.Font(None, 16)
        
        text_x = icon_x + icon_size + padding
        
        # Contact name
        contact_text = font_title.render(self.contact, True, (0, 0, 0))
        notification.blit(contact_text, (text_x, padding))
        
        # Message preview (truncate if too long)
        max_message_width = width - text_x - padding
        message_display = self.message
        if font_message.size(message_display)[0] > max_message_width:
            while font_message.size(message_display + "...")[0] > max_message_width and len(message_display) > 0:
                message_display = message_display[:-1]
            message_display += "..."
        
        message_text = font_message.render(message_display, True, (100, 100, 100))
        notification.blit(message_text, (text_x, padding + 22))
        
        # Draw to screen
        screen.blit(notification, (actual_x, y))
        
        # Store rect for click detection
        self.rect = pygame.Rect(actual_x, y, width, height)
    
    def contains_point(self, pos):
        """Check if point is within notification"""
        if self.rect:
            return self.rect.collidepoint(pos)
        return False


class MessagesNotificationSystem:
    """Manages Messages notifications"""
    
    def __init__(self):
        self.notifications = []
        self.last_notification_time = time.time()
        self.notification_interval = random.uniform(10.0, 20.0)  # 10-20 seconds
        
        # Messages templates
        self.contacts = ["seong-ah", "jar", "halle", "mama velli", "fleece"]
        self.message_templates = [
            "Hey Matt!",
            "How's the conference planning going?",
            "Can you check this?",
            "We need to talk",
            "Hey, are you there?",
            "Can you look at the schedule?",
            "Hey, did you see my message?",
            "We need your input",
            "Hey Matt, status update?",
            "Can you review this?"
        ]
        
        self.notification_width = 350
        self.notification_spacing = 10
        self.start_x = 1920 - self.notification_width - 20  # Top right
        self.start_y = 70  # Below progress bar area
    
    def update(self):
        """Update notification system (notifications only added manually when Calvelli does something)"""
        current_time = time.time()
        
        # Update all notifications
        for notification in self.notifications:
            notification.update(current_time)
        
        # Remove dismissed notifications
        self.notifications = [n for n in self.notifications if not n.should_remove()]
    
    def _add_notification(self):
        """Add a new Messages notification"""
        contact = random.choice(self.contacts)
        message = random.choice(self.message_templates)
        timestamp = time.time()
        notification = MessagesNotification(contact, message, timestamp)
        self.notifications.append(notification)
        return notification
    
    def add_notification(self, contact, message):
        """Manually add a notification"""
        timestamp = time.time()
        notification = MessagesNotification(contact, message, timestamp)
        self.notifications.append(notification)
        return notification
    
    def handle_click(self, pos):
        """Handle click on notifications, returns message data if clicked"""
        for notification in self.notifications:
            if notification.contains_point(pos):
                # Dismiss notification when clicked
                notification.is_dismissing = True
                notification.dismiss_start_time = time.time()
                return notification.message_data
        return None
    
    def render(self, screen):
        """Render all notifications stacked"""
        # Calculate y positions for stacking
        current_y = self.start_y
        
        for i, notification in enumerate(self.notifications):
            # Calculate base position
            base_y = current_y
            
            # If this notification is dismissing, it slides right
            notification.render(screen, self.start_x, base_y, self.notification_width)
            
            # Next notification position (vertical stacking unaffected by horizontal slide)
            spacing = 80 + self.notification_spacing
            current_y += spacing
