#!/usr/bin/env python3
"""
Morning Briefing Generator
Creates the daily morning message with calendar, priorities, and context.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import config

TZ = ZoneInfo(config.TIMEZONE)


async def generate_morning_briefing(db) -> str:
    """Generate the morning briefing message"""
    now = datetime.now(TZ)

    parts = []

    # Header with date and year progress
    day_of_year = now.timetuple().tm_yday
    year_progress = (day_of_year / 365) * 100
    weekday = now.strftime("%A")

    parts.append(
        f"☀️ *Good morning!*\n"
        f"📅 {weekday}, {now.strftime('%B %d, %Y')}\n"
        f"📊 2026 is *{year_progress:.1f}%* complete ({day_of_year}/365 days)"
    )

    # Calendar events (if Google Calendar is connected)
    calendar_events = await get_calendar_events()
    if calendar_events:
        parts.append("\n📆 *Today's Schedule:*")
        for event in calendar_events[:5]:  # Max 5 events
            time_str = event.get("time", "")
            title = event.get("title", "")
            parts.append(f"  • {time_str} - {title}")
    else:
        parts.append("\n📆 No calendar events today (or calendar not connected)")

    # Yesterday's spillover tasks
    spillover = await db.get_spillover_tasks()
    if spillover:
        parts.append(f"\n⚠️ *Spillover from yesterday:* ({len(spillover)} tasks)")
        for task in spillover[:3]:
            parts.append(f"  • {task['task_name']}")
        if len(spillover) > 3:
            parts.append(f"  ...and {len(spillover) - 3} more")

    # Recent patterns (check-in analysis)
    patterns = await analyze_recent_patterns(db)
    if patterns:
        parts.append(f"\n💡 *Pattern alert:* {patterns}")

    # Motivational nudge based on day/energy patterns
    nudge = get_contextual_nudge(now)
    parts.append(f"\n{nudge}")

    return "\n".join(parts)


async def get_calendar_events():
    """
    Fetch today's calendar events from Google Calendar.
    Returns empty list if not configured.
    """
    # TODO: Implement Google Calendar API integration
    # For now, return empty to not block other functionality
    return []


async def analyze_recent_patterns(db) -> str:
    """Analyze recent check-ins for patterns"""
    try:
        checkins = await db.get_recent_checkins(hours=72)  # Last 3 days

        if len(checkins) < 5:
            return ""

        # Count by status
        distracted = sum(1 for c in checkins if c["status"] == "distracted")
        on_track = sum(1 for c in checkins if c["status"] == "on_track")

        # Check for distraction pattern
        if distracted > on_track:
            return "You've been distracted more than focused lately. Consider shorter focus blocks."

        # Check for consistent on-track
        if on_track > len(checkins) * 0.7:
            return "Strong focus streak! Keep the momentum going."

        return ""
    except Exception:
        return ""


def get_contextual_nudge(now: datetime) -> str:
    """Get a contextual motivational nudge"""
    weekday = now.weekday()

    # Monday motivation
    if weekday == 0:
        return "🚀 *Monday energy.* Set the tone for the week. What matters most?"

    # Mid-week
    if weekday == 2:
        return "⚡ *Wednesday.* Halfway through. Time to push or pivot?"

    # Friday
    if weekday == 4:
        return "🎯 *Friday.* Finish strong. What ONE thing would make this week a win?"

    # Weekend
    if weekday in (5, 6):
        return "🌴 *Weekend.* Rest is productive. But if you're working, make it count."

    # Default
    return "💪 *New day, fresh start.* You have more control than you think."


# Standalone test
if __name__ == "__main__":
    import asyncio

    class MockDB:
        async def get_spillover_tasks(self):
            return []

        async def get_recent_checkins(self, hours=72):
            return []

    async def test():
        briefing = await generate_morning_briefing(MockDB())
        print(briefing)

    asyncio.run(test())
