#!/usr/bin/env python3
"""
Supabase Client for Life Management System
Handles all database operations.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, List, Dict, Any
import config

TZ = ZoneInfo(config.TIMEZONE)

# Try to import supabase, gracefully handle if not installed
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: supabase not installed. Database operations will be mocked.")


class SupabaseClient:
    """Client for Supabase database operations"""

    def __init__(self):
        self.client: Optional[Client] = None
        if SUPABASE_AVAILABLE and config.SUPABASE_URL and config.SUPABASE_KEY:
            try:
                self.client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            except Exception as e:
                print(f"Warning: Could not connect to Supabase: {e}")

        # Local cache for when Supabase is unavailable
        self._local_cache = {
            "intentions": {},
            "checkins": [],
            "time_entries": [],
            "focus_blocks": [],
            "spillover": [],
        }

    def _now(self) -> str:
        """Get current timestamp as ISO string"""
        return datetime.now(TZ).isoformat()

    def _today(self) -> str:
        """Get today's date as string"""
        return datetime.now(TZ).strftime("%Y-%m-%d")

    # ==================== Daily Intentions ====================

    async def save_daily_intention(self, one_thing: str, energy_level: str) -> Dict:
        """Save the day's main intention"""
        today = self._today()
        data = {
            "date": today,
            "one_thing": one_thing,
            "energy_level": energy_level,
            "completed": False,
        }

        if self.client:
            try:
                # Upsert to handle multiple submissions in same day
                result = self.client.table("life_daily_intentions").upsert(
                    data, on_conflict="date"
                ).execute()
                return result.data[0] if result.data else data
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback to local cache
        self._local_cache["intentions"][today] = data
        return data

    async def get_today_intention(self) -> Optional[Dict]:
        """Get today's intention"""
        today = self._today()

        if self.client:
            try:
                result = self.client.table("life_daily_intentions").select("*").eq(
                    "date", today
                ).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback to local cache
        return self._local_cache["intentions"].get(today)

    async def mark_intention_complete(self, completed: bool = True) -> bool:
        """Mark today's intention as complete"""
        today = self._today()

        if self.client:
            try:
                self.client.table("life_daily_intentions").update(
                    {"completed": completed}
                ).eq("date", today).execute()
                return True
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback
        if today in self._local_cache["intentions"]:
            self._local_cache["intentions"][today]["completed"] = completed
        return True

    # ==================== Check-ins ====================

    async def save_checkin(self, status: str, current_task: Optional[str] = None) -> Dict:
        """Save a check-in response"""
        data = {
            "timestamp": self._now(),
            "status": status,
            "current_task": current_task,
        }

        if self.client:
            try:
                result = self.client.table("life_checkins").insert(data).execute()
                return result.data[0] if result.data else data
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback
        self._local_cache["checkins"].append(data)
        return data

    async def get_recent_checkins(self, hours: int = 24) -> List[Dict]:
        """Get recent check-ins"""
        cutoff = (datetime.now(TZ) - timedelta(hours=hours)).isoformat()

        if self.client:
            try:
                result = self.client.table("life_checkins").select("*").gte(
                    "timestamp", cutoff
                ).order("timestamp", desc=True).execute()
                return result.data
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback - filter local cache
        return [
            c for c in self._local_cache["checkins"]
            if c["timestamp"] >= cutoff
        ]

    async def get_today_checkins(self) -> List[Dict]:
        """Get today's check-ins"""
        today_start = datetime.now(TZ).replace(hour=0, minute=0, second=0).isoformat()

        if self.client:
            try:
                result = self.client.table("life_checkins").select("*").gte(
                    "timestamp", today_start
                ).order("timestamp", desc=True).execute()
                return result.data
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback
        return [
            c for c in self._local_cache["checkins"]
            if c["timestamp"] >= today_start
        ]

    # ==================== Time Tracking ====================

    async def start_time_entry(self, task_name: str, estimated_minutes: Optional[int] = None) -> Dict:
        """Start a time tracking entry"""
        data = {
            "task_name": task_name,
            "estimated_minutes": estimated_minutes,
            "started_at": self._now(),
            "completed": False,
        }

        if self.client:
            try:
                result = self.client.table("life_time_entries").insert(data).execute()
                return result.data[0] if result.data else data
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback
        data["id"] = len(self._local_cache["time_entries"])
        self._local_cache["time_entries"].append(data)
        return data

    async def stop_time_entry(self, task_name: str, actual_minutes: int) -> Dict:
        """Stop the current time entry"""
        if self.client:
            try:
                # Find the most recent uncompleted entry for this task
                result = self.client.table("life_time_entries").select("*").eq(
                    "task_name", task_name
                ).eq("completed", False).order("started_at", desc=True).limit(1).execute()

                if result.data:
                    entry = result.data[0]
                    self.client.table("life_time_entries").update({
                        "actual_minutes": actual_minutes,
                        "ended_at": self._now(),
                        "completed": True,
                    }).eq("id", entry["id"]).execute()
                    return {"estimated": entry.get("estimated_minutes")}
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback
        for entry in reversed(self._local_cache["time_entries"]):
            if entry["task_name"] == task_name and not entry["completed"]:
                entry["actual_minutes"] = actual_minutes
                entry["ended_at"] = self._now()
                entry["completed"] = True
                return {"estimated": entry.get("estimated_minutes")}

        return {}

    async def get_similar_task_times(self, task_name: str, limit: int = 5) -> List[Dict]:
        """Get historical times for similar tasks"""
        if self.client:
            try:
                # Simple text search (Supabase supports ilike)
                result = self.client.table("life_time_entries").select("*").ilike(
                    "task_name", f"%{task_name}%"
                ).eq("completed", True).order("started_at", desc=True).limit(limit).execute()
                return result.data
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback - simple substring match
        return [
            e for e in self._local_cache["time_entries"]
            if task_name.lower() in e["task_name"].lower() and e["completed"]
        ][:limit]

    # ==================== Focus Blocks ====================

    async def start_focus_block(self, task_name: str, planned_minutes: int) -> Dict:
        """Start a focus block"""
        data = {
            "task_name": task_name,
            "planned_minutes": planned_minutes,
            "started_at": self._now(),
        }

        if self.client:
            try:
                result = self.client.table("life_focus_blocks").insert(data).execute()
                return result.data[0] if result.data else data
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback
        data["id"] = len(self._local_cache["focus_blocks"])
        self._local_cache["focus_blocks"].append(data)
        return data

    async def end_focus_block(self, task_name: str, actual_minutes: Optional[int], rating: int) -> Dict:
        """End a focus block with rating"""
        if self.client:
            try:
                # Find most recent focus block for this task
                result = self.client.table("life_focus_blocks").select("*").eq(
                    "task_name", task_name
                ).is_("ended_at", "null").order("started_at", desc=True).limit(1).execute()

                if result.data:
                    entry = result.data[0]
                    self.client.table("life_focus_blocks").update({
                        "actual_minutes": actual_minutes,
                        "ended_at": self._now(),
                        "rating": rating,
                    }).eq("id", entry["id"]).execute()
                    return entry
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback
        for block in reversed(self._local_cache["focus_blocks"]):
            if block["task_name"] == task_name and not block.get("ended_at"):
                block["actual_minutes"] = actual_minutes
                block["ended_at"] = self._now()
                block["rating"] = rating
                return block

        return {}

    # ==================== Spillover Tasks ====================

    async def add_spillover_task(self, task_name: str, source: str = "manual") -> Dict:
        """Add a task that spilled over"""
        data = {
            "task_name": task_name,
            "original_date": self._today(),
            "source": source,
            "dropped": False,
        }

        if self.client:
            try:
                result = self.client.table("life_spillover").insert(data).execute()
                return result.data[0] if result.data else data
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback
        self._local_cache["spillover"].append(data)
        return data

    async def get_spillover_tasks(self) -> List[Dict]:
        """Get unresolved spillover tasks"""
        if self.client:
            try:
                result = self.client.table("life_spillover").select("*").eq(
                    "dropped", False
                ).is_("rescheduled_to", "null").order("original_date", desc=True).execute()
                return result.data
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback
        return [
            s for s in self._local_cache["spillover"]
            if not s["dropped"] and not s.get("rescheduled_to")
        ]

    # ==================== Weekly Stats ====================

    async def get_weekly_stats(self) -> Dict[str, Any]:
        """Get weekly statistics"""
        week_ago = (datetime.now(TZ) - timedelta(days=7)).isoformat()

        stats = {
            "entries": [],
            "focus_blocks": [],
            "checkins": [],
        }

        if self.client:
            try:
                # Time entries
                result = self.client.table("life_time_entries").select("*").gte(
                    "started_at", week_ago
                ).eq("completed", True).execute()
                stats["entries"] = result.data

                # Focus blocks
                result = self.client.table("life_focus_blocks").select("*").gte(
                    "started_at", week_ago
                ).execute()
                stats["focus_blocks"] = result.data

                # Check-ins
                result = self.client.table("life_checkins").select("*").gte(
                    "timestamp", week_ago
                ).execute()
                stats["checkins"] = result.data
            except Exception as e:
                print(f"Supabase error: {e}")

        # Fallback - use local cache
        if not stats["entries"]:
            stats["entries"] = [
                e for e in self._local_cache["time_entries"]
                if e.get("started_at", "") >= week_ago and e["completed"]
            ]
            stats["focus_blocks"] = [
                f for f in self._local_cache["focus_blocks"]
                if f.get("started_at", "") >= week_ago
            ]
            stats["checkins"] = [
                c for c in self._local_cache["checkins"]
                if c.get("timestamp", "") >= week_ago
            ]

        return stats
