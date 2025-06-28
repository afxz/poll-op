from telegram import Update
from telegram.ext import ContextTypes
from config import POLL_OPTIONS, ADMIN_ID, GROUP_CHAT_ID, CHALLENGE_START_DATE, CHALLENGE_DAYS, MOTIVATION_TIMES
from motivation import get_motivation
from utils import admin_only
from datetime import datetime, timedelta, time as dtime
import logging
import pytz
import re

logger = logging.getLogger(__name__)
IST = pytz.timezone('Asia/Kolkata')

@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    days_left = CHALLENGE_DAYS - day_num + 1
    challenge_end = CHALLENGE_START_DATE.date() + timedelta(days=CHALLENGE_DAYS-1)
    motivation_times = ', '.join([t.strftime('%H:%M') for t in MOTIVATION_TIMES])
    msg = (
        "<b>👋 Welcome to LMS 6.0!</b>\n\n"
        "<b>Navigation & Commands:</b>\n"
        "• <b>/poll</b> — Send a test poll to the group.\n"
        "• <b>/testpoll</b> — Test poll in your DM.\n"
        "• <b>/testmotivation</b> — Send a test motivational message in the group.\n"
        "• <b>/stats</b> — View LMS stats.\n"
        "• <b>/start</b> — Show this menu.\n\n"
        f"<b>Challenge Info:</b>\n"
        f"• <b>Start Date:</b> {CHALLENGE_START_DATE.date()}\n"
        f"• <b>End Date:</b> {challenge_end}\n"
        f"• <b>Day:</b> {day_num if day_num > 0 else 0} / {CHALLENGE_DAYS}\n"
        f"• <b>Days Left:</b> {days_left if days_left > 0 else 0}\n\n"
        f"<b>Auto Posting Times (IST):</b>\n• Poll: Random between 20:00-21:00\n• Motivation: {motivation_times}\n\n"
        "<b>Poll Options:</b>\n"
        + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(POLL_OPTIONS)]) +
        "\n\n<b>Tip:</b> Use /poll or /testmotivation any time to test in the group!\n"
        "<i>All commands are admin-only.</i>"
    )
    if update.message:
        await update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

async def send_daily_poll(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    logger.info(f"Attempting to send poll: day_num={day_num}, group_id={GROUP_CHAT_ID}")
    if 1 <= day_num <= CHALLENGE_DAYS and GROUP_CHAT_ID:
        date_str = today.strftime('%d/%m/%Y')
        question = f"[ Poll : How was your day? {date_str} 🌌 ]\nKeep pushing forward, every day is a win!"
        try:
            poll_msg = await context.bot.send_poll(
                chat_id=GROUP_CHAT_ID,
                question=question,
                options=POLL_OPTIONS,
                is_anonymous=False
            )
            logger.info(f"Poll sent successfully: message_id={poll_msg.message_id}")
            # Pin the poll
            try:
                await context.bot.pin_chat_message(chat_id=GROUP_CHAT_ID, message_id=poll_msg.message_id, disable_notification=True)
                # Service message deletion is not possible via Telegram Bot API as of 2025.
                # This is a Telegram limitation and cannot be worked around.
            except Exception as e:
                logger.warning(f"Failed to pin poll: {e}")
            # Reply to the poll with a positive LMS message
            try:
                await context.bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text="Cast your vote! Every day counts in LMS. Let's keep each other accountable!",
                    reply_to_message_id=poll_msg.message_id
                )
            except Exception as e:
                logger.warning(f"Failed to reply to poll: {e}")
        except Exception as e:
            logger.error(f"Failed to send poll: {e}")
    else:
        logger.warning(f"Poll not sent: day_num={day_num}, group_id={GROUP_CHAT_ID}")

