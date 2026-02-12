# Global Agent Directives (AGENTS.md)

**Authority:** This file contains the primary operating procedures for ALL AI agents (Claude, Gemini, etc.) working in this environment. Read this first.

## 1. Core Mandates
- **Tone:** Concise, professional, direct. No filler ("Okay, I will...").
- **Safety:** NEVER delete files or revert changes without explicit user confirmation.
- **Verification:** Always verify your work. If you generate code, verify it runs. If you generate text, verify word counts.
- **Access:** ALWAYS provide a way for the user to access/view your work.
  - **Live URL:** Provide the Netlify/Production link.
  - **Local Access:** Provide the `localhost` URL or the absolute file path (e.g. `file:///Users/...`).
  - **Context:** Include this at the end of EVERY response that involves web or UI work.
  - **Requirement:** ALWAYS mention the live remote URL at the end of your message if the project is deployed.
- **Source Control:** If a git repo exists, commit meaningful changes. If you cannot commit, explicitly say why and log it in `_worklog/sessions/`.
- **Prompt + Plan Capture:** For non-trivial builds, save the initial user prompt and a short plan in the session log before building, and summarize changes after.

## 2. Project Tracking & Status
- **Linear:** Use Linear for all project tracking. If you are an agent with Linear tools, use them. If not, ask the user to log items.
- **Status Reporting:** Report your status (starting, blocked, completed) to the Agent Hub if you have shell access (`report-status`).
- **Work Logging:** Log your session details in `_worklog/sessions/` and update `_worklog/LATEST.md` upon completion.

## 3. Project-Specific Directives

### NotebookLM / Study Hub
- **Deep Dives:** All generated deep dive lessons/articles MUST be **7,000+ words**.
- **Sourcing:** **REQUIRED:** Gather **50+ sources** (via iterative prompting or Deep Research mode) *before* generating Deep Dive audio.
- **Content:** Do not produce "meta" summaries ("The article discusses..."). Produce the actual content ("The Habsburgs rose to power by...").
- **Format:** JSON output must be valid. Use `article` key for text content.

### Web Development
- **Deployment:** Log all new projects to Supabase and `projects.json`.
- **Frameworks:** Prefer established patterns found in the repo.
- **Artifacts:** Keep a backup copy of the final built artifact(s) in `_worklog/artifacts/` (timestamped).
- **Netlify Safety:** 
  - When creating a NEW project, ALWAYS create a NEW Netlify site. 
  - NEVER reuse an existing Site ID or existing URL (like `art-discoverer`) unless you are certain it belongs to the current project.
  - Verify `netlify.toml` does not contain hardcoded IDs from copied templates.

## 4. Notifications
- **When to Notify:** Blockers, Completion, Critical Errors.
- **Method 1 (Global):** Use `report-status` — notifications are handled automatically by the Agent Hub server.
  - `report-status --name my-agent blocked "Need help"` → auto-sends Telegram
  - **IMPORTANT: When completing a project with a live URL, ALWAYS include `--url`:**
    - `report-status --name my-agent --url "https://my-app.netlify.app" completed "Deployed and ready for review"`
    - The URL will be sent as a clickable link in the Telegram notification so the user can review on their phone.
  - Dashboard: http://localhost:8767/
- **Method 2 (Mac Pop-up):**
  - **From CandyPop:** Use `~/bin/notify-mac "Message" "Title" "Optional URL"`
  - **From Mac:** Use `curl "http://localhost:12345/?msg=Done&title=Agent"`
