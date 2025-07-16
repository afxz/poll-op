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
        # Set context.args for canva_droplink_command
        context.args = [text]
        # Delete the original message
        try:
            await msg.delete()
        except Exception as e:
            logger.warning(f"Failed to delete original Canva link: {e}")
        # Temporarily set update.message to None so canva_droplink_command posts in the channel
        orig_msg = update.message
        try:
            update.message = None
            await canva_droplink_command(update, context)
        finally:
            update.message = orig_msg

# Export for bot.py registration
__all__ = ["canva_channel_auto_handler"]
