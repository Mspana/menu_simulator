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

# Calvelli's activity messages
CALVELLI_ACTIVITIES = [
    "Calvelli secured a $5,000 sponsorship",
    "Calvelli finalized the venue booking",
    "Calvelli sent out 50 fundraising emails",
    "Calvelli updated the budget spreadsheet",
    "Calvelli confirmed 3 keynote speakers",
    "Calvelli organized the catering menu",
    "Calvelli set up the registration system",
    "Calvelli coordinated with 10 vendors",
    "Calvelli drafted the conference schedule",
    "Calvelli reached out to media partners",
    "Calvelli booked the AV equipment",
    "Calvelli confirmed the event insurance",
    "Calvelli arranged transportation logistics",
    "Calvelli finalized the marketing materials",
    "Calvelli secured 2 more sponsors",
    "Calvelli updated the attendee list",
    "Calvelli scheduled all breakout sessions",
    "Calvelli coordinated volunteer assignments",
    "Calvelli prepared the welcome packets",
    "Calvelli confirmed parking arrangements",
]

# Extract senders and subjects from loaded emails for backward compatibility
REGULAR_EMAIL_SENDERS = list(set([email["sender"] for email in REGULAR_EMAILS]))
REGULAR_EMAIL_SUBJECTS = list(set([email["subject"] for email in REGULAR_EMAILS]))
