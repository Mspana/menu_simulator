"""
Menu Simulator Game
Main entry point and game loop
"""

import pygame
import sys
import os
from themed_windows import (FTLWindow, ZomboidWindow, InventoryWindow, 
                           OutlookWindow, MessagesWindow, SlackWindow, DiscordWindow)
from email_view_window import EmailViewWindow
from reply_window import ReplyWindow
from milestone_notifications import MilestoneNotificationSystem
from progress_popup import ProgressPopupSystem
from discord_interrupt import DiscordInterrupt
from game_state import GameState
from ending import EndingScreen
from calvelli_log import CalvelliLog
from activity_log_window import ActivityLogWindow
from email_notifications import EmailNotificationSystem
from outlook_email_system import OutlookEmailSystem
from slack_notifications import SlackNotificationSystem
from messages_notifications import MessagesNotificationSystem
from discord_notifications import DiscordNotificationSystem
from game_notifications import GameNotificationSystem
from phone_call import PhoneCallSystem

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 212)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Menu Simulator - Fundraising for Conference")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load assets
        self.assets_path = os.path.join(os.path.dirname(__file__), "assets_pack")
        self.background = pygame.image.load(
            os.path.join(self.assets_path, "backgrounds", "desktop_workspace_background_1920x1080.png")
        ).convert()
        
        # Game state
        self.game_state = GameState()
        self.discord_interrupt = DiscordInterrupt(self.assets_path)
        self.calvelli_log = CalvelliLog()
        self.email_notifications = EmailNotificationSystem()
        self.slack_notifications = SlackNotificationSystem()
        self.messages_notifications = MessagesNotificationSystem()
        self.discord_notifications = DiscordNotificationSystem()
        self.game_notifications = GameNotificationSystem()
        self.milestone_notifications = MilestoneNotificationSystem(SCREEN_WIDTH)
        self.progress_popup_system = ProgressPopupSystem()
        self.phone_call_system = PhoneCallSystem()
        
        # Menus list (will include dynamically created email windows)
        self.menus = []
        
        # Create activity log window (tall, narrow window on the left)
        log_window_width = 350
        log_window_height = SCREEN_HEIGHT - 100
        log_window_x = 20
        log_window_y = 50
        self.activity_log_window = ActivityLogWindow(
            position=(log_window_x, log_window_y),
            width=log_window_width,
            height=log_window_height,
            assets_path=self.assets_path,
            z_index=100  # Always on top
        )
        
        # Create menu windows
        self.menus = self._create_menus()
        
        # Track email view windows separately for cleanup
        self.email_view_windows = []
        
        # Set up Outlook email system
        outlook_window = next((m for m in self.menus if isinstance(m, OutlookWindow)), None)
        if outlook_window:
            self.outlook_email_system = OutlookEmailSystem(outlook_window)
        else:
            self.outlook_email_system = None
        
        # Ending screen
        self.ending_screen = None
        self.game_complete = False
        
        # Load sounds
        self.sounds = self._load_sounds()
        
    def _load_sounds(self):
        """Load sound effects"""
        sounds = {}
        audio_path = os.path.join(self.assets_path, "audio_optional")
        try:
            sounds['click'] = pygame.mixer.Sound(
                os.path.join(audio_path, "ui_click.wav")
            )
            sounds['discord'] = pygame.mixer.Sound(
                os.path.join(audio_path, "discord_notification_ping.wav")
            )
            sounds['celebration'] = pygame.mixer.Sound(
                os.path.join(audio_path, "celebration_stinger.wav")
            )
        except:
            # If sounds fail to load, continue without them
            pass
        return sounds
    
    def _create_menus(self):
        """Create the themed application windows"""
        menus = []
        
        # Window positions (staggered)
        positions = [
            (100, 100),
            (300, 150),
            (500, 200),
            (200, 300),
            (400, 250),
            (600, 180)
        ]
        
        # Create themed windows
        window_configs = [
            ("Inventory", InventoryWindow),
            ("FTL", FTLWindow),
            ("Zomboid", ZomboidWindow),
            ("Outlook", OutlookWindow),
            ("Messages", MessagesWindow),
            ("Slack", SlackWindow),
            ("Discord", DiscordWindow),
        ]
        
        for i, ((name, window_class), pos) in enumerate(zip(window_configs, positions)):
            menu = window_class(
                position=pos,
                width=800,
                height=600,
                assets_path=self.assets_path,
                z_index=i
            )
            menus.append(menu)
        
        # Bring Outlook to front (highest z-index)
        outlook_window = next((m for m in menus if isinstance(m, OutlookWindow)), None)
        if outlook_window:
            max_z = max(m.z_index for m in menus)
            outlook_window.z_index = max_z + 1
        
        return menus
    
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_TAB:
                    # Cycle through windows (Alt+Tab style)
                    self._cycle_windows()
                else:
                    # Check if any reply window is open and handle typing
                    reply_windows = [w for w in self.menus if isinstance(w, ReplyWindow)]
                    for reply_window in reply_windows:
                        if reply_window.handle_keypress(event.key):
                            break  # Only handle one window at a time
                    
                    # Check if Messages, Slack, or Discord window is replying
                    messages_window = next((m for m in self.menus if isinstance(m, MessagesWindow)), None)
                    if messages_window and messages_window.handle_keypress(event.key):
                        continue
                    
                    slack_window = next((m for m in self.menus if isinstance(m, SlackWindow)), None)
                    if slack_window and slack_window.handle_keypress(event.key):
                        continue
                    
                    discord_window = next((m for m in self.menus if isinstance(m, DiscordWindow)), None)
                    if discord_window and discord_window.handle_keypress(event.key):
                        continue
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_click(event.pos)
                    if 'click' in self.sounds:
                        self.sounds['click'].play()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self._handle_release(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left mouse button held
                    self._handle_drag(event.pos)
        
        # Check for Discord interruptions
        if not self.game_complete:
            self.discord_interrupt.update(self.menus, self.sounds)
    
    def _cycle_windows(self):
        """Cycle through windows (bring next to front)"""
        if not self.menus:
            return
        
        # Find currently top window
        top_idx = max(range(len(self.menus)), key=lambda i: self.menus[i].z_index)
        
        # Bring next window to front
        next_idx = (top_idx + 1) % len(self.menus)
        max_z = max(m.z_index for m in self.menus)
        self.menus[next_idx].z_index = max_z + 1
    
    def _handle_click(self, pos):
        """Handle mouse click"""
        # Check phone call popup first (blocks everything)
        if self.phone_call_system.active_call and self.phone_call_system.active_call.active:
            if self.phone_call_system.handle_click(pos):
                return
        
        # Check Discord popup
        if self.discord_interrupt.is_active():
            if self.discord_interrupt.handle_click(pos, self.menus):
                return
        
        # Check game notifications (FTL/Zomboid circles) - check early so clicks work even if window is behind
        if self.game_notifications.handle_click(pos):
            return
        
        # Check email notifications (for opening Outlook and highlighting email)
        clicked_email_data = self.email_notifications.handle_click(pos)
        if clicked_email_data is not None:  # None means regular notification was dismissed
            if clicked_email_data:  # Non-empty dict means congratulatory email was clicked
                # Find the email in Outlook and highlight it (bring Outlook to front)
                outlook_window = next((m for m in self.menus if isinstance(m, OutlookWindow)), None)
                if outlook_window:
                    # Bring Outlook to front
                    max_z = max([m.z_index for m in self.menus] + [self.activity_log_window.z_index], default=0)
                    outlook_window.z_index = max_z + 1
                    
                    # Find and highlight the email
                    for i, email in enumerate(outlook_window.emails):
                        if (email.get('type') == 'congratulatory' and 
                            email.get('subject') == clicked_email_data['subject']):
                            outlook_window.emails[i]['read'] = True
                            outlook_window.emails[i]['blinking'] = False  # Stop blinking
                            # Set highlighted email (temporary highlight)
                            outlook_window.highlighted_email_index = i
                            outlook_window.highlight_timer = 0  # Reset timer
                            break
            return
        
        # Check Slack notifications
        clicked_slack_data = self.slack_notifications.handle_click(pos)
        if clicked_slack_data:
            # Bring Slack window to front and highlight the message
            slack_window = next((m for m in self.menus if isinstance(m, SlackWindow)), None)
            if slack_window:
                # Bring to front
                max_z = max([m.z_index for m in self.menus] + [self.activity_log_window.z_index], default=0)
                slack_window.z_index = max_z + 1
                # Message is already in the window (added when notification was created)
            return
        
        # Check Messages notifications
        clicked_messages_data = self.messages_notifications.handle_click(pos)
        if clicked_messages_data:
            # Bring Messages window to front
            messages_window = next((m for m in self.menus if isinstance(m, MessagesWindow)), None)
            if messages_window:
                # Bring to front
                max_z = max([m.z_index for m in self.menus] + [self.activity_log_window.z_index], default=0)
                messages_window.z_index = max_z + 1
                # Message is already in the window (added when notification was created)
            return
        
        # Check Discord notifications
        clicked_discord_data = self.discord_notifications.handle_click(pos)
        if clicked_discord_data:
            # Bring Discord window to front
            discord_window = next((m for m in self.menus if isinstance(m, DiscordWindow)), None)
            if discord_window:
                # Bring to front
                max_z = max([m.z_index for m in self.menus] + [self.activity_log_window.z_index], default=0)
                discord_window.z_index = max_z + 1
                # Message is already in the window (added when notification was created)
            return
        
        # Check activity log window
        if self.activity_log_window.handle_click(pos):
            # Bring activity log to front
            max_z = max([m.z_index for m in self.menus] + [self.activity_log_window.z_index])
            self.activity_log_window.z_index = max_z + 1
            return
        
        # Check menu windows (from top to bottom)
        clicked_menu = None
        for menu in sorted(self.menus, key=lambda m: m.z_index, reverse=True):
            if menu.handle_click(pos):
                clicked_menu = menu
                # Bring clicked menu to front
                max_z = max([m.z_index for m in self.menus] + [self.activity_log_window.z_index])
                menu.z_index = max_z + 1
                
                # Check if Outlook wants to open an email in a new window
                if isinstance(menu, OutlookWindow) and menu.email_to_open:
                    # Check if email is already open
                    email_data = menu.email_to_open
                    existing_window = next((w for w in self.menus if isinstance(w, EmailViewWindow) and 
                                          w.email_data.get('subject') == email_data.get('subject') and
                                          w.email_data.get('from') == email_data.get('from')), None)
                    
                    if existing_window:
                        # Center the existing window instead of opening a new one
                        existing_window.position[0] = (SCREEN_WIDTH - existing_window.width) // 2
                        existing_window.position[1] = (SCREEN_HEIGHT - existing_window.height) // 2
                        # Bring to front
                        max_z = max([m.z_index for m in self.menus] + [self.activity_log_window.z_index], default=0)
                        existing_window.z_index = max_z + 1
                    else:
                        # Open new window
                        self._open_email_window(email_data)
                    menu.email_to_open = None
                
                # Check if EmailViewWindow should close
                if isinstance(menu, EmailViewWindow) and menu.should_close:
                    if menu in self.menus:
                        self.menus.remove(menu)
                    if menu in self.email_view_windows:
                        self.email_view_windows.remove(menu)
                    continue
                
                # Check if EmailViewWindow wants to open a reply window
                if isinstance(menu, EmailViewWindow) and menu.reply_to_open:
                    self._open_reply_window(menu.email_data, menu.reply_to_open)
                    menu.reply_to_open = None
                
                # Check if ReplyWindow should close
                if isinstance(menu, ReplyWindow) and menu.should_close:
                    # Update the email in Outlook to mark it as replied
                    if menu.sent_reply:
                        outlook_window = next((m for m in self.menus if isinstance(m, OutlookWindow)), None)
                        if outlook_window:
                            # Find and update the email
                            for email in outlook_window.emails:
                                if (email.get('subject') == menu.email_data.get('subject') and
                                    email.get('from') == menu.email_data.get('from')):
                                    email['replied'] = True
                                    email['reply_text'] = menu.sent_reply
                                    break
                        
                        # Add activity log entry for responding to email
                        self.activity_log_window.add_activity("You responded to an email", 0.1)
                        # Increase progress by 0.1%
                        self.game_state.increase_progress(0.1)
                        # Create progress popup
                        progress_bar_center = (
                            self.activity_log_window.position[0] + self.activity_log_window.width // 2,
                            self.activity_log_window.position[1] + self.activity_log_window.titlebar_height + 35
                        )
                        import time
                        self.progress_popup_system.check_progress_increase(self.game_state.progress, progress_bar_center)
                    
                    # Also close the email view window if it's open
                    email_view_window = next((w for w in self.menus if isinstance(w, EmailViewWindow) and 
                                            w.email_data.get('subject') == menu.email_data.get('subject')), None)
                    if email_view_window:
                        email_view_window.should_close = True
                    
                    if menu in self.menus:
                        self.menus.remove(menu)
                    if menu in self.email_view_windows:
                        self.email_view_windows.remove(menu)
                
                break
        
        # Update game state based on interactions
        if clicked_menu:
            self.game_state.on_menu_interaction()
    
    def _handle_release(self, pos):
        """Handle mouse release (end drag)"""
        # Let activity log window handle release
        self.activity_log_window.handle_release(pos)
        
        # Let menus handle the release
        for menu in self.menus:
            menu.handle_release(pos)
        
        # Track interaction for game state
        if self._find_menu_at_position(pos):
            self.game_state.on_menu_interaction()
    
    def _handle_drag(self, pos):
        """Handle mouse drag"""
        # Handle activity log window dragging
        self.activity_log_window.handle_drag(pos)
        
        # Handle window dragging
        for menu in self.menus:
            menu.handle_drag(pos)
    
    def _find_menu_at_position(self, pos):
        """Find which menu (if any) contains the given position"""
        # Check menus from top to bottom (highest z-index first)
        for menu in sorted(self.menus, key=lambda m: m.z_index, reverse=True):
            if menu.contains_point(pos) and not menu.is_blocked:
                return menu
        return None
    
    def update(self):
        """Update game state"""
        if self.game_complete:
            if self.ending_screen:
                self.ending_screen.update()
            return
        
        # Update game state (secret: progress increases automatically)
        self.game_state.update()
        
        # Update Calvelli log
        current_time_ms = pygame.time.get_ticks()
        self.calvelli_log.update(current_time_ms)
        
        # Check if log triggered a progress increase and add to activity log
        progress_increase = self.calvelli_log.get_progress_increase()
        if progress_increase > 0:
            old_progress = self.game_state.progress
            self.game_state.increase_progress(progress_increase)
            # Add activity to log window with progress increase
            if self.calvelli_log.current_log:
                self.activity_log_window.add_activity(self.calvelli_log.current_log, progress_increase)
                # Create progress popup animation
                progress_bar_center = (
                    self.activity_log_window.position[0] + self.activity_log_window.width // 2,
                    self.activity_log_window.position[1] + self.activity_log_window.titlebar_height + 35
                )
                import time
                current_time = time.time()
                self.progress_popup_system.check_progress_increase(self.game_state.progress, progress_bar_center)
                
                # Trigger Slack, Messages, or Discord notification (random choice)
                # First add message to window, then create notification
                import random
                choice = random.random()
                if choice < 0.33:
                    # Add message to Slack window first
                    slack_window = next((m for m in self.menus if isinstance(m, SlackWindow)), None)
                    if slack_window:
                        channel = random.choice(self.slack_notifications.channels)
                        user = random.choice(self.slack_notifications.users)
                        message = random.choice(self.slack_notifications.message_templates)
                        slack_window.add_message(channel, user, message)
                        # Then create notification
                        self.slack_notifications.add_notification(channel, user, message)
                elif choice < 0.66:
                    # Add message to Messages window first
                    messages_window = next((m for m in self.menus if isinstance(m, MessagesWindow)), None)
                    if messages_window:
                        contact = random.choice(self.messages_notifications.contacts)
                        message = random.choice(self.messages_notifications.message_templates)
                        messages_window.add_message(contact, message)
                        # Then create notification
                        self.messages_notifications.add_notification(contact, message)
                else:
                    # Add message to Discord window first
                    discord_window = next((m for m in self.menus if isinstance(m, DiscordWindow)), None)
                    if discord_window:
                        channel = random.choice(self.discord_notifications.channels)
                        user = random.choice(self.discord_notifications.users)
                        message = random.choice(self.discord_notifications.message_templates)
                        discord_window.add_message(channel, user, message)
                        # Then create notification
                        self.discord_notifications.add_notification(channel, user, message)
                
                # Randomly trigger FTL or Zomboid notification
                if random.random() < 0.3:  # 30% chance
                    game_type = random.choice(["ftl", "zomboid"])
                    if game_type == "ftl":
                        ftl_window = next((m for m in self.menus if isinstance(m, FTLWindow)), None)
                        if ftl_window:
                            self.game_notifications.trigger_notification("ftl", ftl_window)
                    else:
                        zomboid_window = next((m for m in self.menus if isinstance(m, ZomboidWindow)), None)
                        if zomboid_window:
                            self.game_notifications.trigger_notification("zomboid", zomboid_window)
                
                # Randomly trigger phone call (20% chance)
                if random.random() < 0.2:  # 20% chance
                    if not (self.phone_call_system.active_call and self.phone_call_system.active_call.active):
                        self.phone_call_system.trigger_call()
        
        # Check if it's time to send a congratulatory email notification
        if self.calvelli_log.should_trigger_email(current_time_ms):
            self._trigger_congratulatory_email()
        
        # Update email notifications
        self.email_notifications.update()
        
        # Update Slack notifications
        self.slack_notifications.update()
        
        # Update Messages notifications
        self.messages_notifications.update()
        
        # Check for milestone notifications
        import time
        current_time = time.time()
        self.milestone_notifications.check_milestones(self.game_state.progress)
        self.milestone_notifications.update(current_time)
        
        # Update progress popup system
        self.progress_popup_system.update(current_time)
        
        # Update Outlook email system
        if self.outlook_email_system:
            self.outlook_email_system.update()
        
        # Update Outlook window (for highlight timer and blinking)
        outlook_window = next((m for m in self.menus if isinstance(m, OutlookWindow)), None)
        if outlook_window:
            # Use milliseconds for dt (matching blink_timer which uses milliseconds)
            dt = 16  # Approximate frame time in ms (60 FPS)
            outlook_window.update(dt)
        
        # Update themed windows (e.g., Zomboid cycling, Outlook blinking)
        dt = self.clock.get_time()
        for menu in self.menus:
            if hasattr(menu, 'update'):
                menu.update(dt)
        
        # Clean up closed email/reply view windows
        windows_to_remove = [w for w in self.email_view_windows if hasattr(w, 'should_close') and w.should_close]
        for window in windows_to_remove:
            if window in self.menus:
                self.menus.remove(window)
            if window in self.email_view_windows:
                self.email_view_windows.remove(window)
        
        # Also check all menus for EmailViewWindows that should close
        email_windows_to_remove = [w for w in self.menus if isinstance(w, EmailViewWindow) and 
                                   hasattr(w, 'should_close') and w.should_close]
        for window in email_windows_to_remove:
            if window in self.menus:
                self.menus.remove(window)
            if window in self.email_view_windows:
                self.email_view_windows.remove(window)
    
    def _trigger_congratulatory_email(self):
        """Trigger a congratulatory email notification and add to Outlook"""
        from messages_content import CONGRATULATORY_EMAILS
        import random
        import time
        
        # Pick a random congratulatory email
        email_template = random.choice(CONGRATULATORY_EMAILS)
        timestamp = time.time()
        
        # Add notification
        self.email_notifications.add_congratulatory_notification(email_template)
        
        # Add to Outlook inbox
        outlook_window = next((m for m in self.menus if isinstance(m, OutlookWindow)), None)
        if outlook_window:
            outlook_window._add_congratulatory_email(email_template, timestamp)
    
    def _open_email_window(self, email_data):
        """Open an email in a new window"""
        # Calculate position (slightly offset from center)
        import random
        x = 400 + random.randint(-100, 100)
        y = 200 + random.randint(-50, 50)
        
        # Get max z-index to put new window on top
        max_z = max([m.z_index for m in self.menus] + [self.activity_log_window.z_index], default=0)
        
        # Create email view window
        email_window = EmailViewWindow(
            email_data=email_data,
            position=(x, y),
            assets_path=self.assets_path,
            z_index=max_z + 1
        )
        
        # Add to menus list
        self.menus.append(email_window)
        self.email_view_windows.append(email_window)
    
    def _open_reply_window(self, email_data, selected_response):
        """Open a reply composition window"""
        # Calculate position (slightly offset from center)
        import random
        x = 500 + random.randint(-50, 50)
        y = 250 + random.randint(-50, 50)
        
        # Get max z-index to put new window on top
        max_z = max([m.z_index for m in self.menus] + [self.activity_log_window.z_index], default=0)
        
        # Create reply window
        reply_window = ReplyWindow(
            email_data=email_data,
            selected_response=selected_response,
            position=(x, y),
            assets_path=self.assets_path,
            z_index=max_z + 1
        )
        
        # Add to menus list
        self.menus.append(reply_window)
        self.email_view_windows.append(reply_window)
        
        # Check if game is complete
        if self.game_state.progress >= 100.0:
            self.game_complete = True
            self.ending_screen = EndingScreen(
                self.screen,
                self.game_state,
                self.assets_path
            )
            if 'celebration' in self.sounds:
                self.sounds['celebration'].play()
    
    def render(self):
        """Render the game"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        if self.game_complete:
            if self.ending_screen:
                self.ending_screen.render()
        else:
            # Draw menu windows (including game notification overlays)
            for menu in sorted(self.menus, key=lambda m: m.z_index):
                menu.render(self.screen)
                # Draw game notification overlays on FTL/Zomboid windows
                if isinstance(menu, FTLWindow):
                    notification = self.game_notifications.active_notifications.get("ftl")
                    if notification and notification.active:
                        notification.render(self.screen)
                elif isinstance(menu, ZomboidWindow):
                    notification = self.game_notifications.active_notifications.get("zomboid")
                    if notification and notification.active:
                        notification.render(self.screen)
            
            # Draw activity log window (with progress bar inside) - render after menus so it can be on top
            self.activity_log_window.render(self.screen, self.game_state.progress)
            
            # Draw email notifications (top right)
            self.email_notifications.render(self.screen)
            
            # Draw Slack notifications (stacked below email notifications)
            # Calculate offset based on email notification count
            email_notification_count = len(self.email_notifications.notifications)
            slack_y_offset = self.email_notifications.start_y
            if email_notification_count > 0:
                # Calculate total height of email notifications
                for i, notif in enumerate(self.email_notifications.notifications):
                    if notif.is_dismissing:
                        slide_progress = abs(notif.y_offset) / 100.0
                        spacing = int((90 + self.email_notifications.notification_spacing) * (1.0 - slide_progress))
                    else:
                        spacing = 90 + self.email_notifications.notification_spacing
                    slack_y_offset += spacing
                slack_y_offset += 10  # Gap between systems
            
            # Temporarily adjust start_y for rendering
            original_slack_y = self.slack_notifications.start_y
            self.slack_notifications.start_y = slack_y_offset
            self.slack_notifications.render(self.screen)
            self.slack_notifications.start_y = original_slack_y
            
            # Draw Messages notifications (stacked below Slack notifications)
            messages_y_offset = slack_y_offset
            slack_notification_count = len(self.slack_notifications.notifications)
            if slack_notification_count > 0:
                # Calculate total height of Slack notifications
                for i, notif in enumerate(self.slack_notifications.notifications):
                    if notif.is_dismissing:
                        slide_progress = abs(notif.y_offset) / 100.0
                        spacing = int((80 + self.slack_notifications.notification_spacing) * (1.0 - slide_progress))
                    else:
                        spacing = 80 + self.slack_notifications.notification_spacing
                    messages_y_offset += spacing
                messages_y_offset += 10  # Gap between systems
            
            # Temporarily adjust start_y for rendering
            original_messages_y = self.messages_notifications.start_y
            self.messages_notifications.start_y = messages_y_offset
            self.messages_notifications.render(self.screen)
            self.messages_notifications.start_y = original_messages_y
            
            # Draw Discord notifications (stacked below Messages notifications)
            discord_y_offset = messages_y_offset
            messages_notification_count = len(self.messages_notifications.notifications)
            if messages_notification_count > 0:
                # Calculate total height of Messages notifications
                for i, notif in enumerate(self.messages_notifications.notifications):
                    if notif.is_dismissing:
                        slide_progress = abs(notif.y_offset) / 100.0
                        spacing = int((80 + self.messages_notifications.notification_spacing) * (1.0 - slide_progress))
                    else:
                        spacing = 80 + self.messages_notifications.notification_spacing
                    discord_y_offset += spacing
                discord_y_offset += 10  # Gap between systems
            
            # Temporarily adjust start_y for rendering
            original_discord_y = self.discord_notifications.start_y
            self.discord_notifications.start_y = discord_y_offset
            self.discord_notifications.render(self.screen)
            self.discord_notifications.start_y = original_discord_y
            
            # Draw phone call popup and conversation (on top of everything)
            self.phone_call_system.render(self.screen)
            
            # Draw phone call popup and conversation (on top of everything)
            self.phone_call_system.render(self.screen)
            
            # Draw milestone notifications (on top)
            self.milestone_notifications.render(self.screen)
            
            # Draw progress popups (on top of activity log window)
            self.progress_popup_system.render(self.screen)
            
            # Draw Discord interruption if active (on top of everything)
            if self.discord_interrupt.is_active():
                self.discord_interrupt.render(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
