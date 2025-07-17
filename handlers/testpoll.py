from telegram import Update
from telegram.ext import ContextTypes
from utils import admin_only

@admin_only
async def testpoll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    from config import POLL_OPTIONS, GROUP_CHAT_ID, CHALLENGE_START_DATE
    import random
    from datetime import datetime
    import pytz
    IST = pytz.timezone('Asia/Kolkata')
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
        try:
            await context.bot.pin_chat_message(chat_id=int(GROUP_CHAT_ID), message_id=poll_msg.message_id, disable_notification=True)
        except Exception:
            pass
        # Encourage users to participate
        try:
            await context.bot.send_message(
                chat_id=int(GROUP_CHAT_ID),
                text="Let's see everyone's progress! Take a second to vote and stay accountable. 💪\nYour participation motivates others!",
                reply_to_message_id=poll_msg.message_id
            )
        except Exception:
            pass
        if msg_obj:
            await msg_obj.reply_text("✅ Test poll sent, pinned, and encouragement posted in the group.")
    except Exception as e:
        if msg_obj:
            await msg_obj.reply_text(f"Failed to send test poll: {e}")
