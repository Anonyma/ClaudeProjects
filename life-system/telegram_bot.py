#!/usr/bin/env python3
"""
Life Management System - Telegram Bot
Main entry point for the bot that handles:
- Morning briefings
- Hourly check-ins
- Time tracking
- Focus blocks
"""
import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import config
from daily_briefing import generate_morning_briefing
from supabase_client import SupabaseClient

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Conversation states
(
    WAITING_ONE_THING,
    WAITING_ENERGY_LEVEL,
    WAITING_TASK_NAME,
    WAITING_ESTIMATE,
    WAITING_FOCUS_DURATION,
    WAITING_FOCUS_RATING,
) = range(6)

# Timezone
TZ = ZoneInfo(config.TIMEZONE)


class LifeBot:
    def __init__(self):
        self.db = SupabaseClient()
        self.current_task = None
        self.task_start_time = None
        self.focus_block_active = False
        self.focus_block_task = None
        self.focus_block_start = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "👋 Hey Z! I'm your Life Management Bot.\n\n"
            "Commands:\n"
            "/morning - Get your morning briefing\n"
            "/one - Set your ONE thing for today\n"
            "/checkin - Quick status check\n"
            "/start_task - Start tracking a task\n"
            "/stop_task - Stop current task\n"
            "/focus - Start a focus block\n"
            "/status - See what you're working on\n"
            "/stats - Weekly time stats\n\n"
            "I'll also ping you hourly for check-ins!"
        )

    async def morning_briefing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send morning briefing"""
        briefing = await generate_morning_briefing(self.db)
        await update.message.reply_text(briefing, parse_mode="Markdown")

        # Ask for the ONE thing
        await update.message.reply_text(
            "🎯 *What's your ONE thing today?*\n"
            "The single most important task you want to complete.",
            parse_mode="Markdown"
        )
        return WAITING_ONE_THING

    async def set_one_thing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the ONE thing response"""
        one_thing = update.message.text
        context.user_data["one_thing"] = one_thing

        keyboard = [
            [
                InlineKeyboardButton("🔥 High", callback_data="energy_high"),
                InlineKeyboardButton("😐 Medium", callback_data="energy_medium"),
                InlineKeyboardButton("😴 Low", callback_data="energy_low"),
            ]
        ]
        await update.message.reply_text(
            f"Got it: *{one_thing}*\n\nHow's your energy right now?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return WAITING_ENERGY_LEVEL

    async def handle_energy_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle energy level selection"""
        query = update.callback_query
        await query.answer()

        energy = query.data.replace("energy_", "")
        one_thing = context.user_data.get("one_thing", "")

        # Save to database
        await self.db.save_daily_intention(one_thing, energy)

        # Generate response based on energy
        if energy == "high":
            response = (
                f"🔥 *High energy!* Perfect.\n\n"
                f"Dive straight into: *{one_thing}*\n"
                f"Ride this motivation wave. Start a focus block with /focus"
            )
        elif energy == "medium":
            response = (
                f"👍 *Solid energy.* Good enough.\n\n"
                f"Your ONE thing: *{one_thing}*\n"
                f"Warm up with 10 min of easy tasks, then hit the main thing."
            )
        else:
            response = (
                f"😴 *Low energy.* That's real.\n\n"
                f"Your ONE thing: *{one_thing}*\n"
                f"Start with admin tasks or learning (10-15 min). "
                f"The energy often builds once you start moving."
            )

        await query.edit_message_text(response, parse_mode="Markdown")
        return ConversationHandler.END

    async def quick_checkin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send hourly check-in"""
        keyboard = [
            [
                InlineKeyboardButton("✅ On track", callback_data="checkin_on_track"),
                InlineKeyboardButton("😵 Distracted", callback_data="checkin_distracted"),
            ],
            [
                InlineKeyboardButton("🔄 Switched tasks", callback_data="checkin_switched"),
                InlineKeyboardButton("☕ Need break", callback_data="checkin_break"),
            ],
        ]

        today_intention = await self.db.get_today_intention()
        one_thing = today_intention.get("one_thing", "your main task") if today_intention else "your main task"

        status_text = ""
        if self.current_task:
            elapsed = (datetime.now(TZ) - self.task_start_time).total_seconds() / 60
            status_text = f"\n📍 Currently tracking: *{self.current_task}* ({int(elapsed)} min)"

        await update.message.reply_text(
            f"⏰ *Check-in time!*{status_text}\n\n"
            f"Reminder: ONE thing = *{one_thing}*\n\n"
            "How's it going?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    async def handle_checkin_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle check-in button response"""
        query = update.callback_query
        await query.answer()

        status = query.data.replace("checkin_", "")

        # Save to database
        await self.db.save_checkin(status, self.current_task)

        # Check for distraction pattern
        recent_checkins = await self.db.get_recent_checkins(hours=3)
        distracted_count = sum(1 for c in recent_checkins if c["status"] == "distracted")

        responses = {
            "on_track": "✅ Nice! Keep that momentum going.",
            "distracted": "😵 Noted. What pulled you away? Reply with a quick note if you want.",
            "switched": "🔄 Tasks shift. Make sure the switch was intentional, not avoidance.",
            "break": "☕ Breaks are fuel. Set a 10-min timer and actually rest.",
        }

        response = responses.get(status, "Got it!")

        # Add warning if distracted multiple times
        if distracted_count >= 2 and status == "distracted":
            today_intention = await self.db.get_today_intention()
            one_thing = today_intention.get("one_thing", "your main task") if today_intention else "your main task"
            response += (
                f"\n\n⚠️ *Hey, {distracted_count} distractions in 3 hours.*\n"
                f"Your ONE thing was: *{one_thing}*\n"
                "Do you need to adjust your environment?"
            )

        await query.edit_message_text(response, parse_mode="Markdown")

    async def start_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start tracking a task"""
        if self.current_task:
            await update.message.reply_text(
                f"⚠️ Already tracking: *{self.current_task}*\n"
                "Use /stop_task first or I'll auto-stop it.",
                parse_mode="Markdown"
            )

        await update.message.reply_text(
            "🎬 What task are you starting?"
        )
        return WAITING_TASK_NAME

    async def handle_task_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle task name input"""
        task_name = update.message.text
        context.user_data["pending_task"] = task_name

        # Get historical estimates for similar tasks
        similar_tasks = await self.db.get_similar_task_times(task_name)

        hint = ""
        if similar_tasks:
            avg = sum(t["actual_minutes"] for t in similar_tasks) / len(similar_tasks)
            hint = f"\n💡 Similar tasks took ~{int(avg)} min on average."

        await update.message.reply_text(
            f"Task: *{task_name}*{hint}\n\n"
            "How many minutes do you think this will take? (or 'skip')",
            parse_mode="Markdown"
        )
        return WAITING_ESTIMATE

    async def handle_estimate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle time estimate"""
        task_name = context.user_data.get("pending_task")

        estimate = None
        if update.message.text.lower() != "skip":
            try:
                estimate = int(update.message.text)
            except ValueError:
                await update.message.reply_text("Couldn't parse that. Starting without estimate.")

        # Stop previous task if any
        if self.current_task:
            await self._stop_current_task()

        # Start new task
        self.current_task = task_name
        self.task_start_time = datetime.now(TZ)

        # Save to database
        await self.db.start_time_entry(task_name, estimate)

        emoji = "⏱️" if estimate else "🎬"
        estimate_text = f" (estimated {estimate} min)" if estimate else ""

        await update.message.reply_text(
            f"{emoji} Started: *{task_name}*{estimate_text}\n\n"
            "Use /stop_task when done.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    async def stop_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop the current task"""
        if not self.current_task:
            await update.message.reply_text("No task currently being tracked.")
            return

        result = await self._stop_current_task()

        delta_text = ""
        if result.get("estimated"):
            diff = result["actual"] - result["estimated"]
            if diff > 0:
                delta_text = f"\n📊 Took {diff} min longer than estimated."
            elif diff < 0:
                delta_text = f"\n📊 Finished {-diff} min faster than estimated!"

        await update.message.reply_text(
            f"⏹️ Stopped: *{result['task']}*\n"
            f"Duration: {result['actual']} min{delta_text}",
            parse_mode="Markdown"
        )

    async def _stop_current_task(self):
        """Internal method to stop current task"""
        if not self.current_task:
            return None

        elapsed = (datetime.now(TZ) - self.task_start_time).total_seconds() / 60
        result = await self.db.stop_time_entry(self.current_task, int(elapsed))

        task = self.current_task
        self.current_task = None
        self.task_start_time = None

        return {"task": task, "actual": int(elapsed), "estimated": result.get("estimated")}

    async def start_focus_block(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start a focus block"""
        if self.focus_block_active:
            elapsed = (datetime.now(TZ) - self.focus_block_start).total_seconds() / 60
            await update.message.reply_text(
                f"🎯 Focus block already active on: *{self.focus_block_task}*\n"
                f"({int(elapsed)} min in)\n\n"
                "Use /end_focus to end it.",
                parse_mode="Markdown"
            )
            return ConversationHandler.END

        today_intention = await self.db.get_today_intention()
        suggestion = today_intention.get("one_thing", "") if today_intention else ""

        prompt = "🎯 *Focus Block*\n\nWhat will you focus on?"
        if suggestion:
            prompt += f"\n(Today's ONE thing: {suggestion})"

        await update.message.reply_text(prompt, parse_mode="Markdown")
        return WAITING_TASK_NAME

    async def handle_focus_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle focus block task input"""
        context.user_data["focus_task"] = update.message.text

        keyboard = [
            [
                InlineKeyboardButton("25 min", callback_data="focus_25"),
                InlineKeyboardButton("50 min", callback_data="focus_50"),
            ],
            [
                InlineKeyboardButton("90 min", callback_data="focus_90"),
                InlineKeyboardButton("2 hours", callback_data="focus_120"),
            ],
        ]

        await update.message.reply_text(
            "How long?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAITING_FOCUS_DURATION

    async def handle_focus_duration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle focus block duration selection"""
        query = update.callback_query
        await query.answer()

        duration = int(query.data.replace("focus_", ""))
        task = context.user_data.get("focus_task", "Deep work")

        self.focus_block_active = True
        self.focus_block_task = task
        self.focus_block_start = datetime.now(TZ)
        context.user_data["focus_duration"] = duration

        # Save to database
        await self.db.start_focus_block(task, duration)

        # Schedule end reminder
        context.job_queue.run_once(
            self.focus_block_end_reminder,
            duration * 60,
            chat_id=update.effective_chat.id,
            name=f"focus_end_{update.effective_chat.id}",
            data={"task": task, "duration": duration}
        )

        await query.edit_message_text(
            f"🎯 *Focus block started!*\n\n"
            f"Task: *{task}*\n"
            f"Duration: {duration} min\n\n"
            f"🔕 Go deep. I'll ping when time's up.\n"
            f"Use /end_focus if you finish early.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    async def focus_block_end_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send focus block end reminder"""
        job = context.job
        task = job.data["task"]
        duration = job.data["duration"]

        keyboard = [
            [
                InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="focus_rating_5"),
                InlineKeyboardButton("⭐⭐⭐⭐", callback_data="focus_rating_4"),
            ],
            [
                InlineKeyboardButton("⭐⭐⭐", callback_data="focus_rating_3"),
                InlineKeyboardButton("⭐⭐", callback_data="focus_rating_2"),
                InlineKeyboardButton("⭐", callback_data="focus_rating_1"),
            ],
        ]

        await context.bot.send_message(
            chat_id=job.chat_id,
            text=f"🎉 *Focus block complete!*\n\n"
                 f"Task: *{task}*\n"
                 f"Duration: {duration} min\n\n"
                 f"How did it go?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    async def handle_focus_rating(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle focus block rating"""
        query = update.callback_query
        await query.answer()

        rating = int(query.data.replace("focus_rating_", ""))

        actual = None
        if self.focus_block_start:
            actual = int((datetime.now(TZ) - self.focus_block_start).total_seconds() / 60)

        # Save to database
        await self.db.end_focus_block(self.focus_block_task, actual, rating)

        self.focus_block_active = False
        self.focus_block_task = None
        self.focus_block_start = None

        messages = {
            5: "🔥 Excellent! That's the deep work we're after.",
            4: "💪 Solid focus. Nice work.",
            3: "👍 Decent session. What could be better next time?",
            2: "😐 Struggled a bit? Note what pulled you away.",
            1: "😬 Rough one. Don't beat yourself up. Try a shorter block next time.",
        }

        await query.edit_message_text(
            messages.get(rating, "Session logged!"),
            parse_mode="Markdown"
        )

    async def end_focus_early(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """End focus block early"""
        if not self.focus_block_active:
            await update.message.reply_text("No focus block active.")
            return

        # Cancel scheduled reminder
        jobs = context.job_queue.get_jobs_by_name(f"focus_end_{update.effective_chat.id}")
        for job in jobs:
            job.schedule_removal()

        elapsed = int((datetime.now(TZ) - self.focus_block_start).total_seconds() / 60)

        keyboard = [
            [
                InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="focus_rating_5"),
                InlineKeyboardButton("⭐⭐⭐⭐", callback_data="focus_rating_4"),
            ],
            [
                InlineKeyboardButton("⭐⭐⭐", callback_data="focus_rating_3"),
                InlineKeyboardButton("⭐⭐", callback_data="focus_rating_2"),
                InlineKeyboardButton("⭐", callback_data="focus_rating_1"),
            ],
        ]

        await update.message.reply_text(
            f"⏹️ Focus block ended early.\n"
            f"Task: *{self.focus_block_task}*\n"
            f"Duration: {elapsed} min\n\n"
            f"How did it go?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current status"""
        parts = []

        # Today's ONE thing
        today = await self.db.get_today_intention()
        if today:
            status = "✅" if today.get("completed") else "⏳"
            parts.append(f"🎯 ONE thing: *{today['one_thing']}* {status}")

        # Current task
        if self.current_task:
            elapsed = (datetime.now(TZ) - self.task_start_time).total_seconds() / 60
            parts.append(f"⏱️ Current task: *{self.current_task}* ({int(elapsed)} min)")

        # Focus block
        if self.focus_block_active:
            elapsed = (datetime.now(TZ) - self.focus_block_start).total_seconds() / 60
            parts.append(f"🎯 Focus block: *{self.focus_block_task}* ({int(elapsed)} min)")

        # Today's check-ins
        checkins = await self.db.get_today_checkins()
        if checkins:
            on_track = sum(1 for c in checkins if c["status"] == "on_track")
            total = len(checkins)
            parts.append(f"📊 Check-ins: {on_track}/{total} on track")

        if not parts:
            parts.append("No active tracking. Use /morning to start your day!")

        # Year progress
        now = datetime.now(TZ)
        year_progress = (now.timetuple().tm_yday / 365) * 100
        parts.append(f"\n📅 2026 is {year_progress:.1f}% complete")

        await update.message.reply_text("\n".join(parts), parse_mode="Markdown")

    async def weekly_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show weekly time tracking stats"""
        stats = await self.db.get_weekly_stats()

        if not stats["entries"]:
            await update.message.reply_text(
                "No time entries this week yet.\n"
                "Start tracking with /start_task!"
            )
            return

        parts = [f"📊 *Weekly Stats* (Last 7 days)\n"]

        # Total time
        total = sum(e.get("actual_minutes", 0) for e in stats["entries"])
        parts.append(f"⏱️ Total tracked: {total} min ({total/60:.1f} hours)")

        # Estimation accuracy
        with_estimates = [e for e in stats["entries"] if e.get("estimated_minutes")]
        if with_estimates:
            diffs = [(e["actual_minutes"] - e["estimated_minutes"]) for e in with_estimates]
            avg_diff = sum(diffs) / len(diffs)
            if avg_diff > 0:
                parts.append(f"📊 Avg underestimate: {abs(avg_diff):.0f} min")
            else:
                parts.append(f"📊 Avg overestimate: {abs(avg_diff):.0f} min")

        # Focus blocks
        focus = stats.get("focus_blocks", [])
        if focus:
            total_focus = sum(f.get("actual_minutes", 0) for f in focus)
            avg_rating = sum(f.get("rating", 0) for f in focus if f.get("rating")) / len([f for f in focus if f.get("rating")]) if focus else 0
            parts.append(f"🎯 Focus blocks: {len(focus)} ({total_focus} min)")
            if avg_rating:
                parts.append(f"⭐ Avg focus rating: {avg_rating:.1f}/5")

        # Check-in summary
        checkins = stats.get("checkins", [])
        if checkins:
            on_track = sum(1 for c in checkins if c["status"] == "on_track")
            distracted = sum(1 for c in checkins if c["status"] == "distracted")
            parts.append(f"✅ On track: {on_track} | 😵 Distracted: {distracted}")

        await update.message.reply_text("\n".join(parts), parse_mode="Markdown")

    async def send_scheduled_checkin(self, context: ContextTypes.DEFAULT_TYPE):
        """Send scheduled hourly check-in"""
        chat_id = config.TELEGRAM_CHAT_ID

        # Don't send if in focus block
        if self.focus_block_active:
            return

        keyboard = [
            [
                InlineKeyboardButton("✅ On track", callback_data="checkin_on_track"),
                InlineKeyboardButton("😵 Distracted", callback_data="checkin_distracted"),
            ],
            [
                InlineKeyboardButton("🔄 Switched tasks", callback_data="checkin_switched"),
                InlineKeyboardButton("☕ Need break", callback_data="checkin_break"),
            ],
        ]

        today_intention = await self.db.get_today_intention()
        one_thing = today_intention.get("one_thing", "your main task") if today_intention else "your main task"

        status_text = ""
        if self.current_task:
            elapsed = (datetime.now(TZ) - self.task_start_time).total_seconds() / 60
            status_text = f"\n📍 Currently tracking: *{self.current_task}* ({int(elapsed)} min)"

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ *Hourly check-in*{status_text}\n\n"
                 f"ONE thing: *{one_thing}*\n\n"
                 "How's it going?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    async def send_morning_briefing_scheduled(self, context: ContextTypes.DEFAULT_TYPE):
        """Send scheduled morning briefing"""
        chat_id = config.TELEGRAM_CHAT_ID
        briefing = await generate_morning_briefing(self.db)

        await context.bot.send_message(
            chat_id=chat_id,
            text=briefing,
            parse_mode="Markdown"
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text="🎯 *What's your ONE thing today?*\n"
                 "Reply with your most important task.",
            parse_mode="Markdown"
        )


def main():
    """Start the bot"""
    if not config.TELEGRAM_BOT_TOKEN:
        print("Error: LIFE_BOT_TOKEN environment variable not set")
        print("Get a token from @BotFather on Telegram and set:")
        print("  export LIFE_BOT_TOKEN='your-token-here'")
        return

    # Create bot instance
    bot = LifeBot()

    # Create application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Morning briefing conversation
    morning_conv = ConversationHandler(
        entry_points=[CommandHandler("morning", bot.morning_briefing)],
        states={
            WAITING_ONE_THING: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.set_one_thing)],
            WAITING_ENERGY_LEVEL: [CallbackQueryHandler(bot.handle_energy_level, pattern="^energy_")],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    # Task tracking conversation
    task_conv = ConversationHandler(
        entry_points=[CommandHandler("start_task", bot.start_task)],
        states={
            WAITING_TASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_task_name)],
            WAITING_ESTIMATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_estimate)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    # Focus block conversation
    focus_conv = ConversationHandler(
        entry_points=[CommandHandler("focus", bot.start_focus_block)],
        states={
            WAITING_TASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_focus_task)],
            WAITING_FOCUS_DURATION: [CallbackQueryHandler(bot.handle_focus_duration, pattern="^focus_\\d+")],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("one", bot.morning_briefing))  # Alias for setting ONE thing
    application.add_handler(morning_conv)
    application.add_handler(task_conv)
    application.add_handler(focus_conv)
    application.add_handler(CommandHandler("stop_task", bot.stop_task))
    application.add_handler(CommandHandler("end_focus", bot.end_focus_early))
    application.add_handler(CommandHandler("checkin", bot.quick_checkin))
    application.add_handler(CommandHandler("status", bot.status))
    application.add_handler(CommandHandler("stats", bot.weekly_stats))

    # Callback handlers
    application.add_handler(CallbackQueryHandler(bot.handle_checkin_response, pattern="^checkin_"))
    application.add_handler(CallbackQueryHandler(bot.handle_focus_rating, pattern="^focus_rating_"))

    # Schedule jobs
    scheduler = AsyncIOScheduler(timezone=TZ)

    # Morning briefing at 9 AM
    scheduler.add_job(
        bot.send_morning_briefing_scheduled,
        CronTrigger(hour=config.MORNING_BRIEFING_HOUR, minute=0),
        args=[application],
        id="morning_briefing"
    )

    # Hourly check-ins (10 AM to 8 PM)
    for hour in range(10, 21):
        scheduler.add_job(
            bot.send_scheduled_checkin,
            CronTrigger(hour=hour, minute=0),
            args=[application],
            id=f"checkin_{hour}"
        )

    scheduler.start()

    # Start polling
    print("🤖 Life Management Bot starting...")
    print(f"   Timezone: {config.TIMEZONE}")
    print(f"   Morning briefing: {config.MORNING_BRIEFING_HOUR}:00")
    print(f"   Hourly check-ins: 10:00-20:00")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
