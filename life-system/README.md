# Life Management System

A personal life management system with Telegram bot integration for daily structure, time tracking, and focus management.

## Quick Start

### 1. Create Telegram Bot
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Name it: `Z Life Manager` (or whatever you prefer)
4. Copy the token

### 2. Set Environment Variables
Add to your `~/.zshrc`:
```bash
export LIFE_BOT_TOKEN='your-telegram-bot-token'
export SUPABASE_KEY='your-supabase-anon-key'  # Optional, uses local cache otherwise
```

Reload: `source ~/.zshrc`

### 3. Run the Bot
```bash
cd /Users/z/Desktop/PersonalProjects/ClaudeProjects/life-system
./run.sh
```

## Features

### Morning Briefing (/morning)
- Calendar events (when connected)
- Year progress percentage
- Spillover tasks from yesterday
- Sets your ONE thing for the day
- Energy-based recommendations

### Hourly Check-ins
- Automatic pings every hour (10am-8pm)
- Track: on track, distracted, switched tasks, need break
- Pattern detection for distraction warnings

### Time Tracking
- `/start_task` - Start tracking
- `/stop_task` - Stop and log duration
- Historical estimates for similar tasks
- Weekly stats on estimation accuracy

### Focus Blocks
- `/focus` - Start a focus block (25/50/90/120 min)
- No interruptions during block
- Rating system after completion

### Status & Stats
- `/status` - Current task, ONE thing, check-ins
- `/stats` - Weekly time tracking summary

## CLI Interface (for testing)

```bash
source venv/bin/activate

# Morning briefing
python life_cli.py briefing

# Set ONE thing
python life_cli.py one "Build the life system bot"

# Start/stop tasks
python life_cli.py start "Deep work on bot" 60
python life_cli.py stop

# Check-in
python life_cli.py checkin

# Status
python life_cli.py status
python life_cli.py stats
```

## Database Tables (Supabase)

- `life_daily_intentions` - Daily ONE thing tracking
- `life_checkins` - Hourly check-in responses
- `life_time_entries` - Task time tracking
- `life_focus_blocks` - Focus session logs
- `life_spillover` - Tasks that got pushed
- `life_opportunities` - Income opportunities
- `life_o1_evidence` - O-1 visa evidence tracker
- `life_weekly_digests` - Weekly summary logs

## Schedule

| Time | Event |
|------|-------|
| 9:00 AM | Morning briefing |
| 10:00 AM - 8:00 PM | Hourly check-ins |
| (planned) 9:00 PM | Evening review |

## Configuration

Edit `config.py` to adjust:
- Timezone (default: Europe/Vienna)
- Morning briefing hour
- Check-in intervals
- Coach style weights

## Files

```
life-system/
├── telegram_bot.py      # Main Telegram bot
├── daily_briefing.py    # Morning message generator
├── supabase_client.py   # Database operations
├── life_cli.py          # CLI for testing
├── config.py            # Configuration
├── setup.sh             # Initial setup
├── run.sh               # Start the bot
└── supabase_schema.sql  # Database schema
```
