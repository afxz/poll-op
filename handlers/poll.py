import random
import re
import os
import logging
import pytz
from telegram import Update
from telegram.ext import ContextTypes
from config import POLL_OPTIONS, GROUP_CHAT_ID, CHALLENGE_START_DATE, CHALLENGE_DAYS, EMOTIONAL_STATE_OPTIONS
from utils import admin_only
from datetime import datetime

logger = logging.getLogger(__name__)
IST = pytz.timezone('Asia/Kolkata')

@admin_only
def shuffle_poll_options():
    opts = POLL_OPTIONS.copy()
    random.shuffle(opts)
    return opts


@admin_only
async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    date_str = today.strftime('%d/%m/%Y')
    question = f"🌌 LMS Daily Poll — How was your day?\nLMS Day {day_num if day_num > 0 else 0} ({date_str})"
    options = POLL_OPTIONS.copy()
    random.shuffle(options)
    if msg_obj:
        try:
            await msg_obj.reply_poll(
                question=question,
                options=options,
                is_anonymous=False,
                allows_multiple_answers=True
            )
        except Exception as e:
            await msg_obj.reply_text(f"Failed to send poll: {e}")

async def send_daily_poll(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    date_str = today.strftime('%d/%m/%Y')
    question = f"🌌 LMS Daily Poll — How was your day?\nLMS Day {day_num if day_num > 0 else 0} ({date_str})"
    options = POLL_OPTIONS.copy()
    random.shuffle(options)
    try:
        await context.bot.send_poll(
            chat_id=int(GROUP_CHAT_ID),
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=True
        )
    except Exception as e:
        logger.error(f"Failed to send daily poll: {e}")

@admin_only
async def emotion_poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    When /emotionpoll is sent in any chat (group or DM),
    - The bot sends the emotional state poll in the group and pins it.
    - Replies to the user with a confirmation (in DM or group).
    """
    from telegram.constants import ChatAction
    msg_obj = update.message
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    date_str = today.strftime('%d/%m/%Y')
    lms_stats = f"LMS Day {day_num} ({date_str})"
    question = (
        f"🧠 Emotional State Check — How are you feeling right now?\n{lms_stats}\nWin today. Repeat tomorrow."
    )
    options = EMOTIONAL_STATE_OPTIONS.copy()
    random.shuffle(options)
    try:
        # Send poll to group
        poll_msg = await context.bot.send_poll(
            chat_id=int(GROUP_CHAT_ID),
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        # Pin the poll in the group
        await context.bot.pin_chat_message(chat_id=int(GROUP_CHAT_ID), message_id=poll_msg.message_id, disable_notification=True)
        # Reply to the user (in DM or group)
        if msg_obj:
            await msg_obj.reply_text("✅ Emotional state poll sent and pinned in the group.")
    except Exception as e:
        if msg_obj:
            await msg_obj.reply_text(f"Failed to send emotional state poll: {e}")
        logger.error(f"Failed to send or pin emotional state poll: {e}")

async def send_emotion_poll(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    date_str = today.strftime('%d/%m/%Y')
    question = (
        f"🧠 Emotional State Check — How are you feeling right now?\n"
        f"LMS Day {day_num if day_num > 0 else 0} ({date_str})"
    )
    options = EMOTIONAL_STATE_OPTIONS.copy()
    random.shuffle(options)
    try:
        await context.bot.send_poll(
            chat_id=int(GROUP_CHAT_ID),
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )
    except Exception as e:
        logger.error(f"Failed to send emotional state poll: {e}")

@admin_only
async def set_lms_poll_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    if not msg_obj:
        return
    if not context.args or len(context.args) != 1:
        await msg_obj.reply_text("Usage: /setlmspolltime HH:MM (24h IST)")
        return
    new_time = context.args[0]
    if not re.match(r"^\d{2}:\d{2}$", new_time):
        await msg_obj.reply_text("Invalid time format. Use HH:MM (24h IST)")
        return
    os.environ['LMS_POLL_TIME'] = new_time
    await msg_obj.reply_text(f"LMS poll time updated to {new_time} IST. Please restart the bot to apply changes.")

@admin_only
async def set_emotion_poll_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    if not msg_obj:
        return
    if not context.args or len(context.args) != 1:
        await msg_obj.reply_text("Usage: /setemotionpolltime HH:MM (24h IST)")
        return
    new_time = context.args[0]
    if not re.match(r"^\d{2}:\d{2}$", new_time):
        await msg_obj.reply_text("Invalid time format. Use HH:MM (24h IST)")
        return
    os.environ['EMOTION_POLL_TIME'] = new_time
    await msg_obj.reply_text(f"Emotional state poll time updated to {new_time} IST. Please restart the bot to apply changes.")
