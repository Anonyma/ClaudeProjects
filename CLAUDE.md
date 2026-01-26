# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL: Report Agent Status

**ALWAYS report your status to the Agent Hub when starting, getting blocked, completing, or encountering errors.**

### When to Report

| Event | Command |
|-------|---------|
| Starting work | `report-status --name [agent-name] running "Starting: [task description]"` |
| Making progress | `report-status --name [agent-name] running "[current task]"` |
| Blocked/need help | `report-status --name [agent-name] blocked "[what you need]"` |
| Task completed | `report-status --name [agent-name] completed "[what was done]"` |
| Error occurred | `report-status --name [agent-name] error "[error description]"` |

### Agent Naming
- Use a short, descriptive name: `deploy-bot`, `scraper`, `refactor-auth`, `fix-bug-123`
- If working on a specific project, include it: `brainstormrr-fixes`, `time-tracker-deploy`
- The `--name` flag is optional; defaults to current directory name

### Examples

```bash
# Starting a task
report-status --name feature-auth running "Implementing OAuth login flow"

# When blocked
report-status --name feature-auth blocked "Need OAuth client credentials for Google"

# On completion
report-status --name feature-auth completed "OAuth login working, deployed to staging"

# On error
report-status --name feature-auth error "Build failed: missing @auth/core dependency"
```

### Dashboard Access
- **Terminal:** Run `agent-status` or `agents`
- **Web:** Open http://localhost:8766/dashboard.html or run `agent-dashboard`

---

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

## CRITICAL: Always Provide Access Instructions

**At the end of EVERY response where you create, modify, or complete work on a project, ALWAYS provide the user with a way to test or access the changes.**

### What to Include:

**IMPORTANT:** Prefer `http://localhost:XXXX` URLs over `file://` URLs - localhost links are clickable, file:// requires copy-paste.

For **local web apps** (start a server so links are clickable):
```bash
cd /Users/z/Desktop/PersonalProjects/ClaudeProjects/[project] && python3 -m http.server 8XXX &
# Then provide: http://localhost:8XXX/index.html
```

For **one-off outputs** (use the scratch server on port 8877):
```
**View:** http://localhost:8877/your-file.html
```

For **deployed apps**:
```
**Live at:** https://[project].netlify.app
```

For **scripts/CLI tools**:
```
**To run:**
python3 /path/to/script.py [args]
```

For **test files**:
```
**To run tests:** Open in browser:
file:///path/to/test.html
```

### Examples:

✅ Good ending:
> "Fixed the crash bug and added category management. **To test:** Open `file:///Users/z/Desktop/PersonalProjects/ClaudeProjects/brainstormrr/index.html` in your browser."

❌ Bad ending:
> "Fixed the crash bug and added category management." (no access instructions)

---

## Temporary Outputs & One-Off Files (`_scratch/`)

**For one-off reports, dashboards, utilities, or temporary outputs - use the `_scratch/` folder.**

### Location
```
/Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/
```

### When to Use
- Diagnostic reports (memory usage, system stats)
- Temporary HTML dashboards or visualizations
- One-off utilities that don't warrant their own project
- Debug outputs, logs, or analysis files
- Anything generated that might be discarded later

### Serving Files (Clickable Links)
Always serve via HTTP instead of `file://` URLs (which require copy-paste):

```bash
# Start server on port 8877 (if not already running)
cd /Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch && python3 -m http.server 8877 &

# Then provide clickable link:
# http://localhost:8877/your-file.html
```

### Promoting to Projects
If a scratch file becomes useful long-term, move it to its own project folder and log it properly.

### Cleanup
The `_scratch/` folder can be periodically cleaned. Don't put anything critical here.

---

## CRITICAL: Notify User via BabyClaw (Telegram)

**ALWAYS notify the user when you need help, complete significant work, or encounter errors.**

### When to Notify

✅ **MUST notify when:**
- You are **blocked** and need user intervention
- You have **completed** a significant task
- You encounter **critical errors**

❌ **Don't spam:** Not for minor edits or routine operations.

### How to Notify (Use clawdbot gateway wake)

```bash
clawdbot gateway call wake --params '{"text": "Your message here", "mode": "now"}'
```

### Examples

**When blocked:**
```bash
clawdbot gateway call wake --params '{"text": "🆘 Blocked: [project] - [issue]. Need: [what you need]", "mode": "now"}'
```

**When completed:**
```bash
clawdbot gateway call wake --params '{"text": "✅ Done: [project] - [what you completed]", "mode": "now"}'
```

**When error:**
```bash
clawdbot gateway call wake --params '{"text": "⚠️ Error: [project] - [error description]", "mode": "now"}'
```

### Fallback: Direct Pushover (if clawdbot unavailable)

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
