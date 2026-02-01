#!/usr/bin/env python3
"""
Life Management System - CLI Interface
Quick command-line interface for testing and manual use.

Usage:
  python life_cli.py briefing    # Show morning briefing
  python life_cli.py one "task"  # Set ONE thing
  python life_cli.py checkin     # Quick check-in prompt
  python life_cli.py start "task" [estimate]  # Start task
  python life_cli.py stop        # Stop current task
  python life_cli.py status      # Show current status
  python life_cli.py stats       # Weekly stats
"""
import asyncio
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import config
from daily_briefing import generate_morning_briefing
from supabase_client import SupabaseClient

TZ = ZoneInfo(config.TIMEZONE)

# Global state
current_task = None
task_start_time = None


async def cmd_briefing(db):
    """Show morning briefing"""
    briefing = await generate_morning_briefing(db)
    # Convert markdown to plain text for CLI
    briefing = briefing.replace("*", "")
    print(briefing)


async def cmd_one(db, task: str):
    """Set ONE thing for today"""
    energy = input("Energy level (high/medium/low): ").strip().lower()
    if energy not in ("high", "medium", "low"):
        energy = "medium"

    await db.save_daily_intention(task, energy)
    print(f"\n✓ ONE thing set: {task}")
    print(f"  Energy: {energy}")


async def cmd_checkin(db):
    """Quick check-in"""
    global current_task

    intention = await db.get_today_intention()
    one_thing = intention.get("one_thing", "not set") if intention else "not set"

    print(f"\n⏰ Check-in time!")
    print(f"   ONE thing: {one_thing}")
    if current_task:
        elapsed = (datetime.now(TZ) - task_start_time).total_seconds() / 60
        print(f"   Current task: {current_task} ({int(elapsed)} min)")

    print("\nHow's it going?")
    print("  1. On track")
    print("  2. Distracted")
    print("  3. Switched tasks")
    print("  4. Need break")

    choice = input("\nChoice (1-4): ").strip()
    status_map = {"1": "on_track", "2": "distracted", "3": "switched", "4": "break"}
    status = status_map.get(choice, "on_track")

    await db.save_checkin(status, current_task)
    print(f"\n✓ Logged: {status}")


async def cmd_start(db, task: str, estimate: int = None):
    """Start tracking a task"""
    global current_task, task_start_time

    if current_task:
        print(f"⚠️  Stopping previous task: {current_task}")
        await cmd_stop(db)

    current_task = task
    task_start_time = datetime.now(TZ)
    await db.start_time_entry(task, estimate)

    print(f"\n🎬 Started: {task}")
    if estimate:
        print(f"   Estimated: {estimate} min")


async def cmd_stop(db):
    """Stop current task"""
    global current_task, task_start_time

    if not current_task:
        print("No task currently being tracked.")
        return

    elapsed = int((datetime.now(TZ) - task_start_time).total_seconds() / 60)
    result = await db.stop_time_entry(current_task, elapsed)

    print(f"\n⏹️  Stopped: {current_task}")
    print(f"   Duration: {elapsed} min")

    if result.get("estimated"):
        diff = elapsed - result["estimated"]
        if diff > 0:
            print(f"   📊 Took {diff} min longer than estimated")
        elif diff < 0:
            print(f"   📊 Finished {-diff} min faster!")

    current_task = None
    task_start_time = None


async def cmd_status(db):
    """Show current status"""
    global current_task, task_start_time

    print("\n📊 Current Status")
    print("=" * 40)

    # Today's ONE thing
    intention = await db.get_today_intention()
    if intention:
        status = "✓" if intention.get("completed") else "○"
        print(f"🎯 ONE thing: {intention['one_thing']} {status}")

    # Current task
    if current_task:
        elapsed = (datetime.now(TZ) - task_start_time).total_seconds() / 60
        print(f"⏱️  Current: {current_task} ({int(elapsed)} min)")
    else:
        print("⏱️  No task being tracked")

    # Today's check-ins
    checkins = await db.get_today_checkins()
    if checkins:
        on_track = sum(1 for c in checkins if c["status"] == "on_track")
        print(f"📋 Check-ins: {on_track}/{len(checkins)} on track")

    # Year progress
    now = datetime.now(TZ)
    year_progress = (now.timetuple().tm_yday / 365) * 100
    print(f"\n📅 2026 is {year_progress:.1f}% complete")


async def cmd_stats(db):
    """Show weekly stats"""
    stats = await db.get_weekly_stats()

    print("\n📊 Weekly Stats (Last 7 days)")
    print("=" * 40)

    if not stats["entries"]:
        print("No time entries yet. Start tracking with 'start'!")
        return

    # Total time
    total = sum(e.get("actual_minutes", 0) for e in stats["entries"])
    print(f"⏱️  Total tracked: {total} min ({total/60:.1f} hours)")

    # Estimation accuracy
    with_estimates = [e for e in stats["entries"] if e.get("estimated_minutes")]
    if with_estimates:
        diffs = [(e["actual_minutes"] - e["estimated_minutes"]) for e in with_estimates]
        avg_diff = sum(diffs) / len(diffs)
        if avg_diff > 0:
            print(f"📊 Avg underestimate: {abs(avg_diff):.0f} min")
        else:
            print(f"📊 Avg overestimate: {abs(avg_diff):.0f} min")

    # Focus blocks
    focus = stats.get("focus_blocks", [])
    if focus:
        total_focus = sum(f.get("actual_minutes", 0) for f in focus)
        print(f"🎯 Focus blocks: {len(focus)} ({total_focus} min)")

    # Check-ins
    checkins = stats.get("checkins", [])
    if checkins:
        on_track = sum(1 for c in checkins if c["status"] == "on_track")
        distracted = sum(1 for c in checkins if c["status"] == "distracted")
        print(f"✅ On track: {on_track} | 😵 Distracted: {distracted}")


def print_help():
    """Print usage help"""
    print(__doc__)


async def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1].lower()
    db = SupabaseClient()

    if cmd == "briefing":
        await cmd_briefing(db)
    elif cmd == "one" and len(sys.argv) >= 3:
        await cmd_one(db, " ".join(sys.argv[2:]))
    elif cmd == "checkin":
        await cmd_checkin(db)
    elif cmd == "start" and len(sys.argv) >= 3:
        task = sys.argv[2]
        estimate = int(sys.argv[3]) if len(sys.argv) >= 4 else None
        await cmd_start(db, task, estimate)
    elif cmd == "stop":
        await cmd_stop(db)
    elif cmd == "status":
        await cmd_status(db)
    elif cmd == "stats":
        await cmd_stats(db)
    else:
        print_help()


if __name__ == "__main__":
    asyncio.run(main())
