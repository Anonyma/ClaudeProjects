#!/bin/bash
# Setup script for dictation tool

set -e

echo "🔧 Setting up dictation tool..."

# Install Python dependencies
pip3 install -r requirements.txt

# For local Whisper support (optional)
read -p "Install local Whisper support? (requires ~2GB download) [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip3 install faster-whisper
fi

# macOS permissions reminder
echo ""
echo "✅ Dependencies installed!"
echo ""
echo "⚠️  IMPORTANT: macOS permissions required:"
echo "   1. System Settings → Privacy & Security → Accessibility"
echo "      → Add Terminal (or your terminal app)"
echo "   2. System Settings → Privacy & Security → Microphone"
echo "      → Add Terminal (or your terminal app)"
echo ""
echo "To run:"
echo "   python3 dictate.py           # OpenAI API"
echo "   python3 dictate.py --groq    # Groq API (faster)"
echo "   python3 dictate.py --local   # Local Whisper"
