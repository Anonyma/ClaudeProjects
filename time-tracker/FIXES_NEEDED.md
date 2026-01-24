# Time Tracker Fixes

## Issue 1: Hourly Pings Not Sending

**Problem:** Pings only send in a 2-minute window (XX:00-XX:02). If the check runs later, no notification.

**Fix in `mac-app/app.py` line ~125:**

Change from:
```python
def _check_hourly_ping(self):
    """Check if it's time to send an hourly ping."""
    now = datetime.now()

    # Only ping on the hour (with 2-minute window)
    if now.minute > 2:
        return

    # Don't ping if we already did this hour
    if self.last_ping_time and self.last_ping_time.hour == now.hour:
        return
```

To:
```python
def _check_hourly_ping(self):
    """Check if it's time to send an hourly ping."""
    now = datetime.now()

    # Don't ping if we already did this hour
    if self.last_ping_time:
        time_since_last = (now - self.last_ping_time).total_seconds() / 60
        if time_since_last < 60:  # Less than 60 minutes
            return

    # Check if we're close to an hour mark (within 5 minutes)
    if now.minute > 5:
        return
```

This gives a 5-minute window instead of 2, and properly tracks time between pings.

## Issue 2: Silent Error Handling

**Problem:** Pushover errors are swallowed by try/except with only a print statement (not logged).

**Fix in `mac-app/app.py` line ~169:**

Change from:
```python
except Exception as e:
    print(f"Pushover error: {e}")
```

To:
```python
except Exception as e:
    print(f"Pushover error: {e}")
    import traceback
    traceback.print_exc()
    # Also save to error log
    with open('/tmp/timetracker.error.log', 'a') as f:
        f.write(f"{datetime.now()}: Pushover error: {e}\n")
        traceback.print_exc(file=f)
```

## Issue 3: No iOS Shortcut Verification

Need to verify that the "Log Activity" iOS Shortcut exists and has the correct name (case-sensitive!).

Check on iPhone:
1. Open Shortcuts app
2. Look for shortcut named exactly: **"Log Activity"** (not "log activity" or "Log activity")
3. If missing, follow: `ios-shortcut/README.md`

## How to Apply Fixes

```bash
# Backup current version
cp mac-app/app.py mac-app/app.py.backup

# Edit the file (apply fixes above)
nano mac-app/app.py

# Restart the app
launchctl unload ~/Library/LaunchAgents/com.timetracker.agent.plist
launchctl load ~/Library/LaunchAgents/com.timetracker.agent.plist

# Monitor for issues
tail -f /tmp/timetracker.error.log
```

## Test After Fixing

1. Manual ping test:
   - Click menu bar icon → "Send Ping Now"
   - Should get Pushover notification immediately

2. Check logs:
   ```bash
   tail -f /tmp/timetracker.log /tmp/timetracker.error.log
   ```

3. Verify iOS shortcut opens when tapping notification
