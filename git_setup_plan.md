# Git & GitHub Setup Plan

## Goal
Initialize Git repositories for all active projects and push them to GitHub so they can be used with "Conductor" or other external tools.

## Projects to Sync
1. `substack-dashboard`
2. `reading-dashboard`
3. `project-command-center`
4. `voice-memo-transcriber`
5. `time-tracker`
6. `writing-challenge`
7. `voice-studio`

## Steps
1. **[done]** Initialize Git locally (`git init`) - *Completed in previous step*
2. **[current]** Batch Create GitHub Repositories
    - Use `gh repo create` for each project.
    - We will use "private" visibility by default for personal projects unless instructed otherwise.
3. **[pending]** Commit and Push Code
    - Add all files: `git add .`
    - Create initial commit: `git commit -m "Initial commit"`
    - Push to origin: `git push -u origin main` (or master)

## Permissions & Workflow
- We will try to batch these commands to minimize interruptions.
- `SafeToAutoRun` will be used, but note that the system may still prompt for confirmation on network/shell activities.
