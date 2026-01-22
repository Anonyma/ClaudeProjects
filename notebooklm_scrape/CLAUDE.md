# NotebookLM Study System

## Overview
Automated system for scraping NotebookLM audio overviews, transcribing them, generating study materials (summaries + quizzes), and serving them via a web app.

## Architecture

```
User's NotebookLM Account
         ↓ (Playwright automation)
   Audio Downloads (.m4a)
         ↓ (OpenAI Whisper)
     Transcripts (.txt)
         ↓ (GPT-4o-mini)
  Summaries + Quizzes
         ↓
      Supabase DB
         ↓
   Study Web App (Netlify)
```

## Supabase Configuration

- **Project ID**: `ydwjzlikslebokuxzwco`
- **URL**: `https://ydwjzlikslebokuxzwco.supabase.co`
- **Anon Key** (legacy JWT format): `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU`

### Database Tables
| Table | Purpose |
|-------|---------|
| `notebooklm_notebooks` | Notebook metadata (27 notebooks) |
| `notebooklm_assets` | Audio overviews, quizzes, flashcards (22 assets) |
| `notebooklm_transcripts` | Full text transcripts (13 transcripts) |
| `notebooklm_summaries` | AI summaries - standard + TLDR (26 records) |
| `notebooklm_quizzes` | Quiz questions (13 quizzes, ~116 questions) |

## Key Files

### Scripts (run with `/Users/z/miniforge3/bin/python`)
| File | Purpose |
|------|---------|
| `playwright_sync.py` | Browser automation to sync NotebookLM → downloads audio |
| `transcribe_optimized.py` | Whisper transcription with 1.5x speedup (cost optimization) |
| `upload_to_supabase.py` | Upload notebooks.json and assets.json to Supabase |
| `upload_transcripts.py` | Upload transcripts, links to assets via FILENAME_TO_ASSET mapping |
| `generate_study_materials.py` | Generate summaries + quizzes using GPT-4o-mini |
| `export_study_materials.py` | Export to markdown files |

### Data Files
| File | Purpose |
|------|---------|
| `notebooks.json` | Scraped notebook metadata |
| `assets.json` | Scraped asset metadata |
| `notebooklm-audio/*.m4a` | Downloaded audio files |
| `notebooklm-audio/*.txt` | Transcripts (same name as audio) |
| `study_materials/` | Exported markdown summaries and quizzes |

### Web App
| File | Purpose |
|------|---------|
| `study-app/index.html` | Single-page app for summaries + quizzes |
| `study-app/netlify.toml` | Netlify deployment config |

## Common Operations

### Full Sync Pipeline
```bash
cd /Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape
/Users/z/miniforge3/bin/python playwright_sync.py        # Download new audio
/Users/z/miniforge3/bin/python transcribe_optimized.py   # Transcribe
/Users/z/miniforge3/bin/python upload_to_supabase.py     # Sync notebooks/assets
/Users/z/miniforge3/bin/python upload_transcripts.py     # Upload transcripts
/Users/z/miniforge3/bin/python generate_study_materials.py  # Generate summaries/quizzes
/Users/z/miniforge3/bin/python export_study_materials.py    # Export markdown
```

### Adding New Audio Files
1. Place `.m4a` files in `notebooklm-audio/`
2. Run `transcribe_optimized.py` (creates `.txt` files)
3. Add mapping to `FILENAME_TO_ASSET` dict in `upload_transcripts.py`
4. Run `upload_transcripts.py`
5. Run `generate_study_materials.py`

### Playwright Login (if session expired)
```bash
/Users/z/miniforge3/bin/python playwright_sync.py --login
```
This opens a visible Chrome window for Google login. Session saved to `.playwright_profile/`

## Environment Variables
Stored in `/Users/z/Desktop/PersonalProjects/ClaudeProjects/.env`:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `OPENAI_API_KEY`

## Known Issues & Fixes

### Study App shows "Loading..."
- **Cause**: Variable naming conflict - `supabase` conflicts with library
- **Fix**: Renamed client variable to `db` in index.html

### Transcripts not uploading
- **Cause**: Missing entry in `FILENAME_TO_ASSET` mapping
- **Fix**: Add filename→asset_title mapping in `upload_transcripts.py`

### Supabase key format
- Use legacy JWT anon key (starts with `eyJ...`), NOT the new `sb_publishable_` format
- The publishable key format doesn't work with the JS client properly

## Costs
| Service | Usage | Cost |
|---------|-------|------|
| Whisper (whisper-1) | ~6 hours audio | ~$1.50 |
| GPT-4o-mini | Summaries/quizzes | ~$0.10 |
| Supabase | Free tier | $0 |
| Netlify | Free tier | $0 |

## Audio Generation Workflow (Browser Automation)

When helping generate new NotebookLM audio overviews:

1. **Always have a conversation first** before generating:
   - Suggest variations for existing notebooks (different angles, topics not yet covered)
   - Suggest new topics based on user's interests
   - Confirm which notebooks the user wants to generate audio for

2. **Check existing audio** before generating:
   - Review `assets.json` for existing audio assets per notebook
   - Verify on NotebookLM UI which audio already exists
   - Don't regenerate audio that already exists unless user wants a new angle

3. **Daily quota**: User's tier allows ~3 audio/day - be mindful and confirm count

4. **Audio settings**: Always set length to "Long" unless user specifies otherwise

5. **Format options**: Deep dive (default), Brief, Critique, Debate - ask user preference

## Study Materials Format Requirements

### Summary Format (for human reading)
Summaries should NOT be meta ("The podcast discusses..."). Instead, write like an article that teaches the actual content:

- **Article-style prose**: Present the information as if teaching the reader directly
- **Key concepts explained**: Don't just list that a topic was covered; explain what was taught
- **Structured sections**: Use headers to organize by topic/theme
- **Examples included**: Include specific examples, statistics, or case studies mentioned
- **Relevant links**: Research and include 3-5 links to learn more about key topics
- **Visual suggestions**: Note where images/diagrams would help (to be sourced later)

### Claude Reference Format (for AI continuity)
A separate machine-readable section to help future Claude sessions:

```json
{
  "topics_covered": ["topic1", "topic2"],
  "key_concepts": {
    "concept_name": "brief definition or explanation"
  },
  "connections_to_other_notebooks": ["notebook_title"],
  "suggested_follow_ups": ["topic that could be explored deeper"],
  "questions_raised": ["open questions from this episode"]
}
```

This enables:
- Avoiding repetition in future audio generation
- Linking concepts across notebooks
- Building on previously learned material

## GitHub Repository

Study app repo: https://github.com/Anonyma/notebooklm-study-hub
