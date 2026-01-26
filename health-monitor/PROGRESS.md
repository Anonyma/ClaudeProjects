# Health Monitor - Progress Notes

## Last Session: 2026-01-26

### Current Status: Working (with one known issue)

The system health monitor is functional and collecting data every 60 seconds. Dashboard displays data but **refresh button doesn't update to latest data** - this needs debugging.

---

## What's Working

1. **Background data collection** - runs every 60 sec via launchd loop
2. **Pushover alerts** - critical issues (load > 1.5x CPU cores, memory < 200MB)
3. **macOS notifications** - warnings (load spikes, memory spikes, new top apps)
4. **Web dashboard** - shows health summary, metrics, aggregated app usage
5. **Terminal command** - `health` shows current stats
6. **Aggregated app view** - combines all processes per app (e.g., "Comet: 48% memory, 66 processes")

---

## Known Issue: Dashboard Refresh Not Working

**Problem:** Clicking "Refresh" button shows stale data ("Updated 3m ago") even though metrics.json is being updated every 60 seconds.

**What we tried:**
- Changed launchd StartInterval (didn't trigger reliably)
- Switched to a self-looping script (collector-loop.sh) - this works, data IS being collected
- The issue is likely in the dashboard's JavaScript fetch caching

**Likely fix needed:**
- Check if browser is caching the fetch request
- The dashboard already adds `?timestamp` to bust cache, but may need headers
- Look at `loadMetrics()` function in dashboard.html around line 301

**Debug steps:**
```bash
# Check if data is fresh
cat ~/.health-monitor/metrics.json | jq '.timestamp'

# Compare with current time
date -u +"%Y-%m-%dT%H:%M:%SZ"

# If timestamps match, issue is in dashboard JS fetch
# If timestamps don't match, issue is in collector
```

---

## Architecture

```
~/.health-monitor/
├── health-monitor.sh      # Main collector script
├── collector-loop.sh      # Wrapper that runs collector every 60s
├── dashboard.html         # Web UI
├── metrics.json           # Current snapshot
├── history.json           # Rolling 24h history
├── alerts.log             # Alert history
├── stdout.log             # Collector output
└── stderr.log             # Collector errors

~/Library/LaunchAgents/
├── com.z.health-monitor.plist        # Runs collector-loop.sh
└── com.z.health-monitor-server.plist # Serves dashboard on :8765
```

---

## Quick Commands

```bash
# Check current status (runs collector + shows stats)
health

# Open dashboard
health-dashboard
# Or directly: http://localhost:8765/dashboard.html

# Check if services are running
launchctl list | grep health-monitor

# Restart collector
launchctl unload ~/Library/LaunchAgents/com.z.health-monitor.plist
launchctl load ~/Library/LaunchAgents/com.z.health-monitor.plist

# Restart web server
launchctl unload ~/Library/LaunchAgents/com.z.health-monitor-server.plist
launchctl load ~/Library/LaunchAgents/com.z.health-monitor-server.plist

# Manual collection
~/.health-monitor/health-monitor.sh

# Check collection is happening
tail -f ~/.health-monitor/stdout.log
```

---

## Features Implemented

- [x] CPU load monitoring (relative to core count)
- [x] Memory usage tracking
- [x] Disk usage
- [x] Top processes by CPU/memory
- [x] **Aggregated app view** - totals per app across all helper processes
- [x] Pushover alerts for critical issues
- [x] macOS notifications for warnings
- [x] 24-hour history with charts
- [x] Plain English health summary ("System Healthy" / "System Overloaded")

---

## Ideas for Future

- [ ] **Fix refresh button** (priority - see Known Issue above)
- [ ] See which browser tab uses which resources (needs browser API access)
- [ ] Kill button for runaway processes
- [ ] Historical trends ("Comet used 30% more memory today than yesterday")
- [ ] Slack/Discord notifications option
- [ ] Menu bar app instead of dashboard

---

## Key Files to Edit

| File | Purpose |
|------|---------|
| `~/.health-monitor/health-monitor.sh` | Data collection logic, alert thresholds |
| `~/.health-monitor/dashboard.html` | Web UI, refresh logic (check `loadMetrics()`) |
| `~/.health-monitor/collector-loop.sh` | Loop wrapper, change `sleep 60` for different interval |
| `~/Library/LaunchAgents/com.z.health-monitor.plist` | Background service config |

---

## Thresholds (in health-monitor.sh)

- **Load critical:** > 1.5x CPU cores (12 for 8-core Mac)
- **Memory critical:** < 200MB available
- **App memory critical:** Single app > 50% memory
- **Load anomaly:** 2x higher than 1-hour baseline
- **Memory spike:** > 20% increase in collection interval
