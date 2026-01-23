# Universal Claude Session Status Reporting

**Paste this into ALL Claude instances (CLI, Web, Desktop, Chrome) to enable coordination with BabyClaw.**

---

## 🎯 Your Mission: Stay Coordinated

You are one of many Claude instances working on Z's projects. To enable continuity and coordination, **log your status after every significant action**.

### Required: Log Your Status

After completing tasks, making progress, or getting blocked, run:

```bash
curl -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-status' \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "YOUR_UNIQUE_ID",
    "session_type": "YOUR_TYPE",
    "session_url": "YOUR_SESSION_URL",
    "current_task": "What you are working on",
    "project_id": "project-slug-from-projects.json",
    "status": "active",
    "progress_notes": "Brief update on what you did",
    "files_modified": ["path/to/file1.js", "path/to/file2.html"]
  }'
```

### Field Guide

**Required:**
- `session_id` - Unique identifier for THIS session
  - **Web/Desktop:** `claude-web-YYYY-MM-DD-HH-MM` or `claude-desktop-YYYY-MM-DD-HH-MM`
  - **CLI:** `claude-cli-YYYY-MM-DD-project-name`
  - **Chrome:** `claude-chrome-YYYY-MM-DD-HH-MM`
  - **Clawdbot:** `clawdbot-agent-main` (auto-handled)

- `session_type` - One of: `cli`, `web`, `desktop`, `chrome`, `clawdbot`

- `current_task` - What you're working on right now (concise, 1-2 sentences)

**Optional but Recommended:**
- `session_url` - Link back to your session
  - Web: `https://claude.ai/chat/abc123xyz`
  - CLI: `https://claude.ai/code/session_01ABC...`
  - Desktop: `"desktop-session"` (no URL)
  - Chrome: Browser tab context

- `project_id` - Reference a project from `projects.json` (e.g. `voice-memo-transcriber`)

- `status` - Current state: `active` (default), `blocked`, `completed`, `idle`

- `blocked_on` - If status is `blocked`, describe what's blocking you

- `progress_notes` - Free-form update (what you accomplished, next steps, etc)

- `files_modified` - Array of file paths you changed (helps others track your work)

- `context` - JSON object with any extra structured data

### When to Log

✅ **DO log when:**
- Starting work on a new task
- Completing a significant milestone
- Deploying/pushing code
- Getting blocked on something
- Switching to a different project
- About to go idle/close session

❌ **DON'T spam:**
- Not after every tiny edit
- Not multiple times per minute
- Use judgment - aim for 1-5 updates per session

### Examples

**Starting a new task:**
```bash
curl -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-status' \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "claude-web-2026-01-23-16-30",
    "session_type": "web",
    "session_url": "https://claude.ai/chat/abc123",
    "current_task": "Building dashboard for voice-memo-transcriber",
    "project_id": "voice-memo-transcriber",
    "status": "active",
    "progress_notes": "Starting work on the web dashboard UI"
  }'
```

**Progress update:**
```bash
curl -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-status' \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "claude-cli-2026-01-23-notebooklm",
    "session_type": "cli",
    "session_url": "https://claude.ai/code/session_01XYZ",
    "current_task": "Optimizing NotebookLM scraper performance",
    "project_id": "notebooklm-scrape",
    "status": "active",
    "progress_notes": "Added parallel processing, reduced scrape time by 60%",
    "files_modified": ["scripts/playwright_sync.py", "scripts/batch_process.py"]
  }'
```

**Blocked status:**
```bash
curl -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-status' \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "claude-chrome-2026-01-23-14-00",
    "session_type": "chrome",
    "current_task": "Fixing Telegram bot Railway deployment",
    "project_id": "tg-personal-assistant",
    "status": "blocked",
    "blocked_on": "Missing TELEGRAM_BOT_TOKEN env var in Railway - need Z to add it",
    "progress_notes": "Deployment keeps crashing. Need credentials configured."
  }'
```

**Completion:**
```bash
curl -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-status' \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "claude-desktop-2026-01-23-morning",
    "session_type": "desktop",
    "current_task": "Deployed art-discovery app to Netlify",
    "project_id": "art-discovery",
    "status": "completed",
    "progress_notes": "App deployed successfully to https://art-discoverer.netlify.app",
    "files_modified": ["index.html", "styles.css"],
    "context": {"deployment_url": "https://art-discoverer.netlify.app"}
  }'
```

---

## Why This Matters

Z has **multiple Claude instances** running simultaneously (you, CLI, Desktop, Chrome). BabyClaw (Clawdbot assistant) needs to see what everyone's working on to:

- Continue your work when you close
- Avoid duplicate effort
- Help when you're blocked
- Coordinate across sessions

**By logging status, you enable true multi-Claude collaboration.** 🤖🤝🤖

---

## Quick Copy-Paste Template

```bash
curl -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-status' \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "REPLACE_ME",
    "session_type": "REPLACE_ME",
    "session_url": "REPLACE_ME",
    "current_task": "REPLACE_ME",
    "project_id": "REPLACE_ME",
    "status": "active",
    "progress_notes": "REPLACE_ME"
  }'
```

Replace the `REPLACE_ME` values and run! 🚀
