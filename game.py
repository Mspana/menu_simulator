"""
Menu Simulator Game
Main entry point and game loop
"""

import pygame
import sys
import os
import argparse
import math
import random
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
from start_screen import StartScreen
from startup_animation import StartupAnimation

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Configure global font to use Inter instead of the default system font
try:
    _real_font_ctor = pygame.font.Font
    _fonts_dir = os.path.join(
        os.path.dirname(__file__),
        "assets_pack",
        "fonts",
        "Inter",
    )
    _inter_path = os.path.join(_fonts_dir, "Inter-VariableFont_opsz,wght.ttf")
    _font_cache = {}

    def _inter_font(path, size):
        """Drop‑in replacement for pygame.font.Font with caching for Inter.

        When callers pass None, we approximate the old default font's visual
        size by adjusting Inter's point size so the text height matches.
        """
        # When callers pass None, use our Inter font (cached per requested size)
        if path is None:
            if size not in _font_cache:
                # Use Inter at a size slightly smaller than the requested logical size.
                # 0.85 keeps layout close to original while making text a bit larger.
                adjusted_size = max(1, int(round(size * 0.85)))
                _font_cache[size] = _real_font_ctor(_inter_path, adjusted_size)
            return _font_cache[size]
        # For explicit paths, fall back to the real ctor
        return _real_font_ctor(path, size)

    pygame.font.Font = _inter_font
except Exception:
    # Fallback gracefully to default font if Inter isn't available
    pass

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 212)

