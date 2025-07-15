import logging
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID, GROUP_CHAT_ID, CHALLENGE_START_DATE, CHALLENGE_DAYS, MOTIVATION_TIMES, POLL_OPTIONS, EMOTIONAL_STATE_OPTIONS
from motivation_service import get_motivation
from utils import admin_only
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)
IST = pytz.timezone('Asia/Kolkata')

def get_start_message():
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    days_left = CHALLENGE_DAYS - day_num + 1
    challenge_end = CHALLENGE_START_DATE.date() + timedelta(days=CHALLENGE_DAYS-1)
    motivation_times = ', '.join([t.strftime('%H:%M') for t in MOTIVATION_TIMES])
    from config import LMS_POLL_TIME, EMOTION_POLL_TIME
    return (
        "<b>👋 Welcome to LMS 6.0!</b>\n\n"
        "<b>Challenge Info:</b>\n"
        f"• <b>Start Date:</b> {CHALLENGE_START_DATE.date()}\n"
        f"• <b>End Date:</b> {challenge_end}\n"
        f"• <b>Day:</b> {day_num if day_num > 0 else 0} / {CHALLENGE_DAYS}\n"
        f"• <b>Days Left:</b> {days_left if days_left > 0 else 0}\n\n"
        f"<b>Auto Posting Times (IST):</b>\n• Poll: {LMS_POLL_TIME} (LMS)\n• Poll: {EMOTION_POLL_TIME} (Emotional State)\n• Motivation: {motivation_times}\n\n"
        "<b>Key Features:</b>\n"
        "• <b>/canvadroplink</b> — Shorten a Canva invite link and post to the Canva channel.\n"
        "<b>Use the navigation buttons below to explore all features and commands.</b>\n"
        "<i>All commands are admin-only.</i>"
    )

@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = get_start_message()
    keyboard = [
        [
            InlineKeyboardButton("📊 Polls", callback_data="nav_polls"),
            InlineKeyboardButton("💡 Motivation", callback_data="nav_motivation")
        ],
        [
            InlineKeyboardButton("🧠 Emotion", callback_data="nav_emotion"),
            InlineKeyboardButton("📈 Stats", callback_data="nav_stats")
        ],
        [
            InlineKeyboardButton("� Canva", callback_data="nav_canva")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg_obj = update.message
    if msg_obj is not None:
        await msg_obj.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)

async def nav_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    data = getattr(query, 'data', None)
    if not data:
        return
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    days_left = CHALLENGE_DAYS - day_num + 1
    challenge_end = CHALLENGE_START_DATE.date() + timedelta(days=CHALLENGE_DAYS-1)
    motivation_times = ', '.join([t.strftime('%H:%M') for t in MOTIVATION_TIMES])
    from config import LMS_POLL_TIME, EMOTION_POLL_TIME
    if data == "nav_polls":
        msg = (
            "<b>📊 Polls</b>\n\n"
            "• <b>/poll</b> — Send a test poll to the group.\n"
            "• <b>/testpoll</b> — Test poll in your DM.\n"
            "• <b>/emotionpoll</b> — Emotional state check poll.\n\n"
            f"<b>Poll Times (IST):</b> LMS: {LMS_POLL_TIME}, Emotional: {EMOTION_POLL_TIME}\n"
            "<b>Poll Options:</b>\n"
            + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(POLL_OPTIONS)]) +
            "\n\n<b>Other:</b>\n• <b>/canvadroplink</b> — Shorten a Canva invite link and post to the Canva channel."
        )
    elif data == "nav_emotion":
        msg = (
            "<b>🧠 Emotional State Check</b>\n\n"
            "• <b>/emotionpoll</b> — Post an emotional state check poll in the group.\n\n"
            f"<b>Poll Time (IST):</b> {EMOTION_POLL_TIME}\n"
            "<b>Emotional State Options:</b>\n"
            + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(EMOTIONAL_STATE_OPTIONS)])
        )
        keyboard = [
            [InlineKeyboardButton("🔙 Go Back", callback_data="nav_home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        current_msg = getattr(query.message, 'text', None)
        current_markup = getattr(query.message, 'reply_markup', None)
        if current_msg != msg or current_markup != reply_markup:
            await query.edit_message_text(msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)
        await query.answer()
        return
    elif data == "nav_motivation":
        msg = (
            "<b>💡 Motivation</b>\n\n"
            "• <b>/testmotivation</b> — Send a test motivational message in the group.\n\n"
            f"<b>Motivation Times (IST):</b> {motivation_times}"
        )
    elif data == "nav_stats":
        msg = (
            f"<b>📈 LMS Stats</b>\n\n"
            f"<b>Start Date:</b> {CHALLENGE_START_DATE.date()}\n"
            f"<b>End Date:</b> {challenge_end}\n"
            f"<b>Day:</b> {day_num if day_num > 0 else 0} / {CHALLENGE_DAYS}\n"
            f"<b>Days Left:</b> {days_left if days_left > 0 else 0}\n\n"
            f"<b>Group ID:</b> <code>{GROUP_CHAT_ID}</code>\n"
            f"<b>Admin ID:</b> <code>{ADMIN_ID}</code>\n"
            "<i>All times are in Indian Standard Time (IST).</i>"
        )
    elif data == "nav_canva":
        msg = (
            "<b>� Canva Feature</b>\n\n"
            "• <b>/canvadroplink &lt;canva-invite-link&gt; [custom-alias]</b> — Shorten a Canva invite link and post to the Canva channel.\n\n"
            "<b>How it works:</b>\n"
            "1. Use the command with a Canva invite link.\n"
            "2. The bot will shorten the link using Droplink and post it to the designated Canva channel with a tutorial and proof.\n\n"
            "<i>Only admins can use this command.</i>"
        )
        keyboard = [
            [InlineKeyboardButton("🔙 Go Back", callback_data="nav_home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        current_msg = getattr(query.message, 'text', None)
        current_markup = getattr(query.message, 'reply_markup', None)
        if current_msg != msg or current_markup != reply_markup:
            await query.edit_message_text(msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)
        await query.answer()
        return
    else:
        msg = get_start_message()
        keyboard = [
            [InlineKeyboardButton("📊 Polls", callback_data="nav_polls"),
             InlineKeyboardButton("💡 Motivation", callback_data="nav_motivation")],
            [InlineKeyboardButton("🧠 Emotion", callback_data="nav_emotion"),
             InlineKeyboardButton("📈 Stats", callback_data="nav_stats")],
            [InlineKeyboardButton("🌊 Canva", callback_data="nav_canva")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        current_msg = getattr(query.message, 'text', None)
        current_markup = getattr(query.message, 'reply_markup', None)
        if current_msg != msg or current_markup != reply_markup:
            await query.edit_message_text(msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)
        await query.answer()
