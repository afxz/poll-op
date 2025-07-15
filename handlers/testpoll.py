from telegram import Update
from telegram.ext import ContextTypes
from utils import admin_only

@admin_only
async def testpoll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    from config import POLL_OPTIONS
    import random
    options = POLL_OPTIONS.copy()
    random.shuffle(options)
    question = "🌌 LMS Test Poll — How was your day? (Test only)"
    if msg_obj:
        try:
            await msg_obj.reply_poll(
                question=question,
                options=options,
                is_anonymous=False,
                allows_multiple_answers=True
            )
        except Exception as e:
            await msg_obj.reply_text(f"Failed to send test poll: {e}")
