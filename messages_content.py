"""
Messages and Content
Centralized content for the game including Calvelli's activities and email templates
"""

import json
import os

# Load emails from JSON file
def _load_emails():
    """Load email data from JSON file"""
    emails_file = os.path.join(os.path.dirname(__file__), "emails.json")
    try:
        with open(emails_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('regular_emails', []), data.get('congratulatory_emails', [])
    except FileNotFoundError:
        # Fallback to empty lists if file doesn't exist
        return [], []

REGULAR_EMAILS, CONGRATULATORY_EMAILS = _load_emails()

# Calvelli's activity messages (more basic and exasperated)
CALVELLI_ACTIVITIES = [
    "Calvelli did the sponsorship thing",
    "Calvelli booked the venue",
    "Calvelli sent some emails",
    "Calvelli fixed the spreadsheet again",
    "Calvelli got the speakers",
    "Calvelli handled the food",
    "Calvelli set up registration",
    "Calvelli talked to vendors",
    "Calvelli made a schedule",
    "Calvelli contacted media",
    "Calvelli got the AV stuff",
    "Calvelli did the insurance",
    "Calvelli arranged transport",
    "Calvelli finished the marketing",
    "Calvelli found more sponsors",
    "Calvelli updated the list",
    "Calvelli scheduled everything",
    "Calvelli assigned volunteers",
    "Calvelli made the packets",
    "Calvelli sorted parking",
]

# Extract senders and subjects from loaded emails for backward compatibility
REGULAR_EMAIL_SENDERS = list(set([email["sender"] for email in REGULAR_EMAILS]))
REGULAR_EMAIL_SUBJECTS = list(set([email["subject"] for email in REGULAR_EMAILS]))
