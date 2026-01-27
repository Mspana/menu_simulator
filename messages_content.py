"""
Messages and Content
Centralized content for the game including Calvelli's activities and email templates
"""

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

# Congratulatory emails about Calvelli's work
CONGRATULATORY_EMAILS = [
    {
        "sender": "michael miske <michael.miske@conference.org>",
        "subject": "Calvelli is doing amazing work!",
        "message": "Hey Matt, just wanted to say that Calvelli has been absolutely crushing it with the conference planning. The venue booking was handled perfectly, and the sponsor outreach has been incredible. You're lucky to have such a dedicated team member!",
        "responses": [
            "Thanks! Yes, Calvelli is great.",
            "I'll let them know you said that.",
            "We're making good progress!"
        ]
    },
    {
        "sender": "sponsors@conference.org",
        "subject": "Re: Amazing fundraising progress",
        "message": "Matt, we've been so impressed with how quickly things are moving. Calvelli's work on securing sponsorships has been outstanding. The conference is really coming together thanks to their efforts!",
        "responses": [
            "Thank you for the kind words!",
            "Calvelli has been working hard.",
            "We appreciate your support."
        ]
    },
    {
        "sender": "venue@conference.org",
        "subject": "Venue coordination going smoothly",
        "message": "Hi Matt, just wanted to update you that everything with the venue is set. Calvelli has been incredibly organized and responsive. It's been a pleasure working with them on this!",
        "responses": [
            "Great to hear!",
            "Calvelli is very organized.",
            "Thanks for the update."
        ]
    },
    {
        "sender": "media@conference.org",
        "subject": "Media partnerships secured",
        "message": "Matt, Calvelli reached out to us and we're thrilled to partner on the conference. Their professionalism and attention to detail really stood out. Great work!",
        "responses": [
            "Thank you!",
            "Calvelli is very professional.",
            "We're excited to work with you."
        ]
    },
    {
        "sender": "finance@conference.org",
        "subject": "Budget looking great",
        "message": "Hey Matt, the budget spreadsheet Calvelli put together is excellent. Everything is well-organized and we're on track. They've really thought of everything!",
        "responses": [
            "Thanks for the feedback!",
            "Calvelli is very thorough.",
            "Glad everything looks good."
        ]
    },
    {
        "sender": "volunteers@conference.org",
        "subject": "Volunteer coordination",
        "message": "Matt, Calvelli has done an amazing job coordinating all the volunteers. The schedule is clear, assignments are well-organized, and everyone knows what they're doing. Really impressive work!",
        "responses": [
            "That's great to hear!",
            "Calvelli is very organized.",
            "Thanks for letting me know."
        ]
    },
    {
        "sender": "seong-ah@conference.org",
        "subject": "Calvelli is a rockstar!",
        "message": "Hey Matt! Just wanted to say that Calvelli has been doing incredible work. The conference planning is going so smoothly because of them. You should be proud!",
        "responses": [
            "I am! Calvelli is great.",
            "Thanks for saying that.",
            "We're lucky to have them."
        ]
    },
    {
        "sender": "jar@conference.org",
        "subject": "Conference coming together nicely",
        "message": "Matt, everything is looking great. Calvelli's attention to detail on the catering and AV equipment has been spot-on. The conference is going to be fantastic!",
        "responses": [
            "Thanks!",
            "Calvelli pays attention to details.",
            "We're excited too!"
        ]
    },
    {
        "sender": "halle@conference.org",
        "subject": "Schedule looks perfect",
        "message": "Hi Matt, the schedule Calvelli put together is really well thought out. All the breakout sessions are properly coordinated. They've done an excellent job!",
        "responses": [
            "Thank you!",
            "Calvelli worked hard on that.",
            "Glad you like it."
        ]
    },
    {
        "sender": "calvelli@conference.org",
        "subject": "Just checking in",
        "message": "Hey Matt, just wanted to make sure everything is going well on your end. I've been handling the conference planning and wanted to see if you need anything from me. Let me know!",
        "responses": [
            "Everything looks great, thanks!",
            "You're doing amazing work.",
            "Keep it up!"
        ]
    },
]

# Regular email senders (for non-congratulatory emails)
REGULAR_EMAIL_SENDERS = [
    "conference@org.com",
    "sponsors@conference.org",
    "finance@conference.org",
    "venue@conference.org",
    "media@conference.org",
    "volunteers@conference.org",
    "michael miske <michael.miske@conference.org>",
    "seong-ah@conference.org",
    "jar@conference.org",
    "halle@conference.org",
]

# Regular email subjects (for non-congratulatory emails)
REGULAR_EMAIL_SUBJECTS = [
    "Conference Planning Update",
    "Budget Review Needed",
    "Sponsor Meeting Tomorrow",
    "Re: Fundraising Progress",
    "Venue Confirmation",
    "Media Partnership Opportunity",
    "Volunteer Schedule",
    "Registration Update",
    "Catering Menu Finalized",
    "AV Equipment Confirmed",
    "Parking Arrangements",
    "Schedule Changes",
    "Quick Question",
    "Follow-up Required",
    "Action Items",
]
