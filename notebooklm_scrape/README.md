# NotebookLM Study System

Automated scraping, transcription, and study material generation for NotebookLM.

## What's in Supabase

| Table | Records | Description |
|-------|---------|-------------|
| `notebooklm_notebooks` | 27 | Notebook metadata |
| `notebooklm_assets` | 22 | Audio overviews, quizzes, flashcards |
| `notebooklm_transcripts` | 6 | Full text transcripts |
| `notebooklm_summaries` | 12 | AI-generated summaries (standard + TLDR) |
| `notebooklm_quizzes` | 6 | 54 quiz questions total |

## Hands-Free Phone Workflow

### Option 1: Claude Mobile App (Simplest)

1. **Sync study materials to your phone:**
   ```bash
   # Copy to iCloud
   cp -r study_materials ~/Library/Mobile\ Documents/com~apple~CloudDocs/NotebookLM/
   ```

2. **In Claude mobile app:**
   - Share the `ALL_QUIZZES_VOICE.md` file
   - Say: "Quiz me on Art Deco" or "Give me a random question"
   - Answer verbally
   - Say: "Check my answer"

### Option 2: Query Supabase Directly

Since your data is in Supabase, you can query it from anywhere:

```python
# Get a random quiz question
from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_KEY)

quiz = client.table("notebooklm_quizzes").select(
    "questions, notebooklm_assets(asset_title)"
).execute()

# Quiz yourself!
import random
q = random.choice(quiz.data[0]['questions'])
print(f"Q: {q['question']}")
```

### Option 3: Siri Shortcuts (Future)

Create a Shortcut that:
1. Calls Supabase REST API
2. Gets a random question
3. Speaks it aloud
4. Records your answer
5. Checks if correct

## Automation: Daily Sync with Playwright

### First-Time Setup

```bash
# 1. Install Playwright
pip install playwright
playwright install chromium

# 2. Login to NotebookLM (one-time, saves session)
python playwright_sync.py --login
# → Browser opens, login to Google, press Enter when done
```

### How It Works

1. **Persistent browser profile** - Saves your Google login in `.playwright_profile/`
2. **Incremental sync** - Compares NotebookLM to Supabase, only downloads NEW audio
3. **Headless mode** - Runs invisibly after initial login
4. **Full pipeline** - Download → Transcribe → Summarize → Quiz → Export

### Manual Sync

```bash
# Run full pipeline manually
./daily_sync.sh

# Or step by step:
python playwright_sync.py          # Sync new content
python transcribe_optimized.py     # Transcribe audio
python upload_transcripts.py       # Upload to Supabase
python generate_study_materials.py # Generate summaries/quizzes
python export_study_materials.py   # Export markdown
```

### Automatic Daily Sync (macOS)

```bash
# Install the launch agent (runs daily at 6 AM)
cp com.notebooklm.sync.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.notebooklm.sync.plist

# Check status
launchctl list | grep notebooklm

# View logs
tail -f logs/sync.log

# Uninstall
launchctl unload ~/Library/LaunchAgents/com.notebooklm.sync.plist
```

### Sync Options

```bash
# Sync everything (headless)
python playwright_sync.py

# Sync with visible browser (debugging)
python playwright_sync.py --visible

# Sync specific notebook only
python playwright_sync.py --notebook "Work, Wealth, and Automation"

# Re-login if session expired
python playwright_sync.py --login
```

## File Structure

```
notebooklm_scrape/
├── notebooks.json          # Scraped notebook metadata
├── assets.json             # Scraped asset metadata
├── notebooklm-audio/       # Downloaded audio files (.m4a)
│   ├── *.m4a               # Audio files
│   └── *.txt               # Transcripts
├── study_materials/        # Exported study materials
│   ├── *_summary.md        # Individual summaries
│   ├── *_quiz.md           # Individual quizzes
│   └── ALL_QUIZZES_VOICE.md # Combined for voice study
├── upload_to_supabase.py   # Upload notebooks/assets
├── upload_transcripts.py   # Upload transcripts
├── transcribe_optimized.py # Whisper transcription (1.5x speedup)
├── generate_study_materials.py # Create summaries + quizzes
└── export_study_materials.py   # Export to markdown
```

## Costs

| Service | Usage | Cost |
|---------|-------|------|
| Whisper transcription | 3 hours @ 1.5x speedup | ~$0.72 |
| GPT-4o-mini (summaries/quizzes) | ~50k tokens | ~$0.05 |
| Supabase | Free tier | $0 |
| **Total** | | **~$0.77** |

## Quick Commands

```bash
# Transcribe new audio files
python transcribe_optimized.py

# Upload everything to Supabase
python upload_to_supabase.py && python upload_transcripts.py

# Generate summaries and quizzes
python generate_study_materials.py

# Export for phone use
python export_study_materials.py
```
