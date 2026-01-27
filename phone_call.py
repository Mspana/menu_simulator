"""
Phone Call System
Manages incoming phone calls and conversations
"""

import pygame
import random
import time
import math
import json
import os

class PhoneCall:
    """Represents an incoming phone call"""
    
    def __init__(self, caller_name, caller_number, conversation_messages=None):
        self.caller_name = caller_name
        self.caller_number = caller_number
        self.active = False
        self.answered = False
        self.start_time = None
        
        # Use provided conversation or default
        if conversation_messages:
            self.conversation_messages = conversation_messages
        else:
            # Default conversation
            self.conversation_messages = [
                {"speaker": "caller", "text": "Hey, how's the conference planning going?"},
                {"speaker": "player", "text": "Oh, it's going great! I've been working on it all day."},
                {"speaker": "caller", "text": "That's awesome! Need any help with anything?"},
                {"speaker": "player", "text": "Nah, I've got it covered. Thanks though!"},
                {"speaker": "caller", "text": "Alright, well keep up the good work!"},
            ]
        
        # Calculate conversation duration based on messages
        total_chars = sum(len(msg["text"]) for msg in self.conversation_messages)
        typing_time = total_chars * 0.05  # 0.05 seconds per character
        pause_time = (len(self.conversation_messages) - 1) * 0.8  # Pause between messages
        self.conversation_duration = typing_time + pause_time + 5  # Add buffer
        
        self.current_message_index = 0
        self.current_message_start_time = None
        self.typed_chars = 0  # Number of characters typed so far in current message
        self.char_typing_speed = 0.05  # Seconds per character
        self.pause_between_messages = 0.8  # Pause before next message starts
        self.message_complete = False
    
    def start_call(self):
        """Start the incoming call"""
        self.active = True
        self.answered = False
        self.start_time = time.time()
    
    def answer(self):
        """Answer the call"""
        self.answered = True
        self.start_time = time.time()
        self.current_message_index = 0
        self.current_message_start_time = time.time()
        self.typed_chars = 0
        self.message_complete = False
    
    def hang_up(self):
        """Hang up the call"""
        self.active = False
        self.answered = False
    
    def update(self, current_time):
        """Update call state"""
        if not self.active:
            return
        
        if self.answered:
            # Check if conversation should end
            elapsed = current_time - self.start_time
            if elapsed >= self.conversation_duration:
                self.active = False
                self.answered = False
                return
            
            # Update conversation typing
            if self.current_message_index < len(self.conversation_messages):
                message = self.conversation_messages[self.current_message_index]
                message_text = message["text"]
                
                if self.current_message_start_time is None:
                    self.current_message_start_time = current_time
                
                # Calculate how many characters should be typed
                time_since_start = current_time - self.current_message_start_time
                expected_chars = int(time_since_start / self.char_typing_speed)
                
                if expected_chars >= len(message_text):
                    # Message is complete
                    self.typed_chars = len(message_text)
                    self.message_complete = True
                    
                    # Check if we should move to next message
                    time_since_complete = current_time - (self.current_message_start_time + len(message_text) * self.char_typing_speed)
                    if time_since_complete >= self.pause_between_messages:
                        # Move to next message
                        self.current_message_index += 1
                        if self.current_message_index < len(self.conversation_messages):
                            self.current_message_start_time = current_time
                            self.typed_chars = 0
                            self.message_complete = False
                else:
                    # Still typing
                    self.typed_chars = expected_chars
                    self.message_complete = False
    
    def get_current_message(self):
        """Get the current message being displayed"""
        if not self.answered or not self.active:
            return None
        if self.current_message_index < len(self.conversation_messages):
            message = self.conversation_messages[self.current_message_index]
            return {
                "speaker": message["speaker"],
                "text": message["text"][:self.typed_chars]
            }
        return None
    
    def get_all_completed_messages(self):
        """Get all messages that have been fully typed"""
        completed = []
        for i in range(self.current_message_index):
            completed.append(self.conversation_messages[i])
        return completed


