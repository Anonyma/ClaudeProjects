#!/bin/bash
# Start the NotebookLM batch generation on CandyPop in a tmux session
# Run this from Mac: bash start-on-candypop.sh

REMOTE="CandyPop"
SESSION="nlm-batch"
BATCH_DIR="~/Projects/notebooklm/batch-2026-02"

echo "=== NotebookLM Batch Generation ==="
echo "Deploying files to CandyPop..."

# Create directories on CandyPop
ssh "$REMOTE" "mkdir -p ~/Projects/notebooklm/batch-2026-02/sources"

# Copy batch files to CandyPop
scp -r /Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape/batch-2026-02/* \
    "$REMOTE:~/Projects/notebooklm/batch-2026-02/"

echo "Files deployed."
echo ""
echo "Starting Claude Code agent in tmux session '$SESSION' on CandyPop..."

# Create tmux session with proper PATH and start Claude
ssh "$REMOTE" "tmux kill-session -t $SESSION 2>/dev/null; tmux new-session -d -s $SESSION -c ~/Projects/notebooklm"

# Set PATH in tmux session first
ssh "$REMOTE" "tmux send-keys -t $SESSION 'export PATH=\$HOME/.local/bin:\$HOME/bin:\$PATH' Enter"
sleep 1

# Send the claude command
ssh "$REMOTE" "tmux send-keys -t $SESSION 'claude -p \"Read batch-2026-02/TASK.md and batch-2026-02/topics.json. Execute the full batch content generation pipeline. Start with Phase 1 (source research for all 8 topics). Report status via report-status at every phase transition. Update batch-2026-02/progress.json after each step. If Playwright login is expired, report blocked and stop. Begin now.\" --dangerously-skip-permissions 2>&1 | tee batch-2026-02/agent.log' Enter"

echo ""
echo "=== Agent started! ==="
echo ""
echo "Monitor from Mac:"
echo "  bash /Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape/batch-2026-02/monitor.sh"
echo "  bash /Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape/batch-2026-02/monitor.sh --watch"
echo ""
echo "SSH into the session:"
echo "  ssh CandyPop -t 'tmux attach -t $SESSION'"
echo ""
echo "Check agent-hub:"
echo "  agents | grep nlm"
echo ""
echo "Telegram notifications will fire on: blocked, completed, error"