class Game:
    def __init__(self, skip_startup=False):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Menu Simulator - Fundraising for a Conference")
        self.clock = pygame.time.Clock()
        self.running = True
        self.skip_startup = skip_startup
        
        # Startup sequence
        if not skip_startup:
            self.start_screen = StartScreen(self.screen)
            self.startup_animation = None
            self.showing_start_screen = True
            self.showing_startup_animation = False
        else:
            self.start_screen = None
            self.startup_animation = None
            self.showing_start_screen = False
            self.showing_startup_animation = False
        self.game_started = skip_startup
        # Track when the game instance was created (for gating early events)
        self.start_time_ms = pygame.time.get_ticks()
        
        # Load assets
        self.assets_path = os.path.join(os.path.dirname(__file__), "assets_pack")
        # Desktop background: randomly choose one of the provided background images
        backgrounds_dir = os.path.join(self.assets_path, "backgrounds")
        try:
            available = [f for f in os.listdir(backgrounds_dir)
                         if f.lower().startswith("background") and f.lower().endswith(".png")]
            if available:
                chosen = random.choice(available)
                bg_path = os.path.join(backgrounds_dir, chosen)
                bg_image = pygame.image.load(bg_path).convert()
                # Scale to screen size if needed
                if bg_image.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
                    bg_image = pygame.transform.smoothscale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.background = bg_image
            else:
                # Fallback: solid color background if no files match
                self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                self.background.fill((0, 100, 160))
        except Exception:
            # Fallback: solid color background if loading fails
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((0, 100, 160))
        
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
            (600, 180),
            (700, 220)  # Discord window position
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
                # Handle start screen
                if self.showing_start_screen and self.start_screen:
                    if self.start_screen.handle_keypress(event.key):
                        self.showing_start_screen = False
                        self.showing_startup_animation = True
                        import time
                        # Include activity log window in startup animations
                        windows_for_animation = [self.activity_log_window] + self.menus
                        self.startup_animation = StartupAnimation(self.screen, windows_for_animation)
                    continue
                
                if event.key == pygame.K_ESCAPE:
                    if self.game_complete:
                        self.running = False
                    # Don't exit during startup
                    if not self.showing_start_screen and not self.showing_startup_animation:
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
                    # Handle start screen
                    if self.showing_start_screen and self.start_screen:
                        if self.start_screen.handle_click(event.pos):
                            self.showing_start_screen = False
                            self.showing_startup_animation = True
                            # Include activity log window in startup animations
                            windows_for_animation = [self.activity_log_window] + self.menus
                            self.startup_animation = StartupAnimation(self.screen, windows_for_animation)
                        continue
                    
                    if not self.showing_startup_animation:
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
                        # Ensure it is not hidden behind the activity log window
                        min_x = self.activity_log_window.position[0] + self.activity_log_window.width + 20
                        if existing_window.position[0] < min_x:
                            existing_window.position[0] = min_x
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
                
                break
        
        # Update game state based on interactions
        if clicked_menu:
            self.game_state.on_menu_interaction()

    def _register_small_progress(self, message):
        """Helper to add a small (+0.1%) progress event to the activity log."""
        self.activity_log_window.add_activity(message, 0.1)
        self.game_state.increase_progress(0.1)
        # Create a progress popup over the progress bar
        progress_bar_center = (
            self.activity_log_window.position[0] + self.activity_log_window.width // 2,
            self.activity_log_window.position[1] + self.activity_log_window.titlebar_height + 35
        )
        import time
        self.progress_popup_system.check_progress_increase(self.game_state.progress, progress_bar_center)
    
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
        # Handle startup animation
        if self.showing_startup_animation and self.startup_animation:
            dt = self.clock.get_time() / 1000.0  # Convert to seconds
            if self.startup_animation.update(dt):
                self.showing_startup_animation = False
                self.game_started = True
        
        # Don't update game if not started
        if not self.game_started:
            return
        
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
                
                # Randomly trigger FTL or Zomboid notification, but not in the first 30 seconds
                elapsed_ms = current_time_ms - self.start_time_ms
                if elapsed_ms >= 30000:
                    if random.random() < 0.15:  # 15% chance (slightly less frequent)
                        game_type = random.choice(["ftl", "zomboid"])
                        if game_type == "ftl":
                            ftl_window = next((m for m in self.menus if isinstance(m, FTLWindow)), None)
                            if ftl_window:
                                self.game_notifications.trigger_notification("ftl", ftl_window, self.menus)
                        else:
                            zomboid_window = next((m for m in self.menus if isinstance(m, ZomboidWindow)), None)
                            if zomboid_window:
                                self.game_notifications.trigger_notification("zomboid", zomboid_window, self.menus)
                
                # Randomly trigger phone call (20% chance), but not in the first 30 seconds
                elapsed_ms = current_time_ms - self.start_time_ms
                if elapsed_ms >= 30000:
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
        
        # Update phone call system
        self.phone_call_system.update(current_time)
        
        # Update FTL/Zomboid mini-game notifications
        self.game_notifications.update()
        # Grant small progress when a mini-game completes
        if self.game_notifications.completed_events:
            for game_type in self.game_notifications.completed_events:
                if game_type == "ftl":
                    self._register_small_progress("You played FTL")
                elif game_type == "zomboid":
                    self._register_small_progress("You played Zomboid")
            self.game_notifications.completed_events.clear()
        
        # Update Outlook email system
        if self.outlook_email_system:
            self.outlook_email_system.update()
        
        # Open reply windows requested by any EmailViewWindow (triggered on mouse release)
        for menu in list(self.menus):
            if isinstance(menu, EmailViewWindow) and menu.reply_to_open:
                self._open_reply_window(menu.email_data, menu.reply_to_open)
                menu.reply_to_open = None
        
        # Update Outlook window (for highlight timer and blinking)
        outlook_window = next((m for m in self.menus if isinstance(m, OutlookWindow)), None)
        if outlook_window:
            # Use milliseconds for dt (matching blink_timer which uses milliseconds)
            dt = 16  # Approximate frame time in ms (60 FPS)
            outlook_window.update(dt)
        
        # Check for replies sent in Messages, Slack, and Discord windows
        messages_window = next((m for m in self.menus if isinstance(m, MessagesWindow)), None)
        if messages_window and hasattr(messages_window, "sent_reply_events"):
            for event_msg in messages_window.sent_reply_events:
                self._register_small_progress(event_msg)
            messages_window.sent_reply_events.clear()
        
        slack_window = next((m for m in self.menus if isinstance(m, SlackWindow)), None)
        if slack_window and hasattr(slack_window, "sent_reply_events"):
            for event_msg in slack_window.sent_reply_events:
                self._register_small_progress(event_msg)
            slack_window.sent_reply_events.clear()
        
        discord_window = next((m for m in self.menus if isinstance(m, DiscordWindow)), None)
        if discord_window and hasattr(discord_window, "sent_reply_events"):
            for event_msg in discord_window.sent_reply_events:
                self._register_small_progress(event_msg)
            discord_window.sent_reply_events.clear()
        
        # Check for any ReplyWindow instances that have completed and should close
        reply_windows = [w for w in self.menus if isinstance(w, ReplyWindow) and getattr(w, "should_close", False)]
        for reply_window in reply_windows:
            # If a reply was actually sent, update Outlook and register small progress
            if reply_window.sent_reply:
                outlook_window = next((m for m in self.menus if isinstance(m, OutlookWindow)), None)
                if outlook_window:
                    # Find and update the corresponding email
                    for email in outlook_window.emails:
                        if (email.get('subject') == reply_window.email_data.get('subject') and
                            email.get('from') == reply_window.email_data.get('from')):
                            email['replied'] = True
                            email['reply_text'] = reply_window.sent_reply
                            break
                
                # Small progress entry for responding to an email
                self._register_small_progress("You responded to an email")
            
            # Also close the associated email view window if it's open
            email_view_window = next(
                (w for w in self.menus
                 if isinstance(w, EmailViewWindow)
                 and w.email_data.get('subject') == reply_window.email_data.get('subject')
                 and w.email_data.get('from') == reply_window.email_data.get('from')),
                None,
            )
            if email_view_window:
                email_view_window.should_close = True
            
            # Remove the reply window from management lists
            if reply_window in self.menus:
                self.menus.remove(reply_window)
            if reply_window in self.email_view_windows:
                self.email_view_windows.remove(reply_window)
        
        # If progress has reached 100% and game is not yet marked complete, trigger ending
        if not self.game_complete and self.game_state.progress >= 100.0:
            self.game_complete = True
            self.ending_screen = EndingScreen(
                self.screen,
                self.game_state,
                self.assets_path
            )
            if 'celebration' in self.sounds:
                self.sounds['celebration'].play()
        
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
        # Ensure the email window does not appear under the activity log window
        min_x = self.activity_log_window.position[0] + self.activity_log_window.width + 20
        if x < min_x:
            x = min_x
        
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
        # Show start screen
        if self.showing_start_screen and self.start_screen:
            self.start_screen.render()
            pygame.display.flip()
            return
        
        # Show startup animation
        if self.showing_startup_animation and self.startup_animation:
            self.startup_animation.render(self.background)
            pygame.display.flip()
            return
        
        # Don't render game if not started
        if not self.game_started:
            return
        
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
                # Calculate total height of email notifications (horizontal slide doesn't affect vertical spacing)
                for i, notif in enumerate(self.email_notifications.notifications):
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
                # Calculate total height of Slack notifications (horizontal slide doesn't affect vertical spacing)
                for i, notif in enumerate(self.slack_notifications.notifications):
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
                # Calculate total height of Messages notifications (horizontal slide doesn't affect vertical spacing)
                for i, notif in enumerate(self.messages_notifications.notifications):
                    spacing = 80 + self.messages_notifications.notification_spacing
                    discord_y_offset += spacing
                discord_y_offset += 10  # Gap between systems
            
            # Temporarily adjust start_y for rendering
            original_discord_y = self.discord_notifications.start_y
            self.discord_notifications.start_y = discord_y_offset
            self.discord_notifications.render(self.screen)
            self.discord_notifications.start_y = original_discord_y
            
            # Draw phone call popup (on top of everything)
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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Menu Simulator Game')
    parser.add_argument('--no_startup', action='store_true', 
                       help='Skip start screen and startup animations for development')
    args = parser.parse_args()
    
    game = Game(skip_startup=args.no_startup)
    game.run()
