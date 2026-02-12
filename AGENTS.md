# AGENTS.md — Single Source of Truth

**This file contains ALL operating procedures for ALL AI agents (Claude, Codex, Gemini, etc.) working in this repository. Both `CLAUDE.md` and `GEMINI.md` point here.**

---

## 1. Machines

| Name | OS | SSH | IP (Tailscale) | Notes |
|------|----|-----|-----------------|-------|
| Mac (local) | macOS | — | — | Primary dev machine |
| CandyPop | Pop!_OS (Linux) | `ssh CandyPop` | 100.81.82.35 | Heavier compute, browser automation, long-running agents |

---

## 2. Core Mandates

- **Tone:** Concise, professional, direct. No filler ("Okay, I will...").
- **Safety:** NEVER delete files or revert changes without explicit user confirmation.
- **Verification:** Always verify your work. If you generate code, verify it runs. If you generate text, verify word counts.
- **Source Control:** If a git repo exists, commit meaningful changes per logical unit of work. If you cannot commit, explicitly say why and log it in `_worklog/sessions/`.
- **Prompt + Plan Capture:** For non-trivial builds, save the initial user prompt and a short plan in the session log before building, and summarize changes after.
- **Bug Reports:** When the user reports a bug, don't start by trying to fix it. Instead, start by writing a test that reproduces the bug. Then, have subagents try to fix the bug and prove it with a passing test.

---

## 3. Status Reporting & Notifications

**Report your status to the Agent Hub. `blocked`/`completed`/`error` auto-notify via Telegram.**

```bash
report-status [--name NAME] [--ai TYPE] [--project NAME] [--url URL] STATUS "message"
```

- `--name`: Agent name (default: cwd basename). Use descriptive names: `deploy-bot`, `fix-bug-123`
- `--ai`: `claude` (default) | `gemini` | `codex` | `ollama`
- `--url`: Live URL — sent as clickable link in Telegram notification
- **STATUS:** `running` | `blocked` | `completed` | `error` | `idle`

### When to Report
- **Starting**: `report-status --name my-agent running "Starting task"`
- **Blocked**: `report-status --name my-agent blocked "Need API credentials"`
- **Completed**: `report-status --name my-agent completed "Done"`
- **Completed with URL**: `report-status --name my-agent --url "https://app.netlify.app" completed "Deployed"`
- **Error**: `report-status --name my-agent error "Build failed"`

**IMPORTANT:** When completing a project with a live URL, ALWAYS include `--url` so the user gets a clickable link on their phone to review.

### For Non-CLI Agents (HTTP API)
```bash
curl -s -X POST http://localhost:8767/api/status \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent", "status": "completed", "task": "Deployed", "url": "https://app.netlify.app", "ai_type": "claude"}'
```

### Additional Notification Methods
- **From CandyPop:** `~/bin/notify-mac "Message" "Title" "Optional URL"`
- **From Mac:** `curl "http://localhost:12345/?msg=Done&title=Agent"`
- **Dashboard:** http://localhost:8767/ | **Terminal:** `agents` or `agent-status --watch`

---

## 4. Linear Project Tracking

**Use Linear to track project status, create issues, and manage tasks.**

Linear workspace: https://linear.app/z-z-z | Team: Z

### When to Update Linear

| Event | Action |
|-------|--------|
| User reports a bug | Create issue with project, description, priority |
| User requests a feature | Create issue with requirements |
| Starting work on an issue | Update issue state → "In Progress" |
| Completing an issue | Update issue state → "Done" |
| Project milestone complete | Update project with status + comment |

### Quick Reference (MCP / CLI)

```
# Create issue
mcp__linear-server__create_issue
  title: "Clear description"
  team: "Z"
  project: "Project Name"
  description: "Details"
  priority: 3  # 1=Urgent, 2=High, 3=Normal, 4=Low

# Update issue
mcp__linear-server__update_issue  id: "issue-id"  state: "Done"

# Update project
mcp__linear-server__update_project  id: "project-id"  state: "In Progress"
```

### Linear Project Descriptions

Include: overview, key features, file paths, access URLs. Recommended: GitHub link, category, recent updates with dates, status notes.

---

## 5. Always Provide Access Instructions

**At the end of EVERY response where you create, modify, or complete work, ALWAYS provide a way to test or access the changes. NO EXCEPTIONS.**

- Only provide a localhost URL if you have VERIFIED the server is running (`curl -s -o /dev/null -w "%{http_code}" http://localhost:XXXX/`).
- Prefer `http://localhost:XXXX` over `file://` URLs (localhost is clickable).
- For markdown/text files, provide BOTH localhost URL and file path.
- ALWAYS mention the live remote URL if the project is deployed.

### Patterns

| Type | What to provide |
|------|----------------|
| Local web app | Start server, then `http://localhost:8XXX/index.html` |
| One-off output | `http://localhost:8877/file.html` (scratch server) |
| Deployed app | `https://[project].netlify.app` |
| Script/CLI | `python3 /path/to/script.py [args]` |
| Markdown file | URL + `**File:** /full/path.md` |

---

## 6. Netlify Deployment Safety

- **NEW SITES:** Always create a NEW Netlify site (`netlify sites:create`) for new projects.
- **NO REUSE:** NEVER reuse an existing Site ID or URL unless you are certain it belongs to the current project.
- **VERIFY:** Check that `netlify.toml` doesn't contain hardcoded IDs from copied templates.

---

## 7. Project Logging

### Auto-Log Every Project You Create

Log projects immediately after creation or deployment:

```bash
curl -X POST 'https://ydwjzlikslebokuxzwco.supabase.co/functions/v1/log-project' \
  -H 'Content-Type: application/json' \
  -d '{"id": "slug", "name": "Name", "description": "What it does", "type": "web-app", "status": "active", "hosted_url": "https://url", "tags": ["tag1"]}'
```

Also update: `/Users/z/Desktop/PersonalProjects/ClaudeProjects/projects.json`

### Log Work Sessions

After completing work, log in `_worklog/sessions/` and update `_worklog/LATEST.md`:

```bash
echo "| $(date +%Y-%m-%d) | project-name | status | summary |" >> _worklog/LATEST.md
```

---

## 8. Temporary Outputs (`_scratch/`)

Use `_scratch/` for one-off reports, dashboards, debug outputs. Serve via `python3 -m http.server 8877` for clickable links. Promote to project folder if it becomes long-term.

**Path:** `/Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/`

---

## 9. Device File Sync (`device-sync/`)

For files shared between Mac and CandyPop:
- **Mac:** `/Users/z/Desktop/PersonalProjects/ClaudeProjects/device-sync/`
- **CandyPop:** `~/device-sync/`

```bash
scp /path/to/file CandyPop:~/device-sync/[subfolder]/     # Mac → CandyPop
scp CandyPop:~/device-sync/[subfolder]/file device-sync/   # CandyPop → Mac
```

---

## 10. Project-Specific Directives

### NotebookLM / Study Hub
- **Deep Dives:** All articles MUST be **7,000+ words**.
- **Sourcing:** Gather **50+ sources** before generating Deep Dive audio.
- **Content:** Produce actual content, not meta summaries.
- **Format:** Valid JSON with `article` key.
- **Details:** Read `notebooklm_scrape/CLAUDE.md` for full instructions.

### Web Development
- Log all new projects to Supabase and `projects.json`.
- Prefer established patterns found in the repo.
- Keep backup artifacts in `_worklog/artifacts/` (timestamped).
