#!/bin/bash
# Reminder: Continue Writing Challenge & Voice Studio project development
# Scheduled for 10am - Jan 24, 2026

cd /Users/z/Desktop/PersonalProjects/ClaudeProjects

# Send via Python (more reliable than mail command)
python3 << 'PYTHON'
import smtplib
from email.mime.text import MIMEText
import subprocess

message = """Continue Writing Challenge & Voice Studio project development with Claude Code.

Next steps:
- Add Supabase sync for cross-device persistence
- Deploy to Netlify for mobile access

Quick access:
  launch write (Writing Challenge)
  launch speak (Voice Studio)

Project dir: /Users/z/Desktop/PersonalProjects/ClaudeProjects
"""

# Try Pushover email (works without authentication via local sendmail)
try:
    # Use osascript to show notification as fallback
    subprocess.run([
        'osascript', '-e',
        'display notification "Continue Writing & Voice Studio project with Claude Code. Run: launch write" with title "Claude Projects Reminder"'
    ])
    print("macOS notification sent")
except Exception as e:
    print(f"Notification failed: {e}")

# Also try terminal-notifier if available
try:
    subprocess.run([
        'terminal-notifier',
        '-title', 'Claude Projects Reminder',
        '-message', 'Continue Writing & Voice Studio project. Run: launch write',
        '-sound', 'default'
    ], check=False)
except:
    pass

PYTHON

# Also open the TODO file
open /Users/z/Desktop/PersonalProjects/ClaudeProjects/reminders/TODO.md

# Clean up after sending
launchctl unload ~/Library/LaunchAgents/com.claude.reminder.writingproject.plist 2>/dev/null
rm -f ~/Library/LaunchAgents/com.claude.reminder.writingproject.plist
