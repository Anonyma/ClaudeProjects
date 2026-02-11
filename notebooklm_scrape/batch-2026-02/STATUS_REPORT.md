# NotebookLM Batch - Status Report
**Updated:** 2026-02-11 13:30

## Current State: Phase 1 COMPLETE, Phase 2 BLOCKED on remote access

### Phase 1: Source Research - DONE
All 8 source lists generated on CandyPop at `~/Projects/notebooklm/batch-2026-02/sources/`:

| Topic | Sources File | Lines | Status |
|-------|-------------|-------|--------|
| BBB Crossing Technologies | bbb-crossing_sources.md | 132 | Done |
| CRISPR 2.0 | crispr-precision_sources.md | 145 | Done |
| Japanese History | japanese-history_sources.md | 140 | Done |
| Neuroscience | neuroscience-rigorous_sources.md | 205 | Done |
| Architecture | architecture-parametric_sources.md | 141 | Done |
| Microbiome | microbiome_sources.md | 209 | Done |
| Senolytics | senolytics_sources.md | 114 | Done |
| Philosophy of Tech | philosophy-tech_sources.md | ??? | Check |

### Phase 2: NotebookLM Notebook Creation - NOT STARTED
**Blocked on:** Remote desktop access to CandyPop (needed for Playwright browser automation)

### What Went Wrong
1. `claude -p` (single-prompt mode) exited after Phase 1 instead of continuing
2. Progress.json was not updated by the agent
3. No Telegram notifications were sent (agent didn't report blocked/completed status)

### What Needs to Happen Next

#### Step 1: Set up remote access to CandyPop (user action)
```bash
# SSH into CandyPop
ssh CandyPop

# Set/verify your Linux password (needed for sudo)
sudo passwd z

# Install lightweight desktop for VNC/xRDP sessions
sudo apt install -y openbox xterm

# Create VNC startup
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/sh
xsetroot -solid "#2d2d2d"
openbox &
xterm -fa "Monospace" -fs 12 &
exec sleep infinity
EOF
chmod +x ~/.vnc/xstartup

# Set VNC password (separate from Linux password)
vncpasswd

# Start VNC server
vncserver :2 -localhost yes -geometry 1920x1080 -depth 24
```

From Mac, connect with:
```bash
# SSH tunnel + VNC viewer
candypop-vnc start
# Or manually: ssh -f -N -L 5902:localhost:5902 CandyPop && open vnc://localhost:5902
```

#### Step 2: Refresh Playwright login (in remote desktop session)
```bash
cd ~/Projects/notebooklm
export DISPLAY=:2
python3.12 generate_deep_dive.py --login
# Log into Google when Chrome opens
```

#### Step 3: Restart the batch agent properly
```bash
# From Mac, run:
ssh CandyPop "export PATH=\$HOME/.local/bin:\$HOME/bin:\$PATH && \
  tmux kill-session -t nlm-batch 2>/dev/null && \
  tmux new-session -d -s nlm-batch -c ~/Projects/notebooklm && \
  tmux send-keys -t nlm-batch 'export PATH=\$HOME/.local/bin:\$HOME/bin:\$PATH && export DISPLAY=:2' Enter"

# Then start claude in the tmux session
ssh CandyPop "tmux send-keys -t nlm-batch 'claude --dangerously-skip-permissions' Enter"

# Then paste the Phase 2 prompt (or use the restart script)
```

The Phase 2 prompt should be:
```
Phase 1 (source research) is complete. Source lists are in batch-2026-02/sources/.
Now execute Phase 2: Create notebooks on NotebookLM and add sources.
For each topic in batch-2026-02/topics.json:
1. Use generate_deep_dive.py or Playwright to create a notebook on NotebookLM
2. Add the URLs from the source list (target 50+ per notebook)
3. Update batch-2026-02/progress.json after each notebook
4. Report status: report-status --name "nlm-{topic_id}" --project "notebooklm-batch" running "Creating notebook: {title}"
If Playwright login is expired, report blocked and STOP.
After all notebooks are created, proceed to Phase 3 (audio generation).
```

### Monitoring
- **From Mac:** `bash /Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape/batch-2026-02/monitor.sh`
- **Agent hub:** `agents | grep nlm`
- **Telegram:** Notifications fire on blocked/error/completed
- **SSH into tmux:** `ssh CandyPop -t 'tmux attach -t nlm-batch'`

### Files on CandyPop
```
~/Projects/notebooklm/batch-2026-02/
├── TASK.md                    # Full task specification
├── topics.json                # 8 topics with subtopics and prompts
├── progress.json              # Progress tracker (needs updating)
├── sources/                   # Source lists (Phase 1 output)
│   ├── bbb-crossing_sources.md
│   ├── crispr-precision_sources.md
│   ├── japanese-history_sources.md
│   ├── neuroscience-rigorous_sources.md
│   ├── architecture-parametric_sources.md
│   ├── microbiome_sources.md
│   ├── senolytics_sources.md
│   └── philosophy-tech_sources.md
├── agent.log                  # Agent output log
├── monitor.sh                 # Progress monitor
└── start-on-candypop.sh       # Launch script
```

### Known Issues
- VNC server is running on :2 but user never set a VNC password — run `vncpasswd` on CandyPop
- `apt` works fine but needs full PATH; SSH sessions may need `export PATH=/usr/bin:$PATH`
- Playwright login (Google auth) was last refreshed around Feb 8, likely expired
- NotebookLM daily audio quota: ~3 generations/day = ~8-10 days for all 24 deep dives
