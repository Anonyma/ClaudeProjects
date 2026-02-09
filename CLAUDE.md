# CLAUDE.md

> **GLOBAL DIRECTIVES:** Before proceeding, read `AGENTS.md` in the repository root for global operating procedures valid for all agents.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL: Use Linear for Project Tracking

**ALWAYS use Linear to track project status and create issues for bugs, features, and fixes.**

Linear workspace: https://linear.app/z-z-z | Team: Z

### When to Update Linear

| Event | Action |
|-------|--------|
| User reports a bug | `mcp__linear-server__create_issue` with project, description, priority |
| User requests a feature | `mcp__linear-server__create_issue` with requirements |
| Starting work on an issue | `mcp__linear-server__update_issue` → state: "In Progress" |
| Completing an issue | `mcp__linear-server__update_issue` → state: "Done" |
| Project milestone complete | `mcp__linear-server__update_project` with status update |

### Quick Reference

```
# Create issue for a bug/feature
mcp__linear-server__create_issue
  title: "Clear description"
  team: "Z"
  project: "Project Name"  # Match exactly
  description: "Details here"
  priority: 3  # 1=Urgent, 2=High, 3=Normal, 4=Low

# Update issue status
mcp__linear-server__update_issue
  id: "issue-id"
  state: "Done"  # Backlog, Todo, In Progress, Done, Canceled
```

---

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

**NO EXCEPTIONS.** Every response that touches files must end with a URL or file path the user can click/copy to verify the work. This is non-negotiable.

### What to Include:

**CRITICAL:** Only provide a localhost URL if you have VERIFIED the server is actually running and accessible. After starting a server, always test with `curl -s -o /dev/null -w "%{http_code}" http://localhost:XXXX/` before presenting the URL to the user. If the server isn't running, provide the file path instead (but note if the file requires a server to work properly).

**IMPORTANT:** Don't tell the user to "open this file" if it will only display as plain text (e.g., HTML source). If a file needs a browser/server to render properly, either start the server first OR mention "Path: /path/to/file" without suggesting they open it directly.

**IMPORTANT:** Prefer `http://localhost:XXXX` URLs over `file://` URLs - localhost links are clickable, file:// requires copy-paste.

**IMPORTANT:** For documents like Markdown, text files, or other files that render as plain text via localhost, ALWAYS provide BOTH:
1. The localhost URL (for quick access)
2. The full file path (so user can open in an app that renders it properly, e.g., markdown preview)

Example for markdown files:
```
**View:** http://localhost:8877/report.md
**File:** /Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/report.md
```

For **local web apps** (start a server so links are clickable):
```bash
cd /Users/z/Desktop/PersonalProjects/ClaudeProjects/[project] && python3 -m http.server 8XXX &
# Then provide: http://localhost:8XXX/index.html
```

For **one-off outputs** (use the scratch server on port 8877):
```
**View:** http://localhost:8877/your-file.html
```
For markdown/text files, also include:
```
**File:** /Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/your-file.md
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

## Device File Sync (`device-sync/`)

**For files that need to be transferred between Mac and CandyPop, use the `device-sync/` folder.**

### Location
- **Mac:** `/Users/z/Desktop/PersonalProjects/ClaudeProjects/device-sync/`
- **CandyPop:** `~/device-sync/`

### Structure
```
device-sync/
├── audio-transcriptions/  # Voice journals and their transcripts
├── documents/             # Documents to share between devices
└── media/                 # Images, videos, etc.
```

### When to Use
- Voice journal recordings and transcriptions
- Documents that need to be accessed on both machines
- Media files for processing or transfer
- Any file that should be kept long-term and accessible on both devices

### Transfer Commands
```bash
# Mac → CandyPop
scp /path/to/file CandyPop:~/device-sync/[subfolder]/

# CandyPop → Mac
scp CandyPop:~/device-sync/[subfolder]/file /Users/z/Desktop/PersonalProjects/ClaudeProjects/device-sync/[subfolder]/
```

### Important
- **NOT for temporary files** - use `_scratch/` for that
- Files here are intended to be kept and synced between devices
- Commit important transcriptions and documents to git

---

## CRITICAL: Notify User via BabyClaw (Telegram)

**ALWAYS notify the user when you need help, complete significant work, or encounter errors.**

### When to Notify

✅ **MUST notify when:**
- You are **blocked** and need user intervention
- You have **completed** a significant task
- You encounter **critical errors**

❌ **Don't spam:** Not for minor edits or routine operations.

### How to Notify (Telegram via Clawdbot - Preferred)

```bash
clawdbot message send --channel telegram --target 355422856 --message "Your message here"
```

### Examples

**When blocked:**
```bash
clawdbot message send --channel telegram --target 355422856 --message "🆘 Blocked: [project] - [issue]. Need: [what you need]"
```

**When completed:**
```bash
clawdbot message send --channel telegram --target 355422856 --message "✅ Done: [project] - [what you completed]"
```

**When error:**
```bash
clawdbot message send --channel telegram --target 355422856 --message "⚠️ Error: [project] - [error description]"
```

### Fallback: Direct Pushover (if clawdbot/Telegram unavailable)

```bash
curl -s -F "token=ax3nv6fmix3hzr1vzkkb85123js5np" \
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

## CRITICAL: Log Work Sessions

**After completing work on any project, log what you did in `_worklog/`.**

This helps future agents pick up where you left off.

### Quick Log Command:
```bash
cat >> /Users/z/Desktop/PersonalProjects/ClaudeProjects/_worklog/sessions/$(date +%Y-%m-%d)-PROJECTNAME.md << 'EOF'
## Session: [TIME]
**Status:** [completed/blocked/in-progress]

### Done:
- What you did

### Issues:
- Known problems

### Next:
- What's left

### Files:
- Changed files

### Access:
- URLs/commands to test
EOF
```

### Also update LATEST.md:
```bash
echo "| $(date +%Y-%m-%d) | project-name | status | one-line summary |" >> /Users/z/Desktop/PersonalProjects/ClaudeProjects/_worklog/LATEST.md
```

### View recent activity:
```bash
cat /Users/z/Desktop/PersonalProjects/ClaudeProjects/_worklog/LATEST.md
```

---

## Repository Structure

This is a personal projects repository containing independent project directories:

- **notebooklm_scrape/** - NotebookLM Study System (see project CLAUDE.md for details)

## IMPORTANT: Project-Specific Instructions

**For NotebookLM tasks (scraping, transcribing, generating audio, summaries):**
→ **ALWAYS read** `notebooklm_scrape/CLAUDE.md` first. It contains critical instructions for:
- Summary format requirements (article-style, NOT meta descriptions)
- Audio generation strategy for comprehensive, non-redundant coverage
- Transcript analysis workflow
- Prompting best practices for NotebookLM

---
When I report a bug, don't start by trying to fix it. Instead, start by writing a test that reproduces the bug. Then, have subagents try to fix the bug and prove it with a passing test.
