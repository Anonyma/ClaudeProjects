#!/bin/bash
# Run the Life Management Bot

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Check for token
if [ -z "$LIFE_BOT_TOKEN" ]; then
    echo "❌ LIFE_BOT_TOKEN not set"
    echo "Get a token from @BotFather and export it:"
    echo "  export LIFE_BOT_TOKEN='your-token'"
    exit 1
fi

# Run the bot
echo "🤖 Starting Life Management Bot..."
python telegram_bot.py
