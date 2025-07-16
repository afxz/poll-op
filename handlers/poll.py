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
    quotes = [
        "Every day you win, you get stronger. Stay in the fight!",
        "Discipline is choosing between what you want now and what you want most.",
        "The journey is tough, but so are you. Keep going!",
        "You are the master of your fate. Prove it today!",
        "Small wins each day lead to big victories.",
        "Your future self will thank you for not giving up.",
        "Win today. Repeat tomorrow.",
        "Progress, not perfection. Show up for yourself!"
    ]
    motivation = random.choice(quotes)
    question = f"🔥 LMS Day {day_num} — How was your day? ({date_str})\nWin today. Repeat tomorrow.\n\n💡 Motivation: {motivation}"
    options = POLL_OPTIONS.copy()
    random.shuffle(options)
    if msg_obj:
        try:
            poll_msg = await msg_obj.reply_poll(
                question=question,
                options=options,
                is_anonymous=False,
                allows_multiple_answers=False
            )
            # Pin the poll
            await msg_obj.chat.pin_message(poll_msg.message_id, disable_notification=True)
            # Encourage users to participate
            await poll_msg.reply_text(
                "Let's see everyone's progress! Take a second to vote and stay accountable. 💪\nYour participation motivates others!"
            )
        except Exception as e:
            await msg_obj.reply_text(f"Failed to send poll: {e}")

async def send_daily_poll(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    date_str = today.strftime('%d/%m/%Y')
    quotes = [
        "Every day you win, you get stronger. Stay in the fight!",
        "Discipline is choosing between what you want now and what you want most.",
        "The journey is tough, but so are you. Keep going!",
        "You are the master of your fate. Prove it today!",
        "Small wins each day lead to big victories.",
        "Your future self will thank you for not giving up.",
        "Win today. Repeat tomorrow.",
        "Progress, not perfection. Show up for yourself!"
    ]
    motivation = random.choice(quotes)
    question = f"🔥 LMS Day {day_num} — How was your day? ({date_str})\nWin today. Repeat tomorrow.\n\n💡 Motivation: {motivation}"
    options = POLL_OPTIONS.copy()
    random.shuffle(options)
    try:
        poll_msg = await context.bot.send_poll(
            chat_id=int(GROUP_CHAT_ID),
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        # Pin the poll
        await context.bot.pin_chat_message(chat_id=int(GROUP_CHAT_ID), message_id=poll_msg.message_id, disable_notification=True)
        # Encourage users to participate
        await context.bot.send_message(
            chat_id=int(GROUP_CHAT_ID),
            text="Let's see everyone's progress! Take a second to vote and stay accountable. 💪\nYour participation motivates others!",
            reply_to_message_id=poll_msg.message_id
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
    quotes = [
        "Your feelings matter. Share honestly and support each other!",
        "Checking in is a sign of strength, not weakness.",
        "Every emotion is valid. Let's grow together!",
        "Community is power. You're not alone!",
        "Express, don't suppress. We're here for you!",
        "Participation helps everyone feel seen and heard.",
        "Win today. Repeat tomorrow.",
        "Your check-in motivates others to open up!"
    ]
    motivation = random.choice(quotes)
    question = (
        f"🧠 Emotional State Check — How are you feeling right now?\n{lms_stats}\nWin today. Repeat tomorrow.\n\n💡 Motivation: {motivation}"
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
        # Encourage users to participate
        await context.bot.send_message(
            chat_id=int(GROUP_CHAT_ID),
            text="Take a moment to check in! Your honest vote helps the whole group grow. 🧠\nLet's support each other!",
            reply_to_message_id=poll_msg.message_id
        )
        # Reply to the user (in DM or group)
        if msg_obj:
            await msg_obj.reply_text("✅ Emotional state poll sent, pinned, and encouragement posted in the group.")
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
