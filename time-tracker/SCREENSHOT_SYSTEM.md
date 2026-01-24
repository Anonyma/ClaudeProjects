# Screenshot Time Tracking System

## Concept

Automatically capture screenshots every 10 seconds (Mac) and periodically (iPhone) to create a visual timeline of your day.

## Mac Implementation

### Option 1: Built into Time Tracker App

Add to `mac-app/app.py`:

```python
import subprocess
from pathlib import Path

SCREENSHOT_DIR = Path.home() / 'Documents' / 'TimeTracker' / 'Screenshots'
SCREENSHOT_INTERVAL = 10  # seconds
SCREENSHOT_ENABLED = os.getenv('ENABLE_SCREENSHOTS', 'false').lower() == 'true'

def _screenshot_loop(self):
    """Background thread for periodic screenshots."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    while self.monitoring and SCREENSHOT_ENABLED:
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = SCREENSHOT_DIR / f"{timestamp}.png"
            
            # Capture screenshot using macOS screencapture
            subprocess.run([
                'screencapture',
                '-x',  # No sound
                '-t', 'png',  # PNG format
                str(screenshot_path)
            ], check=True)
            
            # Optional: Upload to Supabase Storage
            # self.client.upload_screenshot(screenshot_path)
            
        except Exception as e:
            print(f"Screenshot error: {e}")
        
        time.sleep(SCREENSHOT_INTERVAL)
```

Add to `_start_monitoring()`:
```python
self.screenshot_thread = threading.Thread(target=self._screenshot_loop, daemon=True)
self.screenshot_thread.start()
```

### Option 2: Standalone Script

Create `mac-app/screenshot_daemon.py`:

```python
#!/usr/bin/env python3
"""
Continuous screenshot capture for time tracking.
Captures every N seconds and stores locally.
"""

import subprocess
import time
from datetime import datetime
from pathlib import Path

SCREENSHOT_DIR = Path.home() / 'Documents' / 'TimeTracker' / 'Screenshots'
INTERVAL_SECONDS = 10
QUALITY = 50  # PNG compression (or use JPG for smaller files)

def main():
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Starting screenshot capture to {SCREENSHOT_DIR}")
    print(f"Interval: {INTERVAL_SECONDS}s")
    
    while True:
        try:
            # Organize by date
            today = datetime.now().strftime('%Y-%m-%d')
            day_dir = SCREENSHOT_DIR / today
            day_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%H%M%S')
            screenshot_path = day_dir / f"{timestamp}.png"
            
            # Capture
            subprocess.run([
                'screencapture',
                '-x',  # No sound
                '-t', 'png',
                str(screenshot_path)
            ], check=True)
            
            print(f"Captured: {screenshot_path.name}")
            
        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(INTERVAL_SECONDS)

if __name__ == '__main__':
    main()
```

Run as background service:

```bash
# Test first
python3 mac-app/screenshot_daemon.py

# Then create LaunchAgent
cp mac-app/com.timetracker.screenshots.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.timetracker.screenshots.plist
```

### Storage Considerations

**10 seconds interval = 360 screenshots/hour = 8,640 screenshots/day**

Typical sizes:
- PNG (uncompressed): ~1-5 MB each → **8-43 GB/day** 😱
- PNG (compressed): ~200-800 KB each → **1.7-7 GB/day**
- JPG (quality 70): ~100-300 KB each → **860 MB - 2.6 GB/day**

**Recommendations:**
1. Use JPG with quality 70-80
2. Delete screenshots older than 7 days (auto-cleanup)
3. Store on external drive or cloud (Supabase Storage / S3)

### Privacy Safeguards

```python
# Add to config
SCREENSHOT_QUIET_HOURS_START = 23  # 11 PM
SCREENSHOT_QUIET_HOURS_END = 8     # 8 AM
SCREENSHOT_PAUSE_KEYWORDS = ['banking', 'password', 'private browsing']

def should_skip_screenshot():
    hour = datetime.now().hour
    
    # Skip during quiet hours
    if SCREENSHOT_QUIET_HOURS_START <= hour or hour < SCREENSHOT_QUIET_HOURS_END:
        return True
    
    # Skip if certain apps are focused
    # (Can detect via NSWorkspace on macOS)
    
    return False
```

## iPhone Implementation

### Option 1: iOS Shortcut Automation

Create automation in Shortcuts app:
1. **Time of Day** trigger (every hour)
2. **Take Screenshot** action
3. **Save to Photos** → Album "Time Tracker"
4. Optional: **Upload to Supabase Storage**

**Problem:** iOS doesn't allow background screenshot automations every 10 seconds (battery/privacy).

### Option 2: Manual Periodic Captures

**Better approach for iOS:**
- Hourly automation that takes 1 screenshot
- Manual shortcut (Back Tap) for ad-hoc captures
- Focus on Mac for continuous capture

### Option 3: Use Screen Time API

If willing to build a native iOS app:
- Use `ScreenTimeAPI` to track app usage
- Combine with periodic manual screenshots
- Much more battery-efficient

## Viewing Timeline

Create web dashboard (`dashboard/timeline.html`):

```html
<!-- Timeline view with screenshots -->
<div class="timeline">
  <div class="hour" data-hour="14">
    <h3>2:00 PM</h3>
    <div class="screenshots">
      <img src="screenshots/2026-01-23/140000.jpg" />
      <img src="screenshots/2026-01-23/140010.jpg" />
      <!-- ... 360 images ... -->
    </div>
  </div>
</div>
```

Features:
- Hover to see timestamp
- Click to enlarge
- Scrub through timeline like a video
- OCR to search screenshot text (future)
- AI summary of activity (future)

## Quick Start

```bash
cd ~/Desktop/PersonalProjects/ClaudeProjects/time-tracker

# Create screenshot daemon
cat > mac-app/screenshot_daemon.py << 'EOF'
[paste script above]
EOF

chmod +x mac-app/screenshot_daemon.py

# Test for 1 minute
timeout 60 python3 mac-app/screenshot_daemon.py

# Check output
ls -lh ~/Documents/TimeTracker/Screenshots/$(date +%Y-%m-%d)/
```

## Cost Estimate

**Storage (30 days):**
- JPG @ 200 KB/screenshot × 8,640/day × 30 days = ~52 GB/month
- Supabase Storage: ~$5/month for 100 GB
- Or local SSD (free, but need cleanup)

**Worth it?**
- Helps answer "What did I do Tuesday afternoon?"
- Great for time audits
- Useful for ADHD time blindness
- Privacy trade-off to consider

Want me to build this? 🎥
