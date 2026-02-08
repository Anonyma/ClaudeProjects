# CandyPop NotebookLM Automation Setup

**Date:** 2026-02-06
**Status:** Blocked

## Goal
Set up NotebookLM browser automation on CandyPop so Gemini can generate deep dives and report back to Claude for transcription.

## Completed

### On NotebookLM (via Mac Claude-in-Chrome)
- Created **Biotech Breakthroughs 2023-2026: CRISPR, Gene Therapy & AI** notebook
- Added 20 sources covering: CRISPR trials, Casgevy FDA approval, AlphaFold Nobel Prize, David Liu base editing, gene therapy trends
- Queued default audio overview generation
- Indian religions deep dive was generating (from earlier session)

### On CandyPop
- Installed pip for user (`~/.local/bin/pip`)
- Installed Python packages: `playwright`, `openai`, `supabase`, `selenium`, `python-dotenv`, `webdriver-manager`
- Installed Playwright Chromium browser (`~/.cache/ms-playwright/`)
- Copied all NotebookLM scripts to `~/Projects/notebooklm/`
- Copied `.env` with API keys
- Created `GEMINI.md` instructions for Gemini
- Created `generate_deep_dive.py` - CLI tool for generating deep dives
- Created `setup_login.sh` - helper for Google login
- Created `run_deep_dive.sh` - wrapper with correct PATH

## Blocked On

**Browser automation cannot authenticate with Google because:**

1. **Playwright's Chromium flagged as insecure** - Google blocks login from "Chrome for Testing"
2. **System Chrome profile locked** - User already has Chrome running on CandyPop
3. **Can't share profile** - Chrome only allows one instance per profile

## Options to Unblock

| Option | Pros | Cons |
|--------|------|------|
| Use Claude Code on CandyPop | Already has browser MCP working | Need to coordinate two Claude sessions |
| Keep browser work on Mac | Already working | Doesn't achieve CandyPop automation goal |
| Close Chrome on CandyPop | Selenium/Playwright can use logged-in profile | User loses their browser session |

## Files on CandyPop

```
~/Projects/notebooklm/
├── .env                      # API keys (SUPABASE, OPENAI)
├── .playwright_profile/      # Needs valid Google session
├── notebooklm-audio/         # Output directory
├── CLAUDE.md                 # Original instructions
├── GEMINI.md                 # Gemini-specific instructions
├── generate_deep_dive.py     # Main CLI tool
├── setup_login.sh            # Login helper
├── run_deep_dive.sh          # Wrapper script
├── transcribe_optimized.py   # Transcription
├── upload_to_supabase.py     # Database sync
└── [other scripts...]
```

## Commands for Future Use

```bash
# On CandyPop - generate deep dive (once login works)
export DISPLAY=:1
export PYTHONPATH=~/.local/lib/python3.12/site-packages:$PYTHONPATH
cd ~/Projects/notebooklm
python3 generate_deep_dive.py -n "Notebook Name" -p "Focus prompt" -l long

# Check status
cat ~/Projects/notebooklm/generation_status.json
```

## Next Steps
1. User decides on approach (see options above)
2. Complete browser authentication
3. Test full workflow: Gemini generates → reports status → Claude transcribes

## Linear
- Z-10: Created Biotech notebook (Done)
- Z-11: CandyPop setup (needs creation - Linear token expired)
