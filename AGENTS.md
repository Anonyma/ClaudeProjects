# Global Agent Directives (AGENTS.md)

**Authority:** This file contains the primary operating procedures for ALL AI agents (Claude, Gemini, etc.) working in this environment. Read this first.

## 1. Core Mandates
- **Tone:** Concise, professional, direct. No filler ("Okay, I will...").
- **Safety:** NEVER delete files or revert changes without explicit user confirmation.
- **Verification:** Always verify your work. If you generate code, verify it runs. If you generate text, verify word counts.
- **Access:** ALWAYS provide a way for the user to access/view your work (URL, file path, or command) at the end of a response.
- **Source Control:** If a git repo exists, commit meaningful changes. If you cannot commit, explicitly say why and log it in `_worklog/sessions/`.
- **Prompt + Plan Capture:** For non-trivial builds, save the initial user prompt and a short plan in the session log before building, and summarize changes after.

## 2. Project Tracking & Status
- **Linear:** Use Linear for all project tracking. If you are an agent with Linear tools, use them. If not, ask the user to log items.
- **Status Reporting:** Report your status (starting, blocked, completed) to the Agent Hub if you have shell access (`report-status`).
- **Work Logging:** Log your session details in `_worklog/sessions/` and update `_worklog/LATEST.md` upon completion.

## 3. Project-Specific Directives

### NotebookLM / Study Hub
- **Deep Dives:** All generated deep dive lessons/articles MUST be **7,000+ words**.
- **Content:** Do not produce "meta" summaries ("The article discusses..."). Produce the actual content ("The Habsburgs rose to power by...").
- **Format:** JSON output must be valid. Use `article` key for text content.

### Web Development
- **Deployment:** Log all new projects to Supabase and `projects.json`.
- **Frameworks:** Prefer established patterns found in the repo.
- **Artifacts:** Keep a backup copy of the final built artifact(s) in `_worklog/artifacts/` (timestamped), or clearly state if you did not.

## 4. Notifications
- **When to Notify:** Blockers, Completion, Critical Errors.
- **Method:** Use `clawdbot` (Telegram) or direct Pushover API if available.
  - Target: `355422856` (Telegram)
