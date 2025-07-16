from telegram import Update
from telegram.ext import ContextTypes
from utils import admin_only

@admin_only
async def testpoll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    from config import POLL_OPTIONS, GROUP_CHAT_ID, CHALLENGE_START_DATE
    import random
    from motivation_service import get_motivation
    from datetime import datetime
    import pytz
    IST = pytz.timezone('Asia/Kolkata')
    today = datetime.now(IST).date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    date_str = today.strftime('%d/%m/%Y')
    options = POLL_OPTIONS.copy()
    random.shuffle(options)
    motivation = get_motivation()
    question = f"🔥 LMS Day {day_num} — How was your day? ({date_str})\nWin today. Repeat tomorrow.\n\n💡 Motivation: {motivation}"
    try:
        await context.bot.send_poll(
            chat_id=int(GROUP_CHAT_ID),
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        if msg_obj:
            await msg_obj.reply_text("✅ Test poll sent in the group.")
    except Exception as e:
        if msg_obj:
            await msg_obj.reply_text(f"Failed to send test poll: {e}")
