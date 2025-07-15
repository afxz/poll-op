from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

async def ignore_nonadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else None
    if user_id != ADMIN_ID:
        pass  # Optionally log or ignore
