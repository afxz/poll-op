from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS

async def ignore_nonadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else None
    if user_id not in ADMIN_IDS:
        pass  # Optionally log or ignore
