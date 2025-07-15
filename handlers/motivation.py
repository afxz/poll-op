import re
from telegram import Update
from telegram.ext import ContextTypes
from config import GROUP_CHAT_ID
from motivation_service import get_motivation
from utils import admin_only


@admin_only
async def testmotivation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    from motivation_service import get_motivation
    msg = get_motivation()
    import re
    msg = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', msg)
    msg = re.sub(r'\*(.*?)\*', r'<i>\1</i>', msg)
    msg = re.sub(r'`([^`]+)`', r'<code>\1</code>', msg)
    if msg_obj:
        await msg_obj.reply_text(msg, parse_mode="HTML")

async def send_motivation(context: ContextTypes.DEFAULT_TYPE):
    from motivation_service import get_motivation
    msg = get_motivation()
    import re
    msg = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', msg)
    msg = re.sub(r'\*(.*?)\*', r'<i>\1</i>', msg)
    msg = re.sub(r'`([^`]+)`', r'<code>\1</code>', msg)
    if GROUP_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=int(GROUP_CHAT_ID),
                text=msg,
                parse_mode="HTML"
            )
        except Exception as e:
            import logging
            logging.error(f"Failed to send motivation: {e}")
