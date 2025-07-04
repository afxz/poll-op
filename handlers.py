from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import POLL_OPTIONS, ADMIN_ID, GROUP_CHAT_ID, CHALLENGE_START_DATE, CHALLENGE_DAYS, MOTIVATION_TIMES
from motivation import get_motivation
from utils import admin_only
from datetime import datetime, timedelta, time as dtime
import logging
import pytz
import re
import asyncio
import random

logger = logging.getLogger(__name__)
IST = pytz.timezone('Asia/Kolkata')

def get_start_message():
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    days_left = CHALLENGE_DAYS - day_num + 1
    challenge_end = CHALLENGE_START_DATE.date() + timedelta(days=CHALLENGE_DAYS-1)
    motivation_times = ', '.join([t.strftime('%H:%M') for t in MOTIVATION_TIMES])
    return (
        "<b>👋 Welcome to LMS 6.0!</b>\n\n"
        "<b>Challenge Info:</b>\n"
        f"• <b>Start Date:</b> {CHALLENGE_START_DATE.date()}\n"
        f"• <b>End Date:</b> {challenge_end}\n"
        f"• <b>Day:</b> {day_num if day_num > 0 else 0} / {CHALLENGE_DAYS}\n"
        f"• <b>Days Left:</b> {days_left if days_left > 0 else 0}\n\n"
        f"<b>Auto Posting Times (IST):</b>\n• Poll: Random between 20:00-21:00\n• Motivation: {motivation_times}\n\n"
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
            InlineKeyboardButton("📈 Stats", callback_data="nav_stats"),
            InlineKeyboardButton("🚨 Relapse", callback_data="nav_relapse")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg_obj = update.message
    if msg_obj is not None:
        await msg_obj.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)

