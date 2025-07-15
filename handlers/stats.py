from telegram import Update
from telegram.ext import ContextTypes
from utils import admin_only

@admin_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    # Placeholder: In production, fetch real stats from DB or logs
    stats_text = "<b>LMS Group Stats</b>\n\n- Total Days: 150\n- Current Day: (auto-calc)\n- Polls sent: (auto-calc)\n- Motivations sent: (auto-calc)\n- More stats soon!"
    if msg_obj:
        await msg_obj.reply_text(stats_text, parse_mode="HTML")
