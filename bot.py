import os
import logging
import requests
from datetime import datetime, timedelta, time
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, PollHandler, JobQueue, MessageHandler, filters
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or ''
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or ''
CHALLENGE_START_DATE = datetime.strptime(os.getenv('CHALLENGE_START_DATE', '2025-07-01'), '%Y-%m-%d')
CHALLENGE_DAYS = int(os.getenv('CHALLENGE_DAYS', 150))
POLL_OPTIONS = [
    "Productive day, not relapsed ✅",
    "Done meditation only ✅",
    "Done exercise only ✅",
    "Done both meditation and exercise ✅",
    "Unproductive day 👍",
    "Relapsed ❌"
]
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID') or ''
ADMIN_ID = int(os.getenv('ADMIN_ID', '7068007001'))
MOTIVATION_TIMES = [
    time(int(t.split(':')[0]), int(t.split(':')[1])) for t in os.getenv('MOTIVATION_TIMES', '08:00,20:00').split(',')
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Gemini API Integration ---
def get_motivation():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{
                "text": (
                    "Send a short, powerful, original motivational message for a Last Man Standing (LMS) nofap challenge group. "
                    "The message should be relevant to nofap, self-control, discipline, and perseverance. Avoid generic quotes. "
                    "Make it sound like a daily encouragement for people fighting urges and aiming for self-mastery."
                )
            }]
        }]
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "Stay strong! Every day you resist, you become the master of your mind."

# --- Admin Check Decorator ---
def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = None
        if update.effective_user:
            user_id = update.effective_user.id
        if user_id != ADMIN_ID:
            return  # Ignore non-admins
        return await func(update, context, *args, **kwargs)
    return wrapper

# --- Bot Handlers ---
@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Welcome to LMS 6.0! The challenge begins soon. Use /poll to send today's poll.")

async def send_daily_poll(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().date()
    day_num = (today - CHALLENGE_START_DATE.date()).days + 1
    if 1 <= day_num <= CHALLENGE_DAYS and GROUP_CHAT_ID:
        date_str = today.strftime('%d/%m/%Y')
        question = f"[ Poll : How was your day? {date_str} 🌌 ]"
        await context.bot.send_poll(
            chat_id=GROUP_CHAT_ID,
            question=question,
            options=POLL_OPTIONS,
            is_anonymous=False
        )

async def send_motivation(context: ContextTypes.DEFAULT_TYPE):
    msg = get_motivation()
    if GROUP_CHAT_ID:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)

@admin_only
async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_daily_poll(context)
    if update.message:
        await update.message.reply_text("Poll sent!")

@admin_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Stats feature coming soon! Only admin can see this.")

@admin_only
async def testpoll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send a test poll to the admin's DM
    today = datetime.now().date()
    date_str = today.strftime('%d/%m/%Y')
    question = f"[ Test Poll : How was your day? {date_str} 🌌 ]\n(Only visible to you)"
    await context.bot.send_poll(
        chat_id=ADMIN_ID,
        question=question,
        options=POLL_OPTIONS,
        is_anonymous=False
    )
    if update.message:
        await update.message.reply_text("Test poll sent to your DM! Check your saved messages.")

async def ignore_nonadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ignore all non-admin messages
    user_id = update.effective_user.id if update.effective_user else None
    if user_id != ADMIN_ID:
        return

# --- Scheduler Setup ---
def schedule_jobs(app):
    # Schedule daily poll at 7:00 AM IST (1:30 AM UTC)
    poll_time_utc = time(1, 30)
    app.job_queue.run_daily(send_daily_poll, poll_time_utc)
    # Schedule motivational messages
    for t in MOTIVATION_TIMES:
        # Convert IST to UTC
        utc_hour = (t.hour - 5) % 24
        utc_minute = (t.minute - 30) % 60
        app.job_queue.run_daily(send_motivation, time(utc_hour, utc_minute))

# --- Main ---
def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is not set in .env!")
        return
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("poll", poll_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("testpoll", testpoll_command))
    app.add_handler(MessageHandler(filters.ALL, ignore_nonadmin))
    schedule_jobs(app)
    logger.info("LMS Bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()
