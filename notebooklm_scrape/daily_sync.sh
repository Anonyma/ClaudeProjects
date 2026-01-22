#!/bin/bash
# NotebookLM Daily Sync Pipeline
# Run this manually or via cron/launchd

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment
export $(grep -v '^#' ../.env | xargs)

echo "========================================"
echo "NotebookLM Daily Sync - $(date)"
echo "========================================"

# Step 1: Sync new content from NotebookLM
echo -e "\n[1/5] Syncing from NotebookLM..."
python playwright_sync.py

# Step 2: Transcribe any new audio files
echo -e "\n[2/5] Transcribing new audio..."
python transcribe_optimized.py

# Step 3: Upload transcripts to Supabase
echo -e "\n[3/5] Uploading transcripts..."
python upload_transcripts.py

# Step 4: Generate summaries and quizzes
echo -e "\n[4/5] Generating study materials..."
python generate_study_materials.py

# Step 5: Export to markdown
echo -e "\n[5/5] Exporting to markdown..."
python export_study_materials.py

echo -e "\n========================================"
echo "Sync complete! $(date)"
echo "========================================"
