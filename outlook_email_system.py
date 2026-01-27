"""
Outlook Email System
Periodically adds emails to the Outlook window
"""

import time
import random
from messages_content import CONGRATULATORY_EMAILS

class OutlookEmailSystem:
    """Manages periodic email delivery to Outlook"""
    
    def __init__(self, outlook_window):
        self.outlook_window = outlook_window
        self.last_email_time = time.time()
        self.email_interval = random.uniform(10.0, 20.0)  # 10-20 seconds between emails
        self.congratulatory_chance = 0.3  # 30% chance for congratulatory email
        self.congratulatory_sent = set()  # Track sent congratulatory emails
    
    def update(self):
        """Update email delivery system"""
        current_time = time.time()
        time_since_last = current_time - self.last_email_time
        
        if time_since_last >= self.email_interval:
            # Decide if this should be a congratulatory email
            if (random.random() < self.congratulatory_chance and 
                len(self.congratulatory_sent) < len(CONGRATULATORY_EMAILS)):
                # Send a congratulatory email
                self._send_congratulatory_email(current_time)
            else:
                # Send a regular email
                self.outlook_window._add_email(current_time)
            
            self.last_email_time = current_time
            self.email_interval = random.uniform(10.0, 20.0)  # Next email in 10-20s
    
    def _send_congratulatory_email(self, timestamp):
        """Send a congratulatory email about Calvelli's work"""
        # Get an unsent congratulatory email
        available = [e for e in CONGRATULATORY_EMAILS if id(e) not in self.congratulatory_sent]
        if not available:
            # All sent, reset and start over
            self.congratulatory_sent.clear()
            available = CONGRATULATORY_EMAILS
        
        email_template = random.choice(available)
        self.congratulatory_sent.add(id(email_template))
        
        # Add the congratulatory email to Outlook
        self.outlook_window._add_congratulatory_email(email_template, timestamp)
