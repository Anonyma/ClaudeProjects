#!/bin/bash
# Life Management System - Setup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛠️  Life Management System Setup"
echo "================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Dependencies installed"
echo ""

# Check for Telegram bot token
if [ -z "$LIFE_BOT_TOKEN" ]; then
    echo "⚠️  LIFE_BOT_TOKEN not set"
    echo ""
    echo "To create your bot:"
    echo "1. Message @BotFather on Telegram"
    echo "2. Send /newbot"
    echo "3. Name it something like 'Z Life Manager'"
    echo "4. Copy the token"
    echo ""
    echo "Then add to your shell profile (~/.zshrc or ~/.bashrc):"
    echo "  export LIFE_BOT_TOKEN='your-token-here'"
    echo ""
else
    echo "✅ LIFE_BOT_TOKEN is set"
fi

# Check for Supabase key
if [ -z "$SUPABASE_KEY" ]; then
    echo "⚠️  SUPABASE_KEY not set (bot will use local cache)"
    echo ""
    echo "To connect Supabase, add to your shell profile:"
    echo "  export SUPABASE_KEY='your-anon-key'"
    echo ""
else
    echo "✅ SUPABASE_KEY is set"
fi

# Create data directories
mkdir -p data logs

echo ""
echo "================================"
echo "Setup complete!"
echo ""
echo "To run the bot:"
echo "  cd $SCRIPT_DIR"
echo "  source venv/bin/activate"
echo "  python telegram_bot.py"
echo ""
echo "Or use the run script:"
echo "  ./run.sh"
echo ""
