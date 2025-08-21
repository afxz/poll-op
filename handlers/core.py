import logging
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID, GROUP_CHAT_ID, CHALLENGE_START_DATE, CHALLENGE_DAYS, MOTIVATION_TIMES, POLL_OPTIONS, LMS_POLL_TIME
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
    from config import LMS_POLL_TIME
    return (
        "<b>👋 Welcome to LMS 6.0!</b>\n\n"
        "<b>Challenge Info:</b>\n"
        f"• <b>Start Date:</b> {CHALLENGE_START_DATE.date()}\n"
        f"• <b>End Date:</b> {challenge_end}\n"
        f"• <b>Day:</b> {day_num if day_num > 0 else 0} / {CHALLENGE_DAYS}\n"
        f"• <b>Days Left:</b> {days_left if days_left > 0 else 0}\n\n"
        f"<b>Auto Posting Times (IST):</b>\n• LMS Poll: {LMS_POLL_TIME}\n• Motivation: {motivation_times}\n\n"
        "<b>Elimination Events:</b>\n"
        "• <b>/sendeliminationpoll</b> — Start an elimination poll (non-voters will be removed after admin confirmation).\n"
        "• <b>/eliminationreport</b> — Get a report of who voted and who did not.\n"
        "• <b>/confirmelimination</b> — Confirm and remove non-voters.\n\n"
        "<b>Key Features & Navigation:</b>\n"
        "• <b>/polls</b> — LMS poll commands and info.\n"
        "• <b>/motivationnav</b> — Motivation info.\n"
        "• <b>/statsnav</b> — LMS stats and info.\n"
        "• <b>/togglecanvashortlink</b> — Toggle Canva shortlinking (admin only).\n"
        "<i>All commands are admin-only unless stated. Canva shortlinking toggle resets on restart.</i>"
    )

@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = get_start_message()
    msg_obj = update.message
    if msg_obj is not None:
        await msg_obj.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)


# --- NAVIGATION COMMANDS ---
@admin_only
async def polls_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import LMS_POLL_TIME
    msg = (
        "<b>📊 Polls</b>\n\n"
        "• <b>/poll</b> — Send a daily LMS poll to the group.\n"
        "• <b>/testpoll</b> — Test poll in the group (admin only).\n"
        "• <b>/setlmspolltime</b> — Set LMS poll time (admin only).\n\n"
        f"<b>Poll Time (IST):</b> {LMS_POLL_TIME}\n"
        "<b>Poll Options:</b>\n"
        + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(POLL_OPTIONS)]) +
        "\n\n<b>Other:</b>\n"
        "• <b>/droplink &lt;url&gt;</b> — Instantly shorten any link using Droplink and get the shortlink.\n"
        "• <b>/togglecanvashortlink</b> — Toggle Canva shortlinking (admin only).\n"
        "\n<b>How it works:</b>\n1. Use the command with a Canva invite link or any URL.\n2. The bot will shorten the link using Droplink if enabled. For Canva, it posts to the designated Canva channel with a tutorial and proof. For any other link, it replies with the shortlink.\n3. Use /togglecanvashortlink to enable or disable shortlinking for Canva links.\n\n<i>Only admins can use these commands. Toggle resets on restart.</i>"
    )
    msg_obj = update.message
    if msg_obj is not None:
        await msg_obj.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)



@admin_only
async def motivation_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    motivation_times = ', '.join([t.strftime('%H:%M') for t in MOTIVATION_TIMES])
    msg = (
        "<b>💡 Motivation</b>\n\n"
        "• <b>/testmotivation</b> — Send a test motivational message in the group.\n\n"
        f"<b>Motivation Times (IST):</b> {motivation_times}"
    )
    msg_obj = update.message
    if msg_obj is not None:
        await msg_obj.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

@admin_only
async def stats_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    days_left = CHALLENGE_DAYS - day_num + 1
    challenge_end = CHALLENGE_START_DATE.date() + timedelta(days=CHALLENGE_DAYS-1)
    msg = (
        f"<b>📈 LMS Stats</b>\n\n"
        f"<b>Start Date:</b> {CHALLENGE_START_DATE.date()}\n"
        f"<b>End Date:</b> {challenge_end}\n"
        f"<b>Day:</b> {day_num if day_num > 0 else 0} / {CHALLENGE_DAYS}\n"
        f"<b>Days Left:</b> {days_left if days_left > 0 else 0}\n"
        f"<b>Poll Time (IST):</b> {LMS_POLL_TIME}\n"
        f"<b>Group ID:</b> <code>{GROUP_CHAT_ID}</code>\n"
        f"<b>Admin ID:</b> <code>{ADMIN_ID}</code>\n"
        "<i>All times are in Indian Standard Time (IST).</i>"
    )
    msg_obj = update.message
    if msg_obj is not None:
        await msg_obj.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

def get_help_message():
    return (
        "<b>LMS Bot Help</b>\n\n"
        "• <b>/sendeliminationpoll</b> — Start an elimination poll (non-voters will be removed after admin confirmation).\n"
        "• <b>/eliminationreport</b> — Get a report of who voted and who did not.\n"
        "• <b>/confirmelimination</b> — Confirm and remove non-voters.\n"
        "• <b>/geteliminationvoters</b> — Export elimination voters JSON.\n"
        "• <b>/poll</b> — Send daily LMS poll.\n"
        "• <b>/testpoll</b> — Send test poll.\n"
        "• <b>/motivationnav</b> — Motivation info.\n"
        "• <b>/statsnav</b> — LMS stats and info.\n"
        "• <b>/togglecanvashortlink</b> — Toggle Canva shortlinking (admin only).\n"
        "<i>All commands are admin-only unless stated.</i>"
    )

