# Time Tracker

A cross-device time awareness app to combat time blindness. Pings you hourly, detects AFK periods, and logs everything to Supabase.

## Quick Start

### 1. Set Up Database

Run the schema in Supabase SQL Editor:
```bash
# Copy contents of supabase/schema.sql and paste into:
# https://supabase.com/dashboard/project/ydwjzlikslebokuxzwco/sql/new
```

### 2. Test Dashboard

```bash
open /Users/z/Desktop/PersonalProjects/ClaudeProjects/time-tracker/dashboard/index.html
```

Try logging an activity - it should appear in the timeline.

### 3. Run Mac App

```bash
cd /Users/z/Desktop/PersonalProjects/ClaudeProjects/time-tracker/mac-app
pip3 install -r requirements.txt
python3 app.py
```

The ⏱ icon should appear in your menu bar.

### 4. Set Up iOS (Optional)

See `ios-shortcut/README.md` for:
- Pushover setup ($4.99 one-time)
- iOS Shortcut creation
- Voice logging configuration

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Mac Menu   │     │    iOS      │     │    Web      │
│  Bar App    │     │  Shortcut   │     │  Dashboard  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
              ┌────────────▼────────────┐
              │      Supabase           │
              │  - activity_logs        │
              │  - pings                │
              │  - device_state         │
              │  - time_tracker_settings│
              └─────────────────────────┘
```

## Commands

### Mac App
```bash
# Run in foreground (for testing)
python3 mac-app/app.py

# Test AFK detection
python3 mac-app/afk_detector.py

# Test Supabase connection
python3 mac-app/supabase_client.py
```

### Auto-Start on Login
```bash
# Copy LaunchAgent (if created)
cp mac-app/com.timetracker.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.timetracker.plist
```

## Configuration

Create `.env` in project root:
```bash
# Required for iPhone push notifications
PUSHOVER_USER_KEY=your_user_key
PUSHOVER_API_TOKEN=your_app_token

# Optional overrides
AFK_THRESHOLD_SECONDS=300
PING_INTERVAL_MINUTES=60
SKIP_IF_ACTIVITY_WITHIN_MINUTES=15
```

## Database Tables

| Table | Purpose |
|-------|---------|
| `activity_logs` | All logged activities |
| `pings` | Notification state for cross-device sync |
| `device_state` | AFK tracking per device |
| `time_tracker_settings` | User preferences |

## Files

```
time-tracker/
├── CLAUDE.md              # This file
├── mac-app/
│   ├── app.py             # Menu bar app
│   ├── afk_detector.py    # IOKit idle detection
│   ├── supabase_client.py # API wrapper
│   ├── config.py          # Settings loader
│   └── requirements.txt   # Python deps
├── dashboard/
│   └── index.html         # Web dashboard PWA
├── supabase/
│   └── schema.sql         # Database setup
└── ios-shortcut/
    └── README.md          # Shortcut setup guide
```

## Features

### Implemented
- [x] Manual activity logging (Mac, Web)
- [x] AFK detection on Mac
- [x] AFK return prompts
- [x] Web dashboard with timeline
- [x] Hourly ping system
- [x] Pushover integration for iPhone
- [x] Skip ping if recent activity

### Planned
- [ ] Cross-device notification dismissal
- [ ] Screenshot capture on Mac
- [ ] Query interface ("What was I doing Tuesday?")
- [ ] Statistics and charts
- [ ] Quiet hours
- [ ] iOS native app

## Troubleshooting

### Mac app won't start
```bash
# Check rumps is installed
pip3 show rumps

# Run with verbose output
python3 -u mac-app/app.py
```

### Activities not saving
1. Check dashboard shows "connected" (green dot)
2. Run `python3 mac-app/supabase_client.py` to test connection
3. Verify tables exist in Supabase

### AFK not detecting
```bash
# Test detector directly
python3 mac-app/afk_detector.py
# Should show idle time updating in real-time
```

### Pushover not working
1. Verify keys in `.env`
2. Check Pushover app shows recent notifications
3. Test manually: `curl -X POST -d "token=XXX&user=XXX&message=test" https://api.pushover.net/1/messages.json`
