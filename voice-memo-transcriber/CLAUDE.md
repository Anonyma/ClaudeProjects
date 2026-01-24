# Voice Memo Transcriber

Local-first, privacy-preserving voice memo transcription with multi-machine support.

Supports:
- **Mac (local)**: MLX Whisper on Apple Silicon
- **ASUS (GPU)**: faster-whisper on NVIDIA RTX 2060
- **Windows**: faster-whisper (CPU/GPU)

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
├── CLAUDE.md              # This file
├── requirements.txt       # Mac dependencies (MLX)
├── requirements-linux.txt # Linux/ASUS dependencies (faster-whisper + CUDA)
├── requirements-windows.txt # Windows dependencies
├── config.json            # Backend configuration
├── server.py              # HTTP server (MLX or faster-whisper)
├── .env                   # Symlink to parent .env
├── scripts/
│   ├── transcribe.py          # Local transcription (MLX/OpenAI)
│   ├── transcribe_remote.py   # Remote transcription orchestrator
│   ├── preprocess.py          # FFmpeg silence removal + compression
│   ├── sync_to_supabase.py    # Database sync utilities
│   └── batch_process.py       # Batch processing from inbox
├── setup/
│   ├── asus-setup.sh          # ASUS (Linux) setup script
│   └── windows-setup.ps1      # Windows setup script
├── dashboard/
│   └── index.html         # Web dashboard with backend selector
├── audio/
│   ├── inbox/             # Drop files here
│   └── completed/         # After transcription
└── transcripts/           # .txt output files
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

### Remote Transcription
```bash
# Auto-select best available backend
python3 scripts/transcribe_remote.py audio/memo.m4a

# Use specific backend
python3 scripts/transcribe_remote.py audio/memo.m4a --backend asus
python3 scripts/transcribe_remote.py audio/memo.m4a --backend windows
python3 scripts/transcribe_remote.py audio/memo.m4a --backend local

# Check backend status
python3 scripts/transcribe_remote.py --status

# Batch process with auto selection
python3 scripts/transcribe_remote.py audio/inbox/*.m4a
```

### Start Server
```bash
# Mac (local)
python3 server.py --port 5111

# ASUS (run on ASUS machine)
source ~/whisper-env/bin/activate
python server.py --host 0.0.0.0 --port 5111

# Windows (run on Windows machine)
C:\whisper-env\Scripts\Activate.ps1
python server.py --host 0.0.0.0 --port 5112
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

### Mac (Orchestrator)
- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.10+
- FFmpeg (`brew install ffmpeg`)
- ~8GB free disk space for models (downloaded on first use)

### ASUS (GPU Compute)
- KDE Neon / Ubuntu Linux
- NVIDIA GPU with CUDA (RTX 2060 or newer)
- Python 3.10+
- FFmpeg
- SSH server enabled

### Windows (Secondary Compute)
- Windows 10/11
- OpenSSH Server enabled
- Python 3.10+
- FFmpeg

## Cost Comparison

| Method | Cost | Privacy |
|--------|------|---------|
| MLX Whisper (local) | Free | Full privacy |
| OpenAI API | ~$0.36/hour | Data sent to cloud |

## Remote Setup

### 1. ASUS Setup (Run on ASUS)
```bash
# Copy and run the setup script
bash setup/asus-setup.sh
```

### 2. Windows Setup (Run on Windows as Admin)
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup\windows-setup.ps1
```

### 3. Mac SSH Configuration
Add to `~/.ssh/config`:
```
Host asus
    HostName 192.168.x.x  # ASUS IP
    User username

Host windows
    HostName 192.168.x.y  # Windows IP
    User username
```

Copy SSH keys:
```bash
ssh-keygen -t ed25519 -C "mac-to-remote"
ssh-copy-id asus
ssh-copy-id windows
```

### 4. Verify Setup
```bash
# Check all backends
python3 scripts/transcribe_remote.py --status

# Test SSH connections
ssh asus nvidia-smi  # Should show GPU info
ssh windows echo ok  # Should print "ok"
```

## Tips

- **Large files**: Always use `--preprocess` (enabled by default) for 30%+ speedup
- **Quality vs speed**: Use `large-v3` for final transcripts, `small` for quick drafts
- **Long sessions**: Use `batch_process.py` with `--status` to monitor progress
- **Privacy sensitive**: Keep `--openai` flag off (default)
- **GPU transcription**: Use ASUS backend for fastest processing (~20x real-time)
- **Remote fallback**: System auto-falls back to available backends if primary is offline
