#!/usr/bin/env python3
"""
Time Tracker - Mac Menu Bar App

A menu bar application that:
- Allows quick activity logging
- Detects AFK (away from keyboard) periods
- Prompts user when returning from AFK
- Sends hourly pings (optional)
- Syncs with Supabase for cross-device access
"""

import rumps
import threading
import time
import requests
from datetime import datetime, timezone, timedelta

from config import (
    AFK_THRESHOLD_SECONDS,
    PING_INTERVAL_MINUTES,
    SKIP_IF_ACTIVITY_WITHIN_MINUTES,
    HEARTBEAT_INTERVAL_SECONDS,
    PUSHOVER_USER_KEY,
    PUSHOVER_API_TOKEN
)
from afk_detector import get_idle_time, format_duration
from supabase_client import TimeTrackerClient


class TimeTrackerApp(rumps.App):
    """Menu bar application for time tracking."""

    def __init__(self):
        super().__init__(
            name="Time Tracker",
            title="⏱",
            quit_button=None
        )

        # Initialize client
        self.client = TimeTrackerClient()

        # State
        self.last_activity_text = None
        self.is_afk = False
        self.afk_started_at = None
        self.current_ping_id = None
        self.last_ping_time = None

        # Build menu
        self.menu = [
            rumps.MenuItem("Log Activity...", callback=self.prompt_log_activity),
            rumps.MenuItem("Last: None", callback=None, key='l'),
            None,  # Separator
            rumps.MenuItem("Send Ping Now", callback=self.manual_ping),
            rumps.MenuItem("Open Dashboard", callback=self.open_dashboard),
            None,
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

        # Load last activity
        self._update_last_activity_display()

        # Start background monitoring
        self._start_monitoring()

    def _start_monitoring(self):
        """Start background threads for AFK detection and heartbeat."""
        # AFK monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def _monitor_loop(self):
        """Background loop for AFK detection and periodic pings."""
        last_heartbeat = time.time()
        last_ping_check = time.time()

        while self.monitoring:
            try:
                now = time.time()
                idle_seconds = get_idle_time()

                # AFK detection
                if idle_seconds >= AFK_THRESHOLD_SECONDS:
                    if not self.is_afk:
                        # Just went AFK
                        self.is_afk = True
                        self.afk_started_at = datetime.now(timezone.utc) - timedelta(seconds=idle_seconds)
                        self.title = "💤"  # Update icon to show AFK
                        self.client.update_device_state(
                            device='mac',
                            is_afk=True,
                            afk_started_at=self.afk_started_at
                        )
                else:
                    if self.is_afk:
                        # Just returned from AFK
                        afk_duration = datetime.now(timezone.utc) - self.afk_started_at
                        self.is_afk = False
                        self.title = "⏱"  # Reset icon

                        # Update device state
                        self.client.update_device_state(device='mac', is_afk=False)

                        # Prompt if AFK was significant (> 1 minute)
                        if afk_duration.total_seconds() > 60:
                            self._prompt_afk_return(afk_duration)

                # Heartbeat
                if now - last_heartbeat >= HEARTBEAT_INTERVAL_SECONDS:
                    self.client.update_device_state(device='mac', is_afk=self.is_afk)
                    last_heartbeat = now

                # Hourly ping check
                if now - last_ping_check >= 60:  # Check every minute
                    self._check_hourly_ping()
                    last_ping_check = now

            except Exception as e:
                print(f"Monitor error: {e}")

            time.sleep(5)  # Check every 5 seconds

    def _check_hourly_ping(self):
        """Check if it's time to send an hourly ping."""
        now = datetime.now()

        # Only ping on the hour (with 2-minute window)
        if now.minute > 2:
            return

        # Don't ping if we already did this hour
        if self.last_ping_time and self.last_ping_time.hour == now.hour:
            return

        # Don't ping if recent activity
        if self.client.should_skip_ping(minutes=SKIP_IF_ACTIVITY_WITHIN_MINUTES):
            self.last_ping_time = now
            return

        # Create and show ping
        self.last_ping_time = now
        self._trigger_ping()

    def _trigger_ping(self):
        """Trigger a ping notification."""
        # Create ping record
        ping = self.client.create_ping()
        if ping:
            self.current_ping_id = ping['id']

            # Show local notification/prompt
            rumps.notification(
                title="What are you doing?",
                subtitle="Time to log your activity",
                message="Click to log what you're working on",
                sound=True
            )

            # Send Pushover notification if configured
            self._send_pushover_notification(ping['id'])

    def _send_pushover_notification(self, ping_id: str):
        """Send push notification via Pushover."""
        if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
            return

        try:
            # Create deep link to iOS Shortcut
            shortcut_url = f"shortcuts://run-shortcut?name=Log%20Activity&input=text&text={ping_id}"

            requests.post(
                'https://api.pushover.net/1/messages.json',
                data={
                    'token': PUSHOVER_API_TOKEN,
                    'user': PUSHOVER_USER_KEY,
                    'title': 'What are you doing?',
                    'message': 'Tap to log your activity',
                    'url': shortcut_url,
                    'url_title': 'Log Activity',
                    'priority': 0,
                    'sound': 'pushover'
                },
                timeout=10
            )
        except Exception as e:
            print(f"Pushover error: {e}")

    def _prompt_afk_return(self, duration: timedelta):
        """Show prompt when user returns from AFK."""
        minutes = int(duration.total_seconds() / 60)
        duration_str = format_duration(duration.total_seconds())

        # Use rumps window for input
        response = rumps.Window(
            title="Welcome Back!",
            message=f"You were away for {duration_str}.\nWhat were you doing?",
            default_text="",
            ok="Log",
            cancel="Skip",
            dimensions=(300, 100)
        ).run()

        if response.clicked and response.text.strip():
            # Log the AFK activity with backdated timestamp
            self.client.log_activity(
                activity_text=response.text.strip(),
                device='mac',
                entry_type='afk_return',
                timestamp=self.afk_started_at
            )
            self._update_last_activity(response.text.strip())

        self.afk_started_at = None

    def prompt_log_activity(self, _):
        """Show prompt for manual activity logging."""
        response = rumps.Window(
            title="Log Activity",
            message="What are you doing right now?",
            default_text="",
            ok="Log",
            cancel="Cancel",
            dimensions=(300, 100)
        ).run()

        if response.clicked and response.text.strip():
            activity_text = response.text.strip()

            # Check if responding to a ping
            ping_id = self.current_ping_id
            entry_type = 'ping_response' if ping_id else 'manual'

            result = self.client.log_activity(
                activity_text=activity_text,
                device='mac',
                entry_type=entry_type,
                ping_id=ping_id
            )

            if result:
                self._update_last_activity(activity_text)
                rumps.notification(
                    title="Activity Logged",
                    subtitle="",
                    message=activity_text[:50],
                    sound=False
                )

                # Clear current ping
                self.current_ping_id = None
            else:
                rumps.notification(
                    title="Error",
                    subtitle="Failed to log activity",
                    message="Check your internet connection",
                    sound=True
                )

    def manual_ping(self, _):
        """Manually trigger a ping."""
        self._trigger_ping()

    def _update_last_activity(self, text: str):
        """Update the displayed last activity."""
        self.last_activity_text = text
        # Truncate for menu display
        display = text[:30] + "..." if len(text) > 30 else text
        self.menu["Last: None"].title = f"Last: {display}"

    def _update_last_activity_display(self):
        """Load and display the last activity from database."""
        try:
            activity = self.client.get_last_activity()
            if activity:
                self._update_last_activity(activity['activity_text'])
        except Exception as e:
            print(f"Error loading last activity: {e}")

    def open_dashboard(self, _):
        """Open the web dashboard."""
        import subprocess
        dashboard_path = str(__file__).replace('mac-app/app.py', 'dashboard/index.html')
        subprocess.run(['open', dashboard_path])

    def quit_app(self, _):
        """Clean shutdown."""
        self.monitoring = False
        rumps.quit_application()


def main():
    """Entry point."""
    print("Starting Time Tracker...")
    print(f"AFK threshold: {AFK_THRESHOLD_SECONDS}s")
    print(f"Ping interval: {PING_INTERVAL_MINUTES}m")

    app = TimeTrackerApp()
    app.run()


if __name__ == '__main__':
    main()