class PhoneCallSystem:
    """Manages phone call notifications and conversations"""
    
    def __init__(self):
        self.active_call = None
        self.call_popup_rect = None
        self.answer_button_rect = None
        self.hangup_button_rect = None
        self.conversation_window_rect = None
        
        # Load callers and conversations from JSON file
        self.callers, self.conversation_templates = self._load_phone_calls()
        
        # Popup dimensions
        self.popup_width = 400
        self.popup_height = 200
        self.popup_x = 1920 - self.popup_width - 50  # Bottom right
        self.popup_y = 1080 - self.popup_height - 50
    
    def _load_phone_calls(self):
        """Load phone call data from JSON file"""
        phone_calls_file = os.path.join(os.path.dirname(__file__), "phone_calls.json")
        try:
            with open(phone_calls_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extract callers as tuples (name, number)
                callers = [(caller["name"], caller["number"]) for caller in data.get("callers", [])]
                
                # Extract conversations
                conversations = data.get("conversations", {})
                
                return callers, conversations
        except FileNotFoundError:
            # Fallback to default if file doesn't exist
            return [
                ("Michael Miske", "(555) 123-4567"),
                ("Jar", "(555) 345-6789"),
                ("Halle", "(555) 456-7890"),
                ("Anne", "(555) 789-0123"),
            ], {}
        
        # Conversation window dimensions
        self.conv_width = 500  # Wider to accommodate silhouette and audio bars
        self.conv_height = 200
        self.conv_x = 1920 - self.conv_width - 50  # Bottom right
        self.conv_y = 1080 - self.conv_height - 50
        
        # Audio visualization animation
        self.audio_bars = [0.0] * 8  # 8 bars for visualization
        self.audio_animation_time = 0.0
        self.audio_animation_speed = 0.3
    
    def trigger_call(self):
        """Trigger a new incoming call"""
        if self.active_call and self.active_call.active:
            return  # Don't trigger if a call is already active
        
        caller_name, caller_number = random.choice(self.callers)
        
        # Get conversation for this caller
        conversation = self.conversation_templates.get(caller_name)
        if not conversation:
            # Fallback to default
            conversation = None
        
        self.active_call = PhoneCall(caller_name, caller_number, conversation)
        self.active_call.start_call()
        
        # Set up popup rects
        self.call_popup_rect = pygame.Rect(
            self.popup_x, self.popup_y,
            self.popup_width, self.popup_height
        )
        
        # Answer button (green, left side)
        self.answer_button_rect = pygame.Rect(
            self.popup_x + 50,
            self.popup_y + 140,
            120, 40
        )
        
        # Hang up button (red, right side)
        self.hangup_button_rect = pygame.Rect(
            self.popup_x + 230,
            self.popup_y + 140,
            120, 40
        )
    
    def handle_click(self, pos):
        """Handle clicks on the call popup"""
        if not self.active_call or not self.active_call.active:
            return False
        
        if not self.active_call.answered:
            # Check answer button
            if self.answer_button_rect and self.answer_button_rect.collidepoint(pos):
                self.active_call.answer()
                # Set up conversation window
                self.conversation_window_rect = pygame.Rect(
                    self.conv_x, self.conv_y,
                    self.conv_width, self.conv_height
                )
                return True
            
            # Check hang up button
            if self.hangup_button_rect and self.hangup_button_rect.collidepoint(pos):
                self.active_call.hang_up()
                return True
        
        return False
    
    def update(self, current_time):
        """Update phone call system"""
        if self.active_call:
            self.active_call.update(current_time)
            
            # Update audio visualization animation if call is answered
            if self.active_call.answered and self.active_call.active:
                self.audio_animation_time += self.audio_animation_speed
                # Animate bars with sine waves at different frequencies
                for i in range(len(self.audio_bars)):
                    # Each bar oscillates at a different frequency
                    frequency = 0.5 + (i * 0.15)
                    phase = i * 0.5
                    self.audio_bars[i] = abs(math.sin(self.audio_animation_time * frequency + phase))
            else:
                # Reset bars when not speaking
                self.audio_bars = [0.0] * len(self.audio_bars)
    
    def render(self, screen):
        """Render phone call popup and conversation"""
        if not self.active_call or not self.active_call.active:
            return
        
        # Draw semi-transparent overlay only if call is not answered
        if not self.active_call.answered:
            overlay = pygame.Surface((1920, 1080))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
        
        if not self.active_call.answered:
            # Draw call popup
            pygame.draw.rect(screen, (240, 240, 240), self.call_popup_rect)
            pygame.draw.rect(screen, (100, 100, 100), self.call_popup_rect, 3)
            
            # Draw caller info
            font_large = pygame.font.Font(None, 32)
            font_medium = pygame.font.Font(None, 24)
            
            caller_text = font_large.render(self.active_call.caller_name, True, (0, 0, 0))
            caller_rect = caller_text.get_rect(center=(self.popup_x + self.popup_width // 2, self.popup_y + 40))
            screen.blit(caller_text, caller_rect)
            
            number_text = font_medium.render(self.active_call.caller_number, True, (100, 100, 100))
            number_rect = number_text.get_rect(center=(self.popup_x + self.popup_width // 2, self.popup_y + 75))
            screen.blit(number_text, number_rect)
            
            # Draw "Incoming Call" text
            incoming_text = font_medium.render("Incoming Call", True, (50, 50, 50))
            incoming_rect = incoming_text.get_rect(center=(self.popup_x + self.popup_width // 2, self.popup_y + 110))
            screen.blit(incoming_text, incoming_rect)
            
            # Draw answer button (green)
            pygame.draw.rect(screen, (0, 180, 0), self.answer_button_rect)
            pygame.draw.rect(screen, (0, 120, 0), self.answer_button_rect, 2)
            answer_text = font_medium.render("Answer", True, (255, 255, 255))
            answer_rect = answer_text.get_rect(center=self.answer_button_rect.center)
            screen.blit(answer_text, answer_rect)
            
            # Draw hang up button (red)
            pygame.draw.rect(screen, (200, 0, 0), self.hangup_button_rect)
            pygame.draw.rect(screen, (150, 0, 0), self.hangup_button_rect, 2)
            hangup_text = font_medium.render("Hang Up", True, (255, 255, 255))
            hangup_rect = hangup_text.get_rect(center=self.hangup_button_rect.center)
            screen.blit(hangup_text, hangup_rect)
        
        elif self.active_call.answered:
            # Draw conversation window (bottom right)
            if self.conversation_window_rect:
                # Window background
                pygame.draw.rect(screen, (50, 50, 50), self.conversation_window_rect)
                pygame.draw.rect(screen, (100, 100, 100), self.conversation_window_rect, 2)
                
                # Title bar
                title_bar = pygame.Rect(
                    self.conv_x, self.conv_y,
                    self.conv_width, 30
                )
                pygame.draw.rect(screen, (70, 70, 70), title_bar)
                
                # Caller name in title
                font_small = pygame.font.Font(None, 18)
                title_text = font_small.render(f"Call with {self.active_call.caller_name}", True, (255, 255, 255))
                screen.blit(title_text, (self.conv_x + 10, self.conv_y + 8))
                
                # Call duration indicator
                if self.active_call.start_time:
                    elapsed = time.time() - self.active_call.start_time
                    remaining = max(0, self.active_call.conversation_duration - elapsed)
                    duration_text = font_small.render(f"{remaining:.1f}s", True, (150, 150, 150))
                    screen.blit(duration_text, (self.conv_x + self.conv_width - 50, self.conv_y + 8))
                
                # Content area (below title bar)
                content_y = self.conv_y + 35
                content_height = self.conv_height - 35
                
                # Calculate widths: audio bars 2/3, silhouette 1/3
                audio_area_width = int(self.conv_width * 2 / 3)
                silhouette_width = self.conv_width - audio_area_width
                
                # Draw audio visualization bars (left side, 2/3 width)
                audio_x = self.conv_x + 10
                audio_y = content_y + 10
                audio_height = content_height - 20
                bar_width = (audio_area_width - 20) // len(self.audio_bars) - 2
                bar_spacing = 2
                
                for i, bar_value in enumerate(self.audio_bars):
                    bar_x = audio_x + i * (bar_width + bar_spacing)
                    bar_max_height = audio_height
                    bar_current_height = int(bar_value * bar_max_height)
                    
                    # Draw bar (centered vertically)
                    bar_rect = pygame.Rect(
                        bar_x,
                        audio_y + (bar_max_height - bar_current_height) // 2,
                        bar_width,
                        bar_current_height
                    )
                    
                    # Color gradient: lower bars darker, higher bars brighter
                    intensity = int(100 + bar_value * 155)
                    bar_color = (intensity // 2, intensity, intensity // 2)  # Greenish
                    pygame.draw.rect(screen, bar_color, bar_rect)
                    pygame.draw.rect(screen, (intensity // 3, intensity // 2, intensity // 3), bar_rect, 1)
                
                # Draw silhouette (right side, 1/3 width)
                silhouette_x = self.conv_x + audio_area_width
                silhouette_y = content_y
                silhouette_height = content_height
                
                # Draw silhouette background (dark shape)
                silhouette_rect = pygame.Rect(
                    silhouette_x,
                    silhouette_y,
                    silhouette_width,
                    silhouette_height
                )
                pygame.draw.rect(screen, (30, 30, 30), silhouette_rect)
                
                # Draw simple silhouette shape (head and shoulders)
                center_x = silhouette_x + silhouette_width // 2
                center_y = silhouette_y + silhouette_height // 2
                
                # Head (circle)
                head_radius = min(silhouette_width // 3, silhouette_height // 4)
                pygame.draw.circle(screen, (20, 20, 20), (center_x, center_y - head_radius), head_radius)
                pygame.draw.circle(screen, (40, 40, 40), (center_x, center_y - head_radius), head_radius, 2)
                
                # Shoulders (rounded rectangle)
                shoulder_width = silhouette_width - 20
                shoulder_height = silhouette_height // 3
                shoulder_rect = pygame.Rect(
                    center_x - shoulder_width // 2,
                    center_y,
                    shoulder_width,
                    shoulder_height
                )
                pygame.draw.rect(screen, (20, 20, 20), shoulder_rect)
                pygame.draw.rect(screen, (40, 40, 40), shoulder_rect, 2)
                
                # Conversation messages area (below audio bars and silhouette)
                font_conv = pygame.font.Font(None, 16)
                font_speaker = pygame.font.Font(None, 14)
                max_width = self.conv_width - 20
                
                # Get completed messages and current message
                completed_messages = self.active_call.get_all_completed_messages()
                current_message = self.active_call.get_current_message()
                
                # Calculate starting Y position (show last few messages)
                messages_to_show = completed_messages + ([current_message] if current_message else [])
                # Only show last 3 messages to fit in window
                messages_to_show = messages_to_show[-3:]
                
                # Draw messages from bottom up
                message_y = content_y + content_height - 10
                line_height = 18
                
                for message in reversed(messages_to_show):
                    if message is None:
                        continue
                    
                    speaker = message["speaker"]
                    text = message["text"]
                    
                    # Determine color based on speaker
                    if speaker == "caller":
                        speaker_color = (150, 200, 255)  # Light blue for caller
                        text_color = (220, 220, 220)
                    else:
                        speaker_color = (150, 255, 150)  # Light green for player
                        text_color = (255, 255, 255)
                    
                    # Draw speaker label
                    speaker_label = "Caller" if speaker == "caller" else "You"
                    speaker_surface = font_speaker.render(speaker_label + ":", True, speaker_color)
                    screen.blit(speaker_surface, (self.conv_x + 10, message_y - line_height))
                    
                    # Wrap and draw message text
                    words = text.split(' ')
                    lines = []
                    current_line_text = ""
                    
                    for word in words:
                        test_line = current_line_text + (" " if current_line_text else "") + word
                        test_surface = font_conv.render(test_line, True, text_color)
                        if test_surface.get_width() <= max_width - 60:  # Leave space for speaker label
                            current_line_text = test_line
                        else:
                            if current_line_text:
                                lines.append(current_line_text)
                            current_line_text = word
                    if current_line_text:
                        lines.append(current_line_text)
                    
                    # Draw text lines
                    for i, line in enumerate(lines):
                        line_surface = font_conv.render(line, True, text_color)
                        screen.blit(line_surface, (self.conv_x + 60, message_y - line_height + i * line_height))
                    
                    # Add typing cursor if this is the current message and not complete
                    if message == current_message and not self.active_call.message_complete:
                        cursor_x = self.conv_x + 60
                        if lines:
                            last_line = lines[-1]
                            last_line_surface = font_conv.render(last_line, True, text_color)
                            cursor_x += last_line_surface.get_width()
                        else:
                            cursor_x += font_conv.render(speaker_label + ":", True, text_color).get_width()
                        
                        # Blinking cursor
                        if int(time.time() * 2) % 2 == 0:
                            pygame.draw.line(screen, text_color, 
                                           (cursor_x, message_y - line_height + (len(lines) - 1) * line_height),
                                           (cursor_x, message_y - line_height + (len(lines) - 1) * line_height + 14), 2)
                    
                    # Move up for next message
                    message_y -= (len(lines) + 1) * line_height + 5
                    
                    if message_y < content_y:
                        break  # Don't draw outside content area