# Navigation callback handler
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
    if data == "nav_polls":
        msg = (
            "<b>📊 Polls</b>\n\n"
            "• <b>/poll</b> — Send a test poll to the group.\n"
            "• <b>/testpoll</b> — Test poll in your DM.\n\n"
            "<b>Poll Options:</b>\n"
            + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(POLL_OPTIONS)])
        )
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
    elif data == "nav_relapse":
        msg = (
            "<b>🚨 Relapse Command</b>\n\n"
            "• <b>/relapse</b> — Register a relapse (non-admins only).\n\n"
            "If you relapse, you will be <b>permanently banned</b> from the group. "
            "All ban and relapse-related messages are <b>auto-deleted</b> after 55–77 seconds for privacy and to reduce spam.\n\n"
            "<i>Use this feature responsibly. Only use /relapse if you have truly lost the challenge.</i>"
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
    else:
        # Go Back or unknown: show full start message with navigation buttons (concise, in sync)
        msg = get_start_message()
        keyboard = [
            [
                InlineKeyboardButton("📊 Polls", callback_data="nav_polls"),
                InlineKeyboardButton("💡 Motivation", callback_data="nav_motivation")
            ],
            [
                InlineKeyboardButton("📈 Stats", callback_data="nav_stats"),
                InlineKeyboardButton("🚨 Relapse", callback_data="nav_relapse")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        current_msg = getattr(query.message, 'text', None)
        current_markup = getattr(query.message, 'reply_markup', None)
        if current_msg != msg or current_markup != reply_markup:
            await query.edit_message_text(msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)
        await query.answer()
        return
    # Add Go Back button
    keyboard = [
        [InlineKeyboardButton("🔙 Go Back", callback_data="nav_home")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)
    await query.answer()

async def send_daily_poll(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    logger.info(f"Attempting to send poll: day_num={day_num}, group_id={GROUP_CHAT_ID}")
    if 1 <= day_num <= CHALLENGE_DAYS and GROUP_CHAT_ID:
        date_str = today.strftime('%d/%m/%Y')
        # Modern poll title with random emoji and day
        poll_emojis = ['🔥', '💪', '🌟', '🚀', '🦾', '🏆', '🛡️', '🧠', '🌞', '✨', '🦁', '🕊️', '🧘', '🎯', '🕹️']
        emoji = random.choice(poll_emojis)
        # Short, random nofap motivational quotes
        poll_quotes = [
            "Discipline is choosing between what you want now and what you want most.",
            "Every urge resisted is a victory.",
            "You are stronger than your urges.",
            "Progress, not perfection.",
            "Stay focused. Stay free.",
            "Your future self will thank you.",
            "One day at a time. You got this!",
            "Greatness is built on self-control.",
            "Keep your streak, keep your power.",
            "Real strength is in saying NO.",
            "The best project you’ll ever work on is you.",
            "Win today. Repeat tomorrow.",
            "You’re not alone. We rise together.",
            "Small wins, big results.",
            "Your mind is your greatest weapon."
        ]
        quote = random.choice(poll_quotes)
        question = (
            f"{emoji} LMS Day {day_num} — How was your day? ({date_str})\n"
            f"{quote}"
        )
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
            except Exception as e:
                logger.warning(f"Failed to pin poll: {e}")
            # Reply to the poll with a positive LMS message
            try:
                await context.bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text="Cast your vote! Every day counts. Stay strong, warriors!",
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
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    date_str = today.strftime('%d/%m/%Y')
    poll_emojis = ['🔥', '💪', '🌟', '🚀', '🦾', '🏆', '🛡️', '🧠', '🌞', '✨', '🦁', '🕊️', '🧘', '🎯', '🕹️']
    emoji = random.choice(poll_emojis)
    poll_quotes = [
        "Discipline is choosing between what you want now and what you want most.",
        "Every urge resisted is a victory.",
        "You are stronger than your urges.",
        "Progress, not perfection.",
        "Stay focused. Stay free.",
        "Your future self will thank you.",
        "One day at a time. You got this!",
        "Greatness is built on self-control.",
        "Keep your streak, keep your power.",
        "Real strength is in saying NO.",
        "The best project you’ll ever work on is you.",
        "Win today. Repeat tomorrow.",
        "You’re not alone. We rise together.",
        "Small wins, big results.",
        "Your mind is your greatest weapon."
    ]
    quote = random.choice(poll_quotes)
    question = (
        f"{emoji} LMS Day {day_num} — How was your day? ({date_str})\n"
        f"{quote}\n(This is a test poll for the group)"
    )
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
    msg_obj = update.message
    if msg_obj is not None:
        await msg_obj.reply_text("Test poll sent to the group!")

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
    msg_obj = update.message
    if msg_obj is not None:
        await msg_obj.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

@admin_only
async def testpoll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    date_str = today.strftime('%d/%m/%Y')
    poll_emojis = ['🔥', '💪', '🌟', '🚀', '🦾', '🏆', '🛡️', '🧠', '🌞', '✨', '🦁', '🕊️', '🧘', '🎯', '🕹️']
    emoji = random.choice(poll_emojis)
    poll_quotes = [
        "Discipline is choosing between what you want now and what you want most.",
        "Every urge resisted is a victory.",
        "You are stronger than your urges.",
        "Progress, not perfection.",
        "Stay focused. Stay free.",
        "Your future self will thank you.",
        "One day at a time. You got this!",
        "Greatness is built on self-control.",
        "Keep your streak, keep your power.",
        "Real strength is in saying NO.",
        "The best project you’ll ever work on is you.",
        "Win today. Repeat tomorrow.",
        "You’re not alone. We rise together.",
        "Small wins, big results.",
        "Your mind is your greatest weapon."
    ]
    quote = random.choice(poll_quotes)
    question = (
        f"{emoji} LMS Day {day_num} — How was your day? ({date_str})\n"
        f"{quote}\n(This is a test poll for the group)"
    )
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
    msg_obj = update.message
    if msg_obj is not None:
        await msg_obj.reply_text("Test poll sent to the group!")

@admin_only
async def testmotivation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = get_motivation()
    # Format: bold (**text**), italic (*text*), code (`text`)
    msg = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', msg)
    msg = re.sub(r'\*(.*?)\*', r'<i>\1</i>', msg)
    msg = re.sub(r'`([^`]+)`', r'<code>\1</code>', msg)
    if GROUP_CHAT_ID:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg, parse_mode="HTML")
    msg_obj = update.message
    if msg_obj is not None:
        await msg_obj.reply_text("Test motivational message sent to the group!", parse_mode="HTML")

async def ignore_nonadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else None
    if user_id != ADMIN_ID:
        return

async def send_motivation(context: ContextTypes.DEFAULT_TYPE):
    msg = get_motivation()
    # Format: bold (**text**), italic (*text*), code (`text`)
    msg = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', msg)
    msg = re.sub(r'\*(.*?)\*', r'<i>\1</i>', msg)
    msg = re.sub(r'`([^`]+)`', r'<code>\1</code>', msg)
    if GROUP_CHAT_ID:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg, parse_mode="HTML")

def is_challenge_started():
    today = datetime.now(IST).date()
    return today >= CHALLENGE_START_DATE.date()

async def relapse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or user.id == ADMIN_ID:
        return  # Ignore admin
    today = datetime.now(IST).date()
    challenge_started = is_challenge_started()
    challenge_end = CHALLENGE_START_DATE.date() + timedelta(days=CHALLENGE_DAYS-1)
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    import random
    delete_seconds = random.randint(55, 77)
    if not challenge_started:
        msg = (
            f"🚫 The LMS challenge hasn't started yet!\n\n"
            f"<b>Challenge Info:</b>\n"
            f"• <b>Start Date:</b> {CHALLENGE_START_DATE.date()}\n"
            f"• <b>End Date:</b> {challenge_end}\n"
            f"• <b>Day:</b> 0 / {CHALLENGE_DAYS}\n\n"
            "You can't use <code>/relapse</code> before the challenge begins.\n\n"
            f"<i>This message will be auto-deleted in {delete_seconds} seconds.</i>"
        )
        msg_obj = update.message
        if msg_obj is not None:
            sent_msg = await msg_obj.reply_text(msg, parse_mode="HTML")
            await asyncio.sleep(delete_seconds)
            try:
                await sent_msg.delete()
            except Exception:
                pass
        return
    # Show confirmation with inline buttons, mention user
    msg = (
        f"⚠️ <b>{user.mention_html()} — Are you sure you want to register a relapse?</b>\n\n"
        f"If you click <b>YES</b>, you are officially admitting that you have lost the challenge and will be <b>permanently banned</b> from the group.\n\n"
        f"<b>Challenge Info:</b>\n"
        f"• <b>Start Date:</b> {CHALLENGE_START_DATE.date()}\n"
        f"• <b>End Date:</b> {challenge_end}\n"
        f"• <b>Day:</b> {day_num if day_num > 0 else 0} / {CHALLENGE_DAYS}\n\n"
        f"You have lasted <b>{day_num if day_num > 0 else 0}</b> days in LMS.\n\n"
        f"Are you sure you want to proceed?\n\n"
        f"<b>You need to select quickly, this message will be auto-deleted in {delete_seconds} seconds!</b>"
    )
    keyboard = [
        [
            InlineKeyboardButton("✅ YES", callback_data=f"relapse_yes_{user.id}"),
            InlineKeyboardButton("❌ NO", callback_data=f"relapse_no_{user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg_obj = update.message
    sent_msg = None
    if msg_obj is not None:
        sent_msg = await msg_obj.reply_text(msg, parse_mode="HTML", reply_markup=reply_markup)
    # Schedule auto-delete for both the confirmation and the original /relapse command
    await asyncio.sleep(delete_seconds)
    if sent_msg is not None:
        try:
            await sent_msg.delete()
        except Exception:
            pass
    # Always try to delete the original /relapse command message
    if msg_obj is not None:
        try:
            await msg_obj.delete()
        except Exception:
            pass

async def relapse_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random
    query = update.callback_query
    if not query:
        return
    user = getattr(query, 'from_user', None)
    data = getattr(query, 'data', None)
    if not user or user.id == ADMIN_ID or not data:
        if query:
            await query.answer()
        return
    # Only allow the user who triggered the command to interact
    # The callback_data is relapse_yes_{user_id} or relapse_no_{user_id}
    try:
        action, _, target_id = data.partition('_')[2].partition('_')
        target_id = int(target_id)
    except Exception:
        await query.answer("Invalid action.", show_alert=True)
        return
    if user.id != target_id:
        await query.answer("This button is not for you.", show_alert=True)
        return
    delete_seconds = random.randint(55, 77)
    if data.startswith("relapse_yes_"):
        # Ban and kick user
        group_id = GROUP_CHAT_ID
        try:
            await context.bot.ban_chat_member(chat_id=group_id, user_id=user.id)
            # Delete the /relapse command message if possible
            try:
                msg_obj = getattr(query, 'message', None)
                if msg_obj is not None and hasattr(msg_obj, 'message_id'):
                    await context.bot.delete_message(chat_id=group_id, message_id=msg_obj.message_id)
            except Exception:
                pass
            ban_msg = await context.bot.send_message(
                chat_id=group_id,
                text=f"🚫 User <code>{user.id}</code> has been <b>banned</b> from the group for relapsing and losing the LMS challenge.\n\n<code>This message will be auto-deleted in {delete_seconds} seconds.</code>",
                parse_mode="HTML"
            )
            await query.edit_message_text(
                text=(
                    f"🚫 <b>Banned from LMS Group</b>\n\n"
                    f"User ID: <code>{user.id}</code> has been <b>permanently banned</b> from the group for relapsing and losing the LMS challenge.\n\n"
                    f"<b>User ID:</b> <code>{user.id}</code>\n"
                    f"<b>Reason:</b> Relapse registered during LMS challenge.\n\n"
                    f"<i>This message will be auto-deleted in {delete_seconds} seconds.</i>\n"
                    f"Stay strong and try again next time!"
                ),
                parse_mode="HTML"
            )
            # Schedule auto-delete for both messages
            await asyncio.sleep(delete_seconds)
            try:
                await context.bot.delete_message(chat_id=group_id, message_id=ban_msg.message_id)
            except Exception:
                pass
            try:
                await query.delete_message()
            except Exception:
                pass
        except Exception as e:
            await query.edit_message_text(
                text=f"❌ Failed to ban user: {e}"
            )
    elif data.startswith("relapse_no_"):
        warn_msg = (
            f"⚠️ <b>{user.mention_html()}</b>, please do not joke around with the /relapse command. Only use it if you have truly lost the challenge. Misuse may result in consequences.\n\n"
            f"<i>This message will be auto-deleted in {delete_seconds} seconds.</i>"
        )
        await query.edit_message_text(text=warn_msg, parse_mode="HTML")
        await asyncio.sleep(delete_seconds)
        try:
            await query.delete_message()
        except Exception:
            pass
    await query.answer()

# Register navigation callback handler at the end of the file
# (Make sure to add this handler in bot.py as well)