@admin_only
async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    date_str = today.strftime('%d/%m/%Y')
    question = f"[ Test Poll : How was your day? {date_str} 🌌 ]\nKeep pushing forward, every day is a win!\n(This is a test poll for the group)"
    try:
        poll_msg = await context.bot.send_poll(
            chat_id=GROUP_CHAT_ID,
            question=question,
            options=POLL_OPTIONS,
            is_anonymous=False
        )
        # Pin the poll
        try:
            await context.bot.pin_chat_message(chat_id=GROUP_CHAT_ID, message_id=poll_msg.message_id, disable_notification=True)
            # Service message deletion is not possible via Telegram Bot API as of 2025.
            # This is a Telegram limitation and cannot be worked around.
        except Exception as e:
            logger.warning(f"Failed to pin poll: {e}")
        # Reply to the poll with a positive LMS message
        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text="Test poll sent! Cast your vote and check poll visibility.",
                reply_to_message_id=poll_msg.message_id
            )
        except Exception as e:
            logger.warning(f"Failed to reply to poll: {e}")
    except Exception as e:
        logger.error(f"Failed to send test poll: {e}")
    if update.message:
        await update.message.reply_text("Test poll sent to the group!")

@admin_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    days_left = CHALLENGE_DAYS - day_num + 1
    challenge_end = CHALLENGE_START_DATE.date() + timedelta(days=CHALLENGE_DAYS-1)
    motivation_times = ', '.join([t.strftime('%H:%M') for t in MOTIVATION_TIMES])
    msg = (
        f"<b>LMS 6.0 Stats</b>\n\n"
        f"<b>Start Date:</b> {CHALLENGE_START_DATE.date()}\n"
        f"<b>End Date:</b> {challenge_end}\n"
        f"<b>Day:</b> {day_num if day_num > 0 else 0} / {CHALLENGE_DAYS}\n"
        f"<b>Days Left:</b> {days_left if days_left > 0 else 0}\n\n"
        f"<b>Auto Posting Times (IST):</b>\n• Poll: Random between 20:00-21:00\n• Motivation: {motivation_times}\n\n"
        f"<b>Group ID:</b> <code>{GROUP_CHAT_ID}</code>\n"
        f"<b>Admin ID:</b> <code>{ADMIN_ID}</code>\n"
        "<i>All times are in Indian Standard Time (IST).</i>"
    )
    if update.message:
        await update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

@admin_only
async def testpoll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    date_str = today.strftime('%d/%m/%Y')
    question = f"[ Test Poll : How was your day? {date_str} 🌌 ]\nKeep pushing forward, every day is a win!\n(This is a test poll for the group)"
    try:
        poll_msg = await context.bot.send_poll(
            chat_id=GROUP_CHAT_ID,
            question=question,
            options=POLL_OPTIONS,
            is_anonymous=False
        )
        # Pin the poll
        try:
            await context.bot.pin_chat_message(chat_id=GROUP_CHAT_ID, message_id=poll_msg.message_id, disable_notification=True)
            # Service message deletion is not possible via Telegram Bot API as of 2025.
            # This is a Telegram limitation and cannot be worked around.
        except Exception as e:
            logger.warning(f"Failed to pin poll: {e}")
        # Reply to the poll with a positive LMS message
        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text="Test poll sent! Cast your vote and check poll visibility.",
                reply_to_message_id=poll_msg.message_id
            )
        except Exception as e:
            logger.warning(f"Failed to reply to poll: {e}")
    except Exception as e:
        logger.error(f"Failed to send test poll: {e}")
    if update.message:
        await update.message.reply_text("Test poll sent to the group!")

@admin_only
async def testmotivation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = get_motivation()
    # Replace markdown bold **text** with Telegram HTML <b>text</b>
    msg = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', msg)
    if GROUP_CHAT_ID:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg, parse_mode="HTML")
    if update.message:
        await update.message.reply_text("Test motivational message sent to the group!", parse_mode="HTML")

async def ignore_nonadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else None
    if user_id != ADMIN_ID:
        return

async def send_motivation(context: ContextTypes.DEFAULT_TYPE):
    msg = get_motivation()
    # Replace markdown bold **text** with Telegram HTML <b>text</b>
    msg = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', msg)
    if GROUP_CHAT_ID:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg, parse_mode="HTML")
