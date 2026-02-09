#!/usr/bin/env python3
"""
Supabase client wrapper for Time Tracker.
"""

import requests
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from config import SUPABASE_URL, SUPABASE_ANON_KEY


class TimeTrackerClient:
    """Client for Time Tracker Supabase API."""

    def __init__(self):
        self.base_url = f"{SUPABASE_URL}/rest/v1"
        self.headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

    def _request(self, method: str, endpoint: str, data: dict = None) -> Optional[Any]:
        """Make a request to Supabase."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            if response.text:
                return response.json()
            return None
        except requests.exceptions.RequestException as e:
            print(f"Supabase request error: {e}")
            return None

    def log_activity(
        self,
        activity_text: str,
        input_method: str = 'text',
        device: str = 'mac',
        entry_type: str = 'manual',
        ping_id: str = None,
        tags: List[str] = None,
        timestamp: datetime = None
    ) -> Optional[dict]:
        """
        Log an activity entry.

        Args:
            activity_text: What the user was doing
            input_method: 'text', 'voice', or 'screenshot'
            device: 'mac', 'iphone', or 'web'
            entry_type: 'manual', 'ping_response', or 'afk_return'
            ping_id: UUID of ping being responded to (if any)
            tags: List of tags
            timestamp: Override timestamp (for AFK backfill)

        Returns:
            dict: Created activity log or None on error
        """
        data = {
            'activity_text': activity_text,
            'input_method': input_method,
            'device': device,
            'entry_type': entry_type
        }

        if ping_id:
            data['ping_id'] = ping_id
        if tags:
            data['tags'] = tags
        if timestamp:
            data['timestamp'] = timestamp.isoformat()

        result = self._request('POST', 'activity_logs', data)
        if result and len(result) > 0:
            return result[0]
        return None

    def get_recent_activities(self, limit: int = 10) -> List[dict]:
        """Get recent activity logs."""
        result = self._request('GET', f'activity_logs?order=timestamp.desc&limit={limit}')
        return result if result else []

    def get_last_activity(self) -> Optional[dict]:
        """Get the most recent activity log."""
        activities = self.get_recent_activities(limit=1)
        return activities[0] if activities else None

    def get_last_activity_time(self) -> Optional[datetime]:
        """Get timestamp of most recent activity."""
        activity = self.get_last_activity()
        if activity and 'timestamp' in activity:
            return datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
        return None

    def should_skip_ping(self, minutes: int = 15) -> bool:
        """Check if we should skip ping due to recent activity."""
        last_time = self.get_last_activity_time()
        if not last_time:
            return False

        now = datetime.now(timezone.utc)
        diff = (now - last_time).total_seconds() / 60
        return diff < minutes

    def update_device_state(
        self,
        device: str = 'mac',
        is_afk: bool = False,
        afk_started_at: datetime = None
    ) -> bool:
        """
        Update device state (for AFK tracking).

        Args:
            device: Device identifier
            is_afk: Whether device is currently AFK
            afk_started_at: When AFK period started

        Returns:
            bool: Success
        """
        data = {
            'is_afk': is_afk,
            'last_seen_at': datetime.now(timezone.utc).isoformat()
        }

        if afk_started_at:
            data['afk_started_at'] = afk_started_at.isoformat()
        elif not is_afk:
            data['afk_started_at'] = None

        # Use PATCH with filter to update existing row
        result = self._request(
            'PATCH',
            f'device_state?device=eq.{device}',
            data
        )
        return result is not None

    def create_ping(self) -> Optional[dict]:
        """Create a new ping record."""
        data = {
            'status': 'pending',
            'scheduled_at': datetime.now(timezone.utc).isoformat()
        }
        result = self._request('POST', 'pings', data)
        if result and len(result) > 0:
            return result[0]
        return None

    def snooze_ping(self, ping_id: str, scheduled_at: datetime) -> bool:
        """Update a ping's scheduled time after snoozing."""
        if not ping_id:
            return False
        data = {
            'status': 'pending',
            'scheduled_at': scheduled_at.astimezone(timezone.utc).isoformat()
        }
        result = self._request('PATCH', f'pings?id=eq.{ping_id}', data)
        return result is not None

    def answer_ping(
        self,
        ping_id: str,
        activity_text: str,
        device: str = 'mac',
        input_method: str = 'text'
    ) -> Optional[dict]:
        """
        Answer a ping by logging activity and updating ping status.

        Args:
            ping_id: UUID of the ping
            activity_text: What user was doing
            device: Device answering
            input_method: How activity was entered

        Returns:
            dict: Created activity log or None
        """
        # First log the activity
        activity = self.log_activity(
            activity_text=activity_text,
            input_method=input_method,
            device=device,
            entry_type='ping_response',
            ping_id=ping_id
        )

        if activity:
            # Update ping status
            self._request(
                'PATCH',
                f'pings?id=eq.{ping_id}',
                {
                    'status': 'answered',
                    'answered_by_device': device,
                    'answered_at': datetime.now(timezone.utc).isoformat(),
                    'activity_log_id': activity['id']
                }
            )

        return activity

    def get_pending_pings(self) -> List[dict]:
        """Get all pending pings."""
        result = self._request('GET', 'pings?status=eq.pending&order=scheduled_at.desc')
        return result if result else []

    def get_settings(self) -> Optional[dict]:
        """Get user settings."""
        result = self._request('GET', 'time_tracker_settings?id=eq.1')
        if result and len(result) > 0:
            return result[0]
        return None


if __name__ == '__main__':
    # Test the client
    client = TimeTrackerClient()

    print("Testing Supabase connection...")

    # Test logging
    result = client.log_activity(
        activity_text="Testing Time Tracker client",
        device='mac',
        entry_type='manual',
        tags=['test']
    )

    if result:
        print(f"Logged activity: {result['id']}")
    else:
        print("Failed to log activity - check Supabase tables exist")

    # Test getting recent
    recent = client.get_recent_activities(limit=5)
    print(f"\nRecent activities: {len(recent)}")
    for a in recent:
        print(f"  - {a['timestamp'][:16]}: {a['activity_text'][:50]}")
