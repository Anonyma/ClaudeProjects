#!/bin/bash
# Reminder: Continue Writing Challenge & Voice Studio project development
# Scheduled for 10am - Jan 24, 2026

# Send via Pushover email
echo "Continue Writing Challenge & Voice Studio project development with Claude Code. Session was about adding Supabase sync and Netlify deployment.

Quick access:
- launch write (Writing Challenge)
- launch speak (Voice Studio)

Project dir: /Users/z/Desktop/PersonalProjects/ClaudeProjects" | mail -s "Claude Projects Reminder" 6b9ekxyx2w@pomail.net

# Clean up after sending
launchctl unload ~/Library/LaunchAgents/com.claude.reminder.writingproject.plist 2>/dev/null
rm -f ~/Library/LaunchAgents/com.claude.reminder.writingproject.plist
rm -f "$0"
