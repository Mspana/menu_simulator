# Menu Simulator

A desktop game where you play as Matt Griffin, fundraising for a conference by sifting through menus. The secret: Calvelli is doing all the actual work while you click around!

## Features

- Multiple themed application windows (Inventory, FTL, Zomboid, Outlook, Messages, Slack, Discord)
- Calvelli's activity log showing all the work being done behind the scenes
- Email notifications and Outlook client with reply functionality
- Slack, Messages, and Discord notifications
- Phone call system with conversations
- Progress tracking and milestone notifications
- Discord interruptions from Calvelli
- Interactive game notifications (FTL/Zomboid circle clicking)

## Project Structure

### Core Game Files
- `game.py` - Main game entry point and game loop
- `game_state.py` - Game state management and progress tracking
- `menu.py` - Base menu window system

### Window Systems
- `themed_windows.py` - Themed application windows (Inventory, FTL, Zomboid, Outlook, Messages, Slack, Discord)
- `activity_log_window.py` - Activity log window with progress bar
- `email_view_window.py` - Email detail view window
- `reply_window.py` - Email reply composition window

### Notification Systems
- `email_notifications.py` - Email notification system
- `slack_notifications.py` - Slack notification system
- `messages_notifications.py` - Mac Messages notification system
- `discord_notifications.py` - Discord notification system
- `game_notifications.py` - FTL/Zomboid game notification system
- `milestone_notifications.py` - Progress milestone notifications

### Game Systems
- `calvelli_log.py` - Calvelli's activity logging system
- `discord_interrupt.py` - Discord interruption popups
- `outlook_email_system.py` - Outlook email management
- `phone_call.py` - Phone call system with conversations
- `progress_popup.py` - Progress increase popup animations

### Content & Data
- `messages_content.py` - Centralized content loading
- `emails.json` - Email templates and content
- `phone_calls.json` - Phone call conversations

### Other
- `ending.py` - Ending screen with stats reveal
- `requirements.txt` - Python dependencies

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the game:
```bash
python game.py
```

## Assets

Assets are stored in the `assets_pack/` directory:
- `backgrounds/` - Background images
- `menus/` - Menu screenshots (FTL, Zomboid)
- `ui/` - UI elements (buttons, icons, etc.)
- `audio_optional/` - Sound effects (optional)

## Controls

- **Tab** - Cycle through windows
- **Mouse** - Click and drag windows, interact with UI elements
- **Keyboard** - Type responses in email/Slack/Messages reply windows
- **ESC** - Exit (on ending screen)
