#!/bin/bash
# Launch dictation app - call this from Raycast, Alfred, or a global shortcut

# Configuration - change these as needed
BACKEND="groq"  # Options: openai, groq, local

# Paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DICTATE_PY="$SCRIPT_DIR/dictate.py"

# Check if already running
if pgrep -f "python.*dictate.py" > /dev/null; then
    # Already running - bring to foreground or just exit
    echo "Dictation app already running"
    exit 0
fi

# Source API keys from shell profile
if [ -f ~/.zshrc ]; then
    source ~/.zshrc 2>/dev/null
elif [ -f ~/.bashrc ]; then
    source ~/.bashrc 2>/dev/null
fi

# Run the app
case "$BACKEND" in
    groq)
        python3 "$DICTATE_PY" --groq &
        ;;
    local)
        python3 "$DICTATE_PY" --local &
        ;;
    *)
        python3 "$DICTATE_PY" &
        ;;
esac

disown
