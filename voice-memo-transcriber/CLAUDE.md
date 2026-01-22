# Voice Memo Transcriber

Local-first, privacy-preserving voice memo transcription using MLX Whisper on Apple Silicon.

## Quick Start

```bash
# Install dependencies
cd /Users/z/Desktop/PersonalProjects/ClaudeProjects/voice-memo-transcriber
pip3 install -r requirements.txt

# Transcribe a single file
python3 scripts/transcribe.py audio/inbox/memo.m4a

# Open dashboard
open dashboard/index.html
```

## Project Structure

```
voice-memo-transcriber/
├── CLAUDE.md           # This file
├── requirements.txt    # Python dependencies
├── .env               # Symlink to parent .env
├── scripts/
│   ├── transcribe.py      # Main transcription script (MLX/OpenAI)
│   ├── preprocess.py      # FFmpeg silence removal + compression
│   ├── sync_to_supabase.py # Database sync utilities
│   └── batch_process.py   # Batch processing from inbox
├── dashboard/
│   └── index.html     # Web dashboard (single file)
├── audio/
│   ├── inbox/         # Drop files here
│   └── completed/     # After transcription
└── transcripts/       # .txt output files
```

## Commands

### Transcribe Single File
```bash
# Basic transcription (uses MLX Whisper large-v3)
python3 scripts/transcribe.py audio/inbox/memo.m4a

# With options
python3 scripts/transcribe.py memo.m4a --model medium --no-preprocess --move

# Estimate time/cost without transcribing
python3 scripts/transcribe.py memo.m4a --estimate

# Use OpenAI API instead of local
python3 scripts/transcribe.py memo.m4a --openai
```

### Batch Processing
```bash
# Check queue status
python3 scripts/batch_process.py --status

# Process all pending files in inbox
python3 scripts/batch_process.py

# Limit to N files
python3 scripts/batch_process.py --limit 3

# Add files to queue without processing
python3 scripts/batch_process.py --add-only
```

### Database Utilities
```bash
# View statistics
python3 scripts/sync_to_supabase.py --stats

# List all memos
python3 scripts/sync_to_supabase.py --list

# List pending memos
python3 scripts/sync_to_supabase.py --pending
```

### Preprocessing Only
```bash
# Preprocess without transcribing (silence removal + compression)
python3 scripts/preprocess.py audio/inbox/memo.m4a
```

## Model Options

| Model | Speed | Quality | Notes |
|-------|-------|---------|-------|
| `large-v3` | ~10x real-time | Best | Default, recommended |
| `large-v3-turbo` | ~14x real-time | Great | Faster alternative |
| `medium` | ~7x real-time | Good | Balanced |
| `small` | ~12x real-time | OK | Quick drafts |

For a 2-hour file:
- **large-v3**: ~8-12 minutes
- **With preprocessing**: ~4-6 minutes

## Dashboard

Open `dashboard/index.html` in a browser to:
- View all memos and their status
- Add files via drag & drop
- View/edit transcripts
- Copy transcripts to clipboard
- See time estimates
- Track processing statistics

The dashboard syncs with Supabase for persistence across devices.

## Workflow

1. **Drop file** in dashboard or `audio/inbox/` folder
2. **Run transcription** via command line
3. **View result** in dashboard or `transcripts/` folder
4. File automatically moves to `audio/completed/` (with `--move` flag)

## Database Tables

Supabase project: `ydwjzlikslebokuxzwco`

- `voice_memos`: File tracking (hash, status, duration)
- `voice_transcripts`: Transcript content (text, word count)

## Environment Variables

Uses `.env` file (symlinked from parent directory):
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase public/anon key
- `OPENAI_API_KEY`: For cloud transcription (optional)

## System Requirements

- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.10+
- FFmpeg (`brew install ffmpeg`)
- ~8GB free disk space for models (downloaded on first use)

## Cost Comparison

| Method | Cost | Privacy |
|--------|------|---------|
| MLX Whisper (local) | Free | Full privacy |
| OpenAI API | ~$0.36/hour | Data sent to cloud |

## Tips

- **Large files**: Always use `--preprocess` (enabled by default) for 30%+ speedup
- **Quality vs speed**: Use `large-v3` for final transcripts, `small` for quick drafts
- **Long sessions**: Use `batch_process.py` with `--status` to monitor progress
- **Privacy sensitive**: Keep `--openai` flag off (default)
