# Health Monitor - Progress Notes

## Last Session: 2026-01-25

### What's Working
- **Background monitoring** via launchd (every 10 min) - `launchctl list | grep health`
- **Pushover alerts** for critical issues (load > 12, memory < 200MB)
- **macOS notifications** for warnings (load spikes, memory spikes)
- **Web dashboard** at http://localhost:8765/dashboard.html
- **Terminal command** `health` (after `source ~/.zshrc`)
- **Aggregated app view** - shows total CPU/memory per app (e.g., Comet: 48% memory across 66 processes)

### To Start Dashboard
```bash
cd ~/.health-monitor && python3 -m http.server 8765
# Then open http://localhost:8765/dashboard.html
```

Or use alias (after sourcing zshrc):
```bash
health-dashboard
```

### Recent Changes
1. Fixed process names - now shows "Comet" instead of truncated paths
2. Added aggregated view - combines all helpers per app
3. Made load threshold relative to CPU cores (12 for 8-core Mac)
4. Improved alert messages to explain what's happening

### Ideas for Next Session
- [ ] See which browser tab uses which resources (hard - need browser's internal task manager)
- [ ] Add button to open Activity Monitor filtered to specific app
- [ ] Maybe integrate with Comet's task manager if it has an API
- [ ] Historical trends - "Comet used 30% more memory today than yesterday"
- [ ] Kill button for runaway processes?

### Files
- `~/.health-monitor/` - data directory (metrics.json, history.json, dashboard.html)
- `~/Library/LaunchAgents/com.z.health-monitor.plist` - background scheduler
- `~/.zshrc` - has `health` and `health-dashboard` aliases

### Quick Commands
```bash
# Check current status
health

# Run collector manually
~/.health-monitor/health-monitor.sh

# Check if launchd is running
launchctl list | grep health

# Stop monitoring
launchctl unload ~/Library/LaunchAgents/com.z.health-monitor.plist

# Restart monitoring
launchctl load ~/Library/LaunchAgents/com.z.health-monitor.plist
```
