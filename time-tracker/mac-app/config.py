#!/usr/bin/env python3
"""
Configuration loader for Time Tracker Mac app.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ydwjzlikslebokuxzwco.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU')

# Pushover configuration (optional - for sending pings)
PUSHOVER_USER_KEY = os.getenv('PUSHOVER_USER_KEY', '')
PUSHOVER_API_TOKEN = os.getenv('PUSHOVER_API_TOKEN', '')

# App settings
AFK_THRESHOLD_SECONDS = int(os.getenv('AFK_THRESHOLD_SECONDS', 300))  # 5 minutes
PING_INTERVAL_MINUTES = int(os.getenv('PING_INTERVAL_MINUTES', 60))
SKIP_IF_ACTIVITY_WITHIN_MINUTES = int(os.getenv('SKIP_IF_ACTIVITY_WITHIN_MINUTES', 15))
HEARTBEAT_INTERVAL_SECONDS = int(os.getenv('HEARTBEAT_INTERVAL_SECONDS', 60))
