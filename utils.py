from config import ADMIN_ID
from telegram import Update
from telegram.ext import ContextTypes

def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id if update.effective_user else None
        if user_id != ADMIN_ID:
            return
        return await func(update, context, *args, **kwargs)
    return wrapper
