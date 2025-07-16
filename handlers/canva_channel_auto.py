import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import CANVA_CHANNEL_ID
from handlers.canva import canva_droplink_command

logger = logging.getLogger(__name__)

async def canva_channel_auto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    # Only act in the Canva channel
    if str(msg.chat.id) != str(CANVA_CHANNEL_ID):
        return
    text = msg.text.strip()
    if text.startswith("https://www.canva.com/"):
        # Forwarded messages: treat as text
        context.args = [text]
        # Delete the original message
        try:
            await msg.delete()
        except Exception as e:
            logger.warning(f"Failed to delete original Canva link: {e}")
        # Post using the canva_droplink_command
        await canva_droplink_command(update, context)

# Export for bot.py registration
__all__ = ["canva_channel_auto_handler"]
