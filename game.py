"""
Menu Simulator Game
Main entry point and game loop
"""

import pygame
import sys
import os
from themed_windows import (FTLWindow, ZomboidWindow, InventoryWindow, 
                           OutlookWindow, MessagesWindow, SlackWindow)
from email_view_window import EmailViewWindow
from reply_window import ReplyWindow
from discord_interrupt import DiscordInterrupt
from game_state import GameState
from ending import EndingScreen
from calvelli_log import CalvelliLog
from activity_log_window import ActivityLogWindow
from email_notifications import EmailNotificationSystem
from outlook_email_system import OutlookEmailSystem

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
        
        # Menus list (will include dynamically created email windows)
        self.menus = []
        
        # Create activity log window (tall, narrow window on the right)
        log_window_width = 350
        log_window_height = SCREEN_HEIGHT - 100
        log_window_x = SCREEN_WIDTH - log_window_width - 20
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
        # Check Discord popup first
        if self.discord_interrupt.is_active():
            if self.discord_interrupt.handle_click(pos, self.menus):
                return
        
        # Check email notifications (for opening email in new window)
        clicked_email_data = self.email_notifications.handle_click(pos)
        if clicked_email_data:
            # Find the email in Outlook and open it in a new window
            outlook_window = next((m for m in self.menus if isinstance(m, OutlookWindow)), None)
            if outlook_window:
                # Find the email
                for i, email in enumerate(outlook_window.emails):
                    if (email.get('type') == 'congratulatory' and 
                        email.get('subject') == clicked_email_data['subject']):
                        outlook_window.emails[i]['read'] = True
                        outlook_window.emails[i]['blinking'] = False  # Stop blinking
                        # Open in new window
                        self._open_email_window(outlook_window.emails[i])
                        break
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
                    self._open_email_window(menu.email_to_open)
                    menu.email_to_open = None
                
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
            self.game_state.increase_progress(progress_increase)
            # Add activity to log window
            if self.calvelli_log.current_log:
                self.activity_log_window.add_activity(self.calvelli_log.current_log)
        
        # Check if it's time to send a congratulatory email notification
        if self.calvelli_log.should_trigger_email(current_time_ms):
            self._trigger_congratulatory_email()
        
        # Update email notifications
        self.email_notifications.update()
        
        # Update Outlook email system
        if self.outlook_email_system:
            self.outlook_email_system.update()
        
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
            # Draw menu windows
            for menu in sorted(self.menus, key=lambda m: m.z_index):
                menu.render(self.screen)
            
            # Draw activity log window (with progress bar inside) - render after menus so it can be on top
            self.activity_log_window.render(self.screen, self.game_state.progress)
            
            # Draw email notifications (top right)
            self.email_notifications.render(self.screen)
            
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
