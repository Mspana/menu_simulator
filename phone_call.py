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
        # Get all messages before the current one
        for i in range(self.current_message_index):
            if i < len(self.conversation_messages):
                completed.append(self.conversation_messages[i])
        # Also include current message if it's complete
        if (self.current_message_index < len(self.conversation_messages) and 
            self.message_complete):
            completed.append(self.conversation_messages[self.current_message_index])
        return completed
    
    def get_current_speaker(self):
        """Get who is currently speaking"""
        if not self.answered or not self.active:
            return None
        if self.current_message_index < len(self.conversation_messages):
            return self.conversation_messages[self.current_message_index]["speaker"]
        return None


class PhoneCallSystem:
    """Manages phone call notifications and conversations"""
    
    def __init__(self):
        self.active_call = None
        self.call_popup_rect = None
        self.answer_button_rect = None
        self.hangup_button_rect = None
        
        # Load callers and conversations from JSON file
        self.callers, self.conversation_templates = self._load_phone_calls()
        
        # Popup dimensions (centered)
        self.popup_width = 400
        self.popup_height = 200
        self.popup_x = 960 - self.popup_width // 2  # Centered
        self.popup_y = 540 - self.popup_height // 2  # Centered
        
        # Conversation window dimensions
        self.conv_width = 400
        self.conv_height = 300
        self.conv_x = 1920 - self.conv_width - 50  # Bottom right
        self.conv_y = 1080 - self.conv_height - 50
        
        # Top section dimensions (for silhouette and audio)
        self.top_section_height = 100
        
        # Audio visualization animation
        self.audio_bars = [0.0] * 8  # 8 bars for visualization
        self.audio_animation_time = 0.0
        self.audio_animation_speed = 0.3
    
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
                current_speaker = self.active_call.get_current_speaker()
                # Bars animate more when someone is speaking
                base_amplitude = 0.3 if current_speaker else 0.1
                
                for i in range(len(self.audio_bars)):
                    # Each bar oscillates at a different frequency
                    frequency = 0.5 + (i * 0.15)
                    phase = i * 0.5
                    # Vary amplitude based on who's speaking
                    amplitude = base_amplitude + (0.7 if current_speaker else 0.0)
                    self.audio_bars[i] = abs(math.sin(self.audio_animation_time * frequency + phase)) * amplitude
            else:
                # Reset bars when not speaking
                self.audio_bars = [0.0] * len(self.audio_bars)
    
    def _draw_silhouette(self, screen, x, y, width, height):
        """Draw human-like silhouette (head and shoulders)"""
        # Head (circle/ellipse)
        head_radius = min(width, height) // 3
        head_center_x = x + width // 2
        head_center_y = y + head_radius + 5
        
        # Draw head
        pygame.draw.ellipse(screen, (30, 30, 30), 
                          (head_center_x - head_radius, head_center_y - head_radius,
                           head_radius * 2, head_radius * 2))
        pygame.draw.ellipse(screen, (60, 60, 60), 
                          (head_center_x - head_radius, head_center_y - head_radius,
                           head_radius * 2, head_radius * 2), 2)
        
        # Shoulders (trapezoid shape)
        shoulder_width = width * 0.8
        shoulder_height = height * 0.3
        shoulder_top_y = head_center_y + head_radius - 5
        shoulder_bottom_y = shoulder_top_y + shoulder_height
        
        # Create trapezoid points (wider at bottom)
        shoulder_top_width = shoulder_width * 0.6
        shoulder_bottom_width = shoulder_width
        
        points = [
            (head_center_x - shoulder_top_width // 2, shoulder_top_y),
            (head_center_x + shoulder_top_width // 2, shoulder_top_y),
            (head_center_x + shoulder_bottom_width // 2, shoulder_bottom_y),
            (head_center_x - shoulder_bottom_width // 2, shoulder_bottom_y),
        ]
        
        pygame.draw.polygon(screen, (30, 30, 30), points)
        pygame.draw.polygon(screen, (60, 60, 60), points, 2)
    
    def _draw_audio_bars(self, screen, x, y, width, height):
        """Draw animated audio visualization bars"""
        num_bars = len(self.audio_bars)
        bar_width = (width - (num_bars - 1) * 5) // num_bars  # 5px spacing between bars
        bar_spacing = 5
        
        current_speaker = self.active_call.get_current_speaker() if self.active_call else None
        
        for i, bar_value in enumerate(self.audio_bars):
            bar_x = x + i * (bar_width + bar_spacing)
            bar_height = int(height * bar_value)
            bar_y = y + height - bar_height
            
            # Color based on speaker
            if current_speaker == "caller":
                bar_color = (100, 150, 255)  # Blue for caller
            elif current_speaker == "player":
                bar_color = (100, 255, 150)  # Green for player
            else:
                bar_color = (100, 100, 100)  # Gray when silent
            
            # Draw bar
            pygame.draw.rect(screen, bar_color, 
                           (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (150, 150, 150), 
                           (bar_x, bar_y, bar_width, bar_height), 1)
    
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
            # Window background
            conv_rect = pygame.Rect(self.conv_x, self.conv_y, self.conv_width, self.conv_height)
            pygame.draw.rect(screen, (40, 40, 40), conv_rect)
            pygame.draw.rect(screen, (80, 80, 80), conv_rect, 2)
            
            # Top section: Silhouette + Audio bars
            top_section_y = self.conv_y
            top_section_rect = pygame.Rect(self.conv_x, top_section_y, self.conv_width, self.top_section_height)
            pygame.draw.rect(screen, (50, 50, 50), top_section_rect)
            
            # Silhouette on left (1/3 width)
            silhouette_width = self.conv_width // 3
            silhouette_x = self.conv_x + 10
            silhouette_y = top_section_y + 5
            silhouette_height = self.top_section_height - 10
            self._draw_silhouette(screen, silhouette_x, silhouette_y, silhouette_width, silhouette_height)
            
            # Audio bars on right (2/3 width)
            audio_x = self.conv_x + silhouette_width + 20
            audio_y = top_section_y + 20
            audio_width = self.conv_width - silhouette_width - 30
            audio_height = self.top_section_height - 40
            self._draw_audio_bars(screen, audio_x, audio_y, audio_width, audio_height)
            
            # Title bar
            title_bar_y = top_section_y + self.top_section_height
            title_bar = pygame.Rect(
                self.conv_x, title_bar_y,
                self.conv_width, 30
            )
            pygame.draw.rect(screen, (60, 60, 60), title_bar)
            
            # Caller name in title
            font_small = pygame.font.Font(None, 18)
            title_text = font_small.render(f"Call with {self.active_call.caller_name}", True, (255, 255, 255))
            screen.blit(title_text, (self.conv_x + 10, title_bar_y + 8))
            
            # Call duration indicator
            if self.active_call.start_time:
                elapsed = time.time() - self.active_call.start_time
                remaining = max(0, self.active_call.conversation_duration - elapsed)
                duration_text = font_small.render(f"{remaining:.1f}s", True, (150, 150, 150))
                screen.blit(duration_text, (self.conv_x + self.conv_width - 50, title_bar_y + 8))
            
            # Content area (below title bar)
            content_y = title_bar_y + 30  # Right below title bar
            content_height = self.conv_height - self.top_section_height - 30  # Remaining height
            
            # Draw content area background for visibility
            content_rect = pygame.Rect(self.conv_x, content_y, self.conv_width, content_height)
            pygame.draw.rect(screen, (35, 35, 35), content_rect)  # Slightly lighter than window bg
            
            # Message display
            font_conv = pygame.font.Font(None, 16)
            font_speaker = pygame.font.Font(None, 14)
            max_width = self.conv_width - 30  # Leave padding
            
            # Get all messages to display
            messages_to_show = []
            current_message = self.active_call.get_current_message()
            
            # Add completed messages
            completed_messages = self.active_call.get_all_completed_messages()
            for msg in completed_messages:
                messages_to_show.append({
                    "speaker": msg["speaker"],
                    "text": msg["text"]
                })
            
            # Add current message if it exists and is not already in completed messages
            # (to avoid duplicate when message just completed)
            if current_message and current_message.get("text"):
                # If the current message is complete, it's already in completed_messages
                # so we don't need to add it again
                if not self.active_call.message_complete:
                    messages_to_show.append(current_message)
            
            # Calculate total height needed for all messages
            line_height = 20
            message_spacing = 25
            total_height = 0
            message_heights = []  # Store height of each message for scrolling
            
            for message in messages_to_show:
                if not message:
                    continue
                
                speaker = message.get("speaker", "caller")
                text = message.get("text", "")
                
                # Skip empty messages in height calculation
                if not text:
                    continue
                
                # Wrap text to calculate height
                words = text.split(' ')
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    test_surface = font_conv.render(test_line, True, (255, 255, 255))
                    if test_surface.get_width() <= max_width - 70:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                message_height = (len(lines) * line_height) + message_spacing
                message_heights.append(message_height)
                total_height += message_height
            
            # Calculate scroll offset: if messages exceed content area, scroll up
            # so newest message is always at the bottom
            scroll_offset = 0
            if total_height > content_height - 20:  # 20px padding
                scroll_offset = total_height - (content_height - 20)
            
            # Draw messages from top to bottom, starting with scroll offset
            message_y = content_y + 10 - int(scroll_offset)
            message_index = 0
            
            for message in messages_to_show:
                if not message:
                    continue
                
                speaker = message.get("speaker", "caller")
                text = message.get("text", "")
                
                # Skip empty messages
                if not text:
                    continue
                
                # Get height for this message
                message_height = message_heights[message_index] if message_index < len(message_heights) else 50
                message_index += 1
                
                # Skip if this message is above the visible area
                if message_y + message_height < content_y:
                    message_y += message_height
                    continue
                
                # Don't draw if below visible area
                if message_y > content_y + content_height:
                    break
                
                # Determine color based on speaker
                if speaker == "caller":
                    speaker_color = (150, 200, 255)  # Light blue for caller
                    text_color = (220, 220, 220)
                else:
                    speaker_color = (150, 255, 150)  # Light green for player
                    text_color = (255, 255, 255)
                
                # Draw speaker label
                speaker_label = self.active_call.caller_name if speaker == "caller" else "You"
                speaker_surface = font_speaker.render(speaker_label + ":", True, speaker_color)
                
                # Only draw if within visible bounds
                if message_y >= content_y - 20:
                    screen.blit(speaker_surface, (self.conv_x + 10, message_y))
                
                # Wrap text
                words = text.split(' ')
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    test_surface = font_conv.render(test_line, True, text_color)
                    if test_surface.get_width() <= max_width - 70:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                # Draw text lines (only if within visible bounds)
                for i, line in enumerate(lines):
                    line_y = message_y + i * line_height
                    if line_y >= content_y - 20 and line_y <= content_y + content_height:
                        line_surface = font_conv.render(line, True, text_color)
                        screen.blit(line_surface, (self.conv_x + 70, line_y))
                
                # Add typing cursor for current message
                is_current = (current_message and 
                             message.get("speaker") == current_message.get("speaker") and
                             len(message.get("text", "")) > 0 and
                             message.get("text", "").startswith(current_message.get("text", "")))
                if is_current and not self.active_call.message_complete:
                    cursor_x = self.conv_x + 70
                    if lines:
                        last_line = lines[-1]
                        last_line_surface = font_conv.render(last_line, True, text_color)
                        cursor_x += last_line_surface.get_width()
                    else:
                        cursor_x += font_speaker.render(speaker_label + ":", True, speaker_color).get_width()
                    
                    cursor_y = message_y + (len(lines) - 1) * line_height if lines else message_y
                    if cursor_y >= content_y - 20 and cursor_y <= content_y + content_height:
                        if int(time.time() * 2) % 2 == 0:
                            pygame.draw.line(screen, text_color,
                                           (cursor_x, cursor_y),
                                           (cursor_x, cursor_y + 14), 2)
                
                # Move down for next message
                message_y += message_height
