"""
Email Notification System
Shows email notifications in the top right that stack and slide up
"""

import pygame
import random
import time

class EmailNotification:
    """A single email notification"""
    
    def __init__(self, sender, subject, timestamp, is_congratulatory=False, email_data=None):
        self.sender = sender
        self.subject = subject
        self.timestamp = timestamp
        self.created_time = time.time()
        self.duration = 8.0  # Show for 8 seconds (longer for congratulatory)
        self.is_dismissing = False
        self.dismiss_start_time = 0
        self.dismiss_duration = 0.3  # Slide out animation duration
        self.y_offset = 0  # For sliding animation
        self.is_congratulatory = is_congratulatory
        self.email_data = email_data  # Store email data for opening in Outlook
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
            # Slide up (negative offset)
            self.y_offset = -progress * 100  # Slide up 100 pixels
    
    def should_remove(self):
        """Check if notification should be removed"""
        if self.is_dismissing:
            dismiss_elapsed = time.time() - self.dismiss_start_time
            return dismiss_elapsed >= self.dismiss_duration
        return False
    
    def render(self, screen, x, y, width):
        """Render the notification"""
        # Calculate actual y position with offset
        actual_y = y + int(self.y_offset)
        
        # Don't render if completely off screen
        if actual_y < -100:
            return
        
        # Notification dimensions
        height = 80
        padding = 12
        
        # Create notification surface
        notification = pygame.Surface((width, height))
        notification.set_alpha(240)
        
        # Different color for congratulatory emails
        if self.is_congratulatory:
            notification.fill((255, 240, 200))  # Light orange tint
        else:
            notification.fill((255, 255, 255))
        
        # Draw border (orange for congratulatory)
        border_color = (255, 165, 0) if self.is_congratulatory else (200, 200, 200)
        pygame.draw.rect(notification, border_color, 
                        pygame.Rect(0, 0, width, height), 2)
        
        # Draw email icon (simple envelope)
        icon_size = 24
        icon_x = padding
        icon_y = (height - icon_size) // 2
        icon_color = (255, 165, 0) if self.is_congratulatory else (0, 120, 212)
        pygame.draw.rect(notification, icon_color, 
                        pygame.Rect(icon_x, icon_y, icon_size, icon_size), 2)
        
        # Draw sender and subject
        font_sender = pygame.font.Font(None, 18)
        font_subject = pygame.font.Font(None, 16)
        
        text_x = icon_x + icon_size + padding
        
        # Sender (bold-ish)
        sender_text = font_sender.render(self.sender, True, (0, 0, 0))
        notification.blit(sender_text, (text_x, padding))
        
        # Subject (truncate if too long)
        max_subject_width = width - text_x - padding
        subject_display = self.subject
        if font_subject.size(subject_display)[0] > max_subject_width:
            while font_subject.size(subject_display + "...")[0] > max_subject_width and len(subject_display) > 0:
                subject_display = subject_display[:-1]
            subject_display += "..."
        
        subject_text = font_subject.render(subject_display, True, (100, 100, 100))
        notification.blit(subject_text, (text_x, padding + 22))
        
        # Draw to screen
        screen.blit(notification, (x, actual_y))
        
        # Store rect for click detection
        self.rect = pygame.Rect(x, actual_y, width, height)
    
    def contains_point(self, pos):
        """Check if point is within notification"""
        if self.rect:
            return self.rect.collidepoint(pos)
        return False


class EmailNotificationSystem:
    """Manages email notifications"""
    
    def __init__(self):
        self.notifications = []
        self.last_notification_time = time.time()
        self.notification_interval = random.uniform(8.0, 15.0)  # 8-15 seconds
        
        # Email templates
        self.senders = [
            "conference@org.com",
            "sponsors@conference.org",
            "finance@conference.org",
            "venue@conference.org",
            "media@conference.org",
            "volunteers@conference.org",
        ]
        
        self.subjects = [
            "Budget Review Needed",
            "Sponsor Confirmation",
            "Venue Update",
            "Media Partnership Opportunity",
            "Volunteer Schedule",
            "Registration Update",
            "Catering Menu Finalized",
            "AV Equipment Confirmed",
            "Parking Arrangements",
            "Schedule Changes",
        ]
        
        self.notification_width = 350
        self.notification_spacing = 10
        self.start_x = 1920 - self.notification_width - 20  # Top right
        self.start_y = 70  # Below progress bar area
        self.pending_congratulatory_email = None  # Email to send when triggered
    
    def update(self):
        """Update notification system"""
        current_time = time.time()
        
        # Check if it's time for a new notification
        time_since_last = current_time - self.last_notification_time
        if time_since_last >= self.notification_interval:
            self._add_notification()
            self.last_notification_time = current_time
            self.notification_interval = random.uniform(8.0, 15.0)
        
        # Update all notifications
        for notification in self.notifications:
            notification.update(current_time)
        
        # Remove dismissed notifications
        self.notifications = [n for n in self.notifications if not n.should_remove()]
    
    def _add_notification(self):
        """Add a new email notification"""
        sender = random.choice(self.senders)
        subject = random.choice(self.subjects)
        timestamp = time.time()
        notification = EmailNotification(sender, subject, timestamp)
        self.notifications.append(notification)
    
    def add_congratulatory_notification(self, email_template):
        """Add a congratulatory email notification"""
        timestamp = time.time()
        notification = EmailNotification(
            email_template["sender"],
            email_template["subject"],
            timestamp,
            is_congratulatory=True,
            email_data=email_template
        )
        self.notifications.append(notification)
        return notification
    
    def handle_click(self, pos):
        """Handle click on notifications, returns email data if congratulatory email was clicked"""
        for notification in self.notifications:
            if notification.contains_point(pos) and notification.is_congratulatory:
                return notification.email_data
        return None
    
    def render(self, screen):
        """Render all notifications stacked"""
        # Calculate y positions for stacking
        # When a notification is dismissing, others slide up
        current_y = self.start_y
        
        for i, notification in enumerate(self.notifications):
            # Calculate base position
            base_y = current_y
            
            # If this notification is dismissing, it slides up
            # Other notifications below it also need to account for the slide
            render_y = base_y + int(notification.y_offset)
            
            notification.render(screen, self.start_x, render_y, self.notification_width)
            
            # Next notification position (account for dismissing notification's space)
            if notification.is_dismissing:
                # Dismissing notifications take less space as they slide up
                slide_progress = abs(notification.y_offset) / 100.0
                spacing = int((90 + self.notification_spacing) * (1.0 - slide_progress))
            else:
                spacing = 90 + self.notification_spacing
            
            current_y += spacing
