# NotebookLM Study System

## Overview
Automated system for scraping NotebookLM audio overviews, transcribing them, generating study materials (summaries + quizzes), and serving them via a web app.

---

## User Communication Preferences
- Do not output code changes or diffs in responses. Provide diagrams, brief summaries, or checklists instead.
- Always include an access link at the end of responses (live URL or local file path) so the user can preview the app or work.

---

## CRITICAL: Summary Format Requirements

**Summaries must be ARTICLE-STYLE, not meta descriptions.**

### What NOT to do (meta style):
```
❌ "The podcast explores the transition from ornate to austere art styles..."
❌ "In this episode, the hosts discuss..."
❌ "The deep dive examines..."
```

### What TO do (article style):
```
✅ Write as if teaching the reader directly
✅ Present the actual content and insights
✅ Use "you" to address the reader
✅ Include specific examples, dates, names from the transcript
```

### Required Summary Structure:

```markdown
# [Topic Title]

## Overview
[2-3 sentences introducing what you'll learn - NOT what "the podcast covers"]

## [Major Theme 1]
[Teach the actual content. Include specific examples, quotes, data points]

## [Major Theme 2]
[Continue teaching. Be specific and substantive]

## Key Insights
- [Specific insight with supporting detail]
- [Another insight]

## Connections & Context
[How this relates to other topics, historical context, modern relevance]

## Learn More
- [Link 1: Title](url) - Brief description
- [Link 2: Title](url) - Brief description

---

<!-- Claude Reference (for AI continuity) -->
```json
{
  "topics_covered": ["topic1", "topic2"],
  "key_concepts": {"concept": "definition"},
  "connections_to_other_notebooks": ["notebook_title"],
  "suggested_follow_ups": ["topics for deeper exploration"],
  "gaps_not_covered": ["what this audio didn't address"]
}
```
```

---

## CRITICAL: Source Sourcing Strategy

### Goal: Deep Research Base (50+ Sources)

**Before creating any Deep Dive audio, you MUST ensure a robust source base.**
A Deep Dive based on 5-10 sources is shallow. One based on 50+ sources is comprehensive.

### The Protocol:
1.  **Prompt NotebookLM to find sources:** Ask it to find relevant sources for your topic.
2.  **Iterative Collection:**
    - It typically finds ~10 sources at a time.
    - **Import** these sources immediately.
    - **Repeat** the prompt to find *more* different sources.
    - **Alternative:** Use **Deep Research Mode** if available to find larger batches (up to 50).
3.  **Threshold:** Do NOT generate the Deep Dive audio until you have imported **at least 50 high-quality sources**.
4.  **Verification:** Check the "Sources" tab to ensure diversity (papers, articles, reliable web pages).

---

## CRITICAL: Audio Generation Strategy

### Goal: Comprehensive, Non-Redundant Coverage

NotebookLM notebooks often have 50-100 sources. A single 20-minute audio can't cover everything. The strategy is to generate MULTIPLE audio files, each focusing on DIFFERENT aspects.

### NotebookLM Limitations (Research-Based)
- **Maximum length: ~20 minutes** with "Longer" setting
- ~10 minutes with "Default"
- ~5 minutes with "Shorter"
- **60-minute deep dives are NOT possible** in a single generation

### How to Get Comprehensive Coverage

1. **Analyze existing transcripts first** - Before generating new audio, read ALL existing transcripts for that notebook to understand what's already covered

2. **Generate prompts for uncovered areas** - Use specific, positive instructions (NOT negative like "don't cover X")

3. **Use the Customize feature** with specific focus areas:
   - "Focus ONLY on [specific subtopic]"
   - "Target expertise level: expert/advanced"
   - "Cover the following specific aspects: [list]"

### Before Generating New Audio

Run this analysis workflow:

```
1. Read all transcripts for the notebook
2. Create a coverage map:
   - Topics thoroughly covered
   - Topics mentioned briefly
   - Topics NOT covered at all
3. Check sources.json - what sources exist that weren't discussed?
4. Generate a prompt targeting UNCOVERED areas
```

### Effective Prompt Templates

**For deeper exploration of a subtopic:**
```
Focus exclusively on [specific topic].
Assume the listener already knows the basics from previous episodes.
Go deep into: [specific aspects]
Include: specific examples, case studies, counterarguments
Expertise level: Advanced
```

**For different perspective:**
```
Approach this topic from [specific angle/discipline].
Focus on: [specific questions]
Don't repeat general overviews - get into the nuances.
```

**For connecting themes:**
```
Explore the connections between [topic A] and [topic B].
Focus on: how they influenced each other, shared patterns, contrasts
Assume familiarity with both topics.
```

### Best Practices from Research

1. **Consolidate sources before generating:**
   - Generate Study Guide, FAQ, Timeline notes
   - Click "Convert all notes to source"
   - This creates a focused summary the AI uses

2. **Set expertise level:** Use "Expert" for more depth, less basics

3. **Use follow-up prompts:** After initial generation, use interactive mode to dig deeper

4. **Multiple passes:** Generate several shorter focused audios rather than one long general one

Sources:
- https://support.google.com/notebooklm/answer/16212820
- https://www.xda-developers.com/notebooklm-audio-overview-tips/

---

## Architecture

```
User's NotebookLM Account
         ↓ (Playwright automation)
   Audio Downloads (.m4a)
         ↓ (OpenAI Whisper)
     Transcripts (.txt)
         ↓ (GPT-4o-mini / Claude)
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
| `notebooklm_assets` | Audio overviews, quizzes, flashcards |
| `notebooklm_transcripts` | Full text transcripts |
| `notebooklm_summaries` | AI summaries - standard + TLDR |
| `notebooklm_quizzes` | Quiz questions |

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

1. **Analyze existing coverage first:**
   - Read ALL transcripts for the notebook in `notebooklm-audio/`
   - Review `assets.json` for existing audio assets
   - Create a mental map of what's covered vs. gaps

2. **Propose non-redundant audio:**
   - Identify topics NOT yet covered
   - Suggest specific focus areas for new audio
   - Confirm with user before generating

3. **Daily quota**: User's tier allows ~3 audio/day - be mindful and confirm count

4. **Audio settings**: Always set length to "Long" unless user specifies otherwise

5. **Format options**: Deep dive (default), Brief, Critique, Debate - ask user preference

## Transcript Analysis Workflow

Before generating new audio for a notebook:

```python
# Pseudocode for coverage analysis
1. List all transcripts for notebook (from notebooklm-audio/*.txt)
2. For each transcript:
   - Extract main topics discussed
   - Note specific examples/case studies mentioned
   - Identify depth level (overview vs deep dive)
3. Compare against notebook sources (sources.json)
4. Identify:
   - Well-covered topics (skip these)
   - Briefly mentioned topics (could go deeper)
   - Uncovered source material (target these)
5. Generate specific prompt for new audio
```

## GitHub Repository

Study app repo: https://github.com/Anonyma/notebooklm-study-hub
