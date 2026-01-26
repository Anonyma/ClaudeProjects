# Work Log System

Central log of all agent work sessions across projects.

## Structure

```
_worklog/
├── README.md           # This file
├── sessions/           # Individual session logs
│   ├── 2026-01-26-health-monitor.md
│   ├── 2026-01-25-brainstormrr.md
│   └── ...
└── LATEST.md           # Quick view of recent activity
```

## For Agents: How to Log

After completing work on any project, append to the session log:

```bash
# Create/append to today's session log
cat >> /Users/z/Desktop/PersonalProjects/ClaudeProjects/_worklog/sessions/$(date +%Y-%m-%d)-PROJECT.md << 'EOF'

## Session: [TIME]
**Project:** [project-name]
**Status:** [completed/blocked/in-progress]

### What was done:
- Item 1
- Item 2

### Known issues:
- Issue 1

### Next steps:
- Step 1

### Files changed:
- `path/to/file1`
- `path/to/file2`

---
EOF
```

## Quick Commands

```bash
# See recent activity
cat /Users/z/Desktop/PersonalProjects/ClaudeProjects/_worklog/LATEST.md

# See all sessions for a project
ls _worklog/sessions/*health-monitor*

# Update LATEST.md
echo "Last: $(date) - [project] - [status]" >> _worklog/LATEST.md
```
