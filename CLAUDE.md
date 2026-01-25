# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL: Git Commits

**After creating or modifying files in this repository, ALWAYS commit the changes.**

- Commit after adding new files
- Commit after editing existing files
- Commit after updating `projects.json`
- Use clear, descriptive commit messages
- Don't batch unrelated changes - commit per logical unit of work

Example:
```bash
git add -A && git commit -m "Add voice-memo-transcriber project"
```

---

## CRITICAL: Notify User When Blocked/Completed/Error

**ALWAYS notify the user when you need help, complete significant work, or encounter errors.**

### When to Notify

✅ **MUST notify when:**
- You are **blocked** and need user intervention
- You have **completed** a significant task
- You encounter **critical errors**

❌ **Don't spam:** Not for minor edits or routine operations.

### How to Notify (Use log-status endpoint)

This automatically sends Pushover notifications to user's phone AND laptop:

```bash
curl -s -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-status' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU' \
  -d '{
    "session_id": "claude-[type]-[date]",
    "session_type": "cli",
    "current_task": "What you are working on",
    "project_id": "project-slug",
    "status": "blocked",
    "blocked_on": "What is blocking you",
    "progress_notes": "Additional context"
  }'
```

### Status Values (triggers different notifications)

| Status | Notification | Priority |
|--------|--------------|----------|
| `blocked` | 🆘 Agent Blocked | High (bypasses quiet hours) |
| `error` | ⚠️ Agent Error | High |
| `completed` | ✅ Task Completed | Normal |
| `active` | No notification | - |

### Quick Examples

**When blocked:**
```bash
curl -s -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-status' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU' \
  -d '{"session_id": "cli-2026-01-25", "session_type": "cli", "current_task": "Deploy bot", "project_id": "tg-bot", "status": "blocked", "blocked_on": "Missing TELEGRAM_BOT_TOKEN in Railway"}'
```

**When completed:**
```bash
curl -s -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-status' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU' \
  -d '{"session_id": "cli-2026-01-25", "session_type": "cli", "current_task": "Deployed to Netlify", "project_id": "writing-challenge", "status": "completed", "progress_notes": "Live at https://writing-challenge-app.netlify.app"}'
```

### Fallback: Direct Pushover (if log-status fails)

```bash
curl -s -F "token=aabpf2tb7a9p3tnhdw3vzfb6hyxcna" \
  -F "user=u8wpte8pqd3snj75s2n8gxqdzq94xj" \
  -F "title=🆘 Agent Needs Help" \
  -F "message=Project: [name] - Issue: [description]" \
  -F "priority=1" \
  https://api.pushover.net/1/messages.json
```

---

## CRITICAL: Auto-Log Every Project You Create

**EVERY Claude instance (CLI, Browser, Web) MUST log projects immediately after creation or deployment.**

### How to Log (Choose based on your capabilities):

#### Option 1: API Call (Works for ALL Claude instances including Browser)
```bash
curl -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-project' \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "my-project-slug",
    "name": "My Project Name",
    "description": "What it does",
    "type": "web-app",
    "status": "active",
    "hosted_url": "https://my-app.netlify.app",
    "github_repo": "https://github.com/user/repo",
    "deployment_platform": "netlify",
    "tags": ["tag1", "tag2"]
  }'
```

#### Option 2: Supabase MCP (Claude Code CLI only)
```sql
INSERT INTO claude_projects (id, name, description, type, status, hosted_url, tags)
VALUES ('project-id', 'Name', 'Description', 'web-app', 'active', 'https://url', ARRAY['tags']);
```

#### Option 3: Update local JSON (Claude Code CLI only)
Also update: `/Users/z/Desktop/PersonalProjects/ClaudeProjects/projects.json`

### Required Fields:
- `id`: URL-safe slug (e.g., "my-cool-app")
- `name`: Human-readable name

### Optional but Recommended:
- `description`: What the project does
- `type`: web-app, telegram-bot, python-scripts, document, artifact, api
- `status`: active, wip, needs-fix, archived, deprecated
- `hosted_url`: Live URL if deployed
- `path`: Local file path if applicable
- `localhost_command`: Command to run locally (e.g., "python -m http.server 8000")
- `github_repo`: GitHub repository URL
- `deployment_platform`: netlify, railway, replit, vercel, github-pages
- `claude_session_url`: Link back to the Claude session that created it
- `tags`: Array of relevant tags

### When to Log:
- After deploying to Netlify, Railway, Vercel, Replit, GitHub Pages
- After creating a local web app or script
- After generating an artifact that should be saved
- After significant updates to existing projects

### Project Command Center Dashboard:
View all projects at: `file:///Users/z/Desktop/PersonalProjects/ClaudeProjects/project-command-center/index.html`
Or deploy to Netlify for remote access.

---

## Repository Structure

This is a personal projects repository containing independent project directories:

- **notebooklm_scrape/** - Python scripts for scraping NotebookLM data and transcribing audio

## notebooklm_scrape

### Purpose
Scrapes notebook metadata, sources, and audio assets from NotebookLM. Includes audio transcription via OpenAI API.

### Setup
```bash
cd notebooklm_scrape
pip3 install -r requirements.txt
export OPENAI_API_KEY='your-key'  # Required for transcription only
```

### Commands

**Initialize/update notebook data from DOM scrapes:**
```bash
python3 scrape_data.py           # Create initial notebooks.json from raw data
python3 batch_add_notebooks.py   # Batch update all notebook metadata
```

**Add individual notebook data (from browser scraping):**
```bash
python3 add_notebook_data.py '<json_data>'
```

**Finalize and validate:**
```bash
python3 finalize_scrape.py       # Update notebook IDs, validate JSON, print summary
```

**Transcribe audio files:**
```bash
python3 transcribe_notebooklm.py --test-one              # Test with single file first
python3 transcribe_notebooklm.py notebooklm-audio/       # Transcribe all audio
```

### Data Files
- `notebooks.json` - Notebook metadata (title, description, tags, source count)
- `sources.json` - Source documents for each notebook
- `assets.json` - Generated assets (audio overviews)
- `progress.log` - Scraping progress log

### Architecture
Scripts share common patterns:
- `SCRAPE_DIR` constant points to the project directory
- `load_json()`/`save_json()` for data persistence
- `log_progress()` appends timestamped entries to progress.log
- Deduplication via `(notebook_id, source_title)` or `(notebook_id, asset_title)` tuples

Workflow: Browser scraping (manual via Claude-in-Chrome) → DOM data → Python processing → JSON files

### Cost Warning
Transcription uses OpenAI's `gpt-4o-transcribe` model (~$2.50/hour of audio). Always test with `--test-one` first.
