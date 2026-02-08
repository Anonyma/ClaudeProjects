#!/usr/bin/env python3
"""
End-of-Day Reflection Bot

A Telegram bot that:
1. Sends evening prompt at 21:00 (configurable)
2. Collects responses via conversation
3. Stores everything in Supabase

Run: python eod_reflection_bot.py
Manual trigger: python eod_reflection_bot.py --send-now
"""
import asyncio
import os
import sys
import json
import logging
from datetime import datetime, date, time as dt_time, timedelta
from zoneinfo import ZoneInfo
from typing import Optional

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

import config
from supabase_client import SupabaseClient
from llm_client import get_llm_client

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TZ = ZoneInfo(config.TIMEZONE)

# Schedule config
REFLECTION_HOUR = 21  # 9 PM
REFLECTION_MINUTE = 0

# Conversation states
(
    WAITING_ACCOMPLISHMENTS,
    WAITING_MOOD,
    WAITING_ENERGY,
    WAITING_FOCUS,
    WAITING_STRUGGLES,
    WAITING_WINS,
    WAITING_TOMORROW,
    WAITING_FREEFORM,
) = range(8)


class ReflectionBot:
    def __init__(self):
        self.db = SupabaseClient()
        self.active_reflections = {}

    def _get_reflection(self, chat_id: int) -> dict:
        if chat_id not in self.active_reflections:
            self.active_reflections[chat_id] = {
                "date": date.today().isoformat(),
                "reflection_type": "end_of_day",
                "started_at": datetime.now(TZ).isoformat(),
                "accomplishments": [],
                "worked_on": [],
                "struggled_with": [],
                "overall_mood": None,
                "energy_pattern": None,
                "focus_quality": None,
                "wins": None,
                "one_thing_tomorrow": None,
                "raw_journal": None,
            }
        return self.active_reflections[chat_id]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        llm = get_llm_client()
        ai_status = "🧠 AI enabled" if llm.enabled else "📝 Basic mode"

        await update.message.reply_text(
            f"Hey! I'm your reflection bot. ({ai_status})\n\n"
            "/reflect - Start end-of-day reflection\n"
            "/quick - Quick 2-question check-in\n"
            "/chat <msg> - Chat with AI coach\n"
            "/status - Check bot status\n\n"
            f"I'll also ping you at {REFLECTION_HOUR}:00 daily."
        )

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        llm = get_llm_client()
        ai_status = "✅ Connected" if llm.enabled else "❌ No API key"

        await update.message.reply_text(
            f"*Bot Status*\n\n"
            f"🤖 Bot: Running\n"
            f"🧠 AI: {ai_status}\n"
            f"⏰ Daily prompt: {REFLECTION_HOUR}:00 {config.TIMEZONE}\n"
            f"💾 Supabase: {'Connected' if self.db else 'Not configured'}",
            parse_mode="Markdown"
        )

    async def chat_with_ai(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /chat <your message>")
            return

        message = " ".join(context.args)
        llm = get_llm_client()

        if not llm.enabled:
            await update.message.reply_text(
                "AI not configured. Set ANTHROPIC_API_KEY to enable."
            )
            return

        await update.message.reply_text("🤔...")

        response = await llm.chat(message)
        if response:
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Couldn't get a response. Try again?")

    async def start_reflection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self._get_reflection(chat_id)

        await update.message.reply_text(
            "🌙 *End of Day Reflection*\n\n"
            "Let's review your day. Takes 3-5 min.\n"
            "Say 'skip' to skip any question.\n\n"
            "*What did you actually get done today?*\n"
            "(List things you completed, big or small)",
            parse_mode="Markdown"
        )
        return WAITING_ACCOMPLISHMENTS

    async def handle_accomplishments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        text = update.message.text

        if text.lower() != "skip":
            items = [line.strip().strip("-•").strip() for line in text.split("\n") if line.strip()]
            self._get_reflection(chat_id)["accomplishments"] = items

        keyboard = [
            [
                InlineKeyboardButton("1 rough", callback_data="mood_1"),
                InlineKeyboardButton("2 meh", callback_data="mood_2"),
                InlineKeyboardButton("3 okay", callback_data="mood_3"),
            ],
            [
                InlineKeyboardButton("4 good", callback_data="mood_4"),
                InlineKeyboardButton("5 great", callback_data="mood_5"),
            ],
        ]
        await update.message.reply_text(
            "*How would you rate your overall day?*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return WAITING_MOOD

    async def handle_mood(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        chat_id = update.effective_chat.id
        mood_map = {"mood_1": "rough", "mood_2": "meh", "mood_3": "okay", "mood_4": "good", "mood_5": "great"}
        self._get_reflection(chat_id)["overall_mood"] = mood_map.get(query.data, "okay")

        keyboard = [
            [InlineKeyboardButton("steady", callback_data="energy_steady")],
            [InlineKeyboardButton("morning peak → faded", callback_data="energy_morning_peak")],
            [InlineKeyboardButton("afternoon slump", callback_data="energy_afternoon_slump")],
            [InlineKeyboardButton("late surge", callback_data="energy_late_surge")],
            [InlineKeyboardButton("erratic", callback_data="energy_erratic")],
        ]
        await query.edit_message_text(
            "*How was your energy pattern?*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return WAITING_ENERGY

    async def handle_energy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        chat_id = update.effective_chat.id
        energy = query.data.replace("energy_", "")
        self._get_reflection(chat_id)["energy_pattern"] = energy

        keyboard = [[
            InlineKeyboardButton("1", callback_data="focus_1"),
            InlineKeyboardButton("2", callback_data="focus_2"),
            InlineKeyboardButton("3", callback_data="focus_3"),
            InlineKeyboardButton("4", callback_data="focus_4"),
            InlineKeyboardButton("5", callback_data="focus_5"),
        ]]
        await query.edit_message_text(
            "*How was your focus today?* (1-5)\n1 = scattered, 5 = laser focused",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return WAITING_FOCUS

    async def handle_focus(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        chat_id = update.effective_chat.id
        focus = int(query.data.replace("focus_", ""))
        self._get_reflection(chat_id)["focus_quality"] = focus

        await query.edit_message_text(
            "*What was hard today? What got in the way?*\n(Or say 'skip')",
            parse_mode="Markdown"
        )
        return WAITING_STRUGGLES

    async def handle_struggles(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        text = update.message.text

        if text.lower() != "skip":
            items = [line.strip().strip("-•").strip() for line in text.split("\n") if line.strip()]
            self._get_reflection(chat_id)["struggled_with"] = items

        await update.message.reply_text(
            "*What's one thing that went well today?*",
            parse_mode="Markdown"
        )
        return WAITING_WINS

    async def handle_wins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        text = update.message.text

        if text.lower() != "skip":
            self._get_reflection(chat_id)["wins"] = text.strip()

        await update.message.reply_text(
            "*What's your ONE thing for tomorrow?*",
            parse_mode="Markdown"
        )
        return WAITING_TOMORROW

    async def handle_tomorrow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        text = update.message.text

        if text.lower() != "skip":
            self._get_reflection(chat_id)["one_thing_tomorrow"] = text.strip()

        await update.message.reply_text(
            "*Anything else on your mind?*\n(Or say 'done')",
            parse_mode="Markdown"
        )
        return WAITING_FREEFORM

    async def handle_freeform(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        text = update.message.text

        reflection = self._get_reflection(chat_id)
        if text.lower() not in ["done", "skip", "none"]:
            reflection["raw_journal"] = text.strip()

        reflection["completed_at"] = datetime.now(TZ).isoformat()
        success = await self.db.save_reflection(reflection)

        # Summary
        parts = []
        if reflection.get("accomplishments"):
            parts.append(f"✅ {len(reflection['accomplishments'])} done")
        if reflection.get("overall_mood"):
            parts.append(f"Mood: {reflection['overall_mood']}")
        if reflection.get("focus_quality"):
            parts.append(f"Focus: {reflection['focus_quality']}/5")
        if reflection.get("one_thing_tomorrow"):
            parts.append(f"Tomorrow: {reflection['one_thing_tomorrow'][:30]}...")

        summary = " | ".join(parts) if parts else "Logged."
        del self.active_reflections[chat_id]

        status = "✅ Saved" if success else "⚠️ Local only"

        # Try to get AI feedback
        llm = get_llm_client()
        ai_feedback = await llm.generate_reflection_feedback(reflection)

        response = f"🌙 *Reflection Complete*\n\n{summary}\n\n{status}"
        if ai_feedback:
            response += f"\n\n💭 {ai_feedback}"
        response += "\n\nRest well. 🌅"

        await update.message.reply_text(response, parse_mode="Markdown")
        return ConversationHandler.END

    async def quick_checkin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data="quick_1"),
                InlineKeyboardButton("2", callback_data="quick_2"),
                InlineKeyboardButton("3", callback_data="quick_3"),
                InlineKeyboardButton("4", callback_data="quick_4"),
                InlineKeyboardButton("5", callback_data="quick_5"),
            ],
        ]
        await update.message.reply_text(
            "⚡ *Quick check-in*\n\nHow's your day? (1-5)",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    async def handle_quick_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        mood = query.data.replace("quick_", "")
        context.user_data["quick_mood"] = mood

        await query.edit_message_text(
            "*What are you doing rn?* (1-3 words)",
            parse_mode="Markdown"
        )

    async def handle_quick_activity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        activity = update.message.text.strip()
        mood = context.user_data.get("quick_mood", "3")

        await self.db.save_checkin(status=f"mood_{mood}", current_task=activity)
        await update.message.reply_text(f"✅ Logged: {activity} (mood {mood}/5)")

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if chat_id in self.active_reflections:
            del self.active_reflections[chat_id]
        await update.message.reply_text("Cancelled.")
        return ConversationHandler.END


async def scheduled_reflection_prompt(context: ContextTypes.DEFAULT_TYPE):
    """Send the daily reflection prompt"""
    logger.info("Sending scheduled reflection prompt")
    await context.bot.send_message(
        chat_id=config.TELEGRAM_CHAT_ID,
        text="🌙 *End of Day Reflection*\n\n"
             "Time to review your day.\n\n"
             "/reflect - Full reflection (3-5 min)\n"
             "/quick - Quick check-in (30 sec)",
        parse_mode="Markdown"
    )


async def send_reflection_prompt():
    """Manual trigger for reflection prompt"""
    from telegram import Bot

    if not config.TELEGRAM_BOT_TOKEN:
        print("No bot token")
        return

    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    await bot.send_message(
        chat_id=config.TELEGRAM_CHAT_ID,
        text="🌙 *End of Day Reflection*\n\n"
             "/reflect - Full reflection (3-5 min)\n"
             "/quick - Quick check-in (30 sec)",
        parse_mode="Markdown"
    )
    print(f"Sent to {config.TELEGRAM_CHAT_ID}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--send-now":
        asyncio.run(send_reflection_prompt())
        return

    if not config.TELEGRAM_BOT_TOKEN:
        print("Error: Set TELEGRAM_BOT_TOKEN or LIFE_BOT_TOKEN")
        return

    bot = ReflectionBot()
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Reflection conversation
    reflection_conv = ConversationHandler(
        entry_points=[CommandHandler("reflect", bot.start_reflection)],
        states={
            WAITING_ACCOMPLISHMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_accomplishments)],
            WAITING_MOOD: [CallbackQueryHandler(bot.handle_mood, pattern="^mood_")],
            WAITING_ENERGY: [CallbackQueryHandler(bot.handle_energy, pattern="^energy_")],
            WAITING_FOCUS: [CallbackQueryHandler(bot.handle_focus, pattern="^focus_")],
            WAITING_STRUGGLES: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_struggles)],
            WAITING_WINS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_wins)],
            WAITING_TOMORROW: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_tomorrow)],
            WAITING_FREEFORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_freeform)],
        },
        fallbacks=[CommandHandler("cancel", bot.cancel)],
    )

    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("status", bot.status))
    application.add_handler(CommandHandler("chat", bot.chat_with_ai))
    application.add_handler(reflection_conv)
    application.add_handler(CommandHandler("quick", bot.quick_checkin))
    application.add_handler(CallbackQueryHandler(bot.handle_quick_response, pattern="^quick_"))

    # Schedule daily reflection prompt at 21:00
    job_queue = application.job_queue
    reflection_time = dt_time(hour=REFLECTION_HOUR, minute=REFLECTION_MINUTE, tzinfo=TZ)
    job_queue.run_daily(
        scheduled_reflection_prompt,
        time=reflection_time,
        name="daily_reflection"
    )

    logger.info(f"🌙 Reflection Bot starting...")
    logger.info(f"   Daily prompt at {REFLECTION_HOUR}:{REFLECTION_MINUTE:02d} {config.TIMEZONE}")
    logger.info(f"   Commands: /reflect, /quick")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
