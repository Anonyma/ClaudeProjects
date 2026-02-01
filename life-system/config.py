"""
Configuration for Life Management System
"""
import os
from pathlib import Path

# Telegram Bot Token - get from @BotFather
TELEGRAM_BOT_TOKEN = os.environ.get("LIFE_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("LIFE_CHAT_ID", "355422856")  # Your Telegram ID

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ydwjzlikslebokuxzwco.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Google Calendar
GOOGLE_CREDENTIALS_PATH = os.environ.get(
    "GOOGLE_CREDENTIALS_PATH",
    str(Path.home() / ".config" / "life-system" / "google_credentials.json")
)
GOOGLE_TOKEN_PATH = os.environ.get(
    "GOOGLE_TOKEN_PATH",
    str(Path.home() / ".config" / "life-system" / "google_token.json")
)

# Timezone
TIMEZONE = "Europe/Vienna"  # CET

# Schedule Settings
MORNING_BRIEFING_HOUR = 9  # 9 AM CET
CHECKIN_INTERVAL_MINUTES = 60  # Hourly check-ins
EVENING_REVIEW_HOUR = 21  # 9 PM CET

# Project paths
PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
LOGS_DIR = PROJECT_DIR / "logs"

# Create directories
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Coach style weights (for message generation)
COACH_STYLE = {
    "practical": 0.60,  # "Here's a simpler alternative"
    "tough_love": 0.25,  # "You said X, you didn't do it. Why?"
    "gentle": 0.15,  # "What's making this feel hard?"
}
