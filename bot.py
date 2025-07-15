import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import TELEGRAM_TOKEN
from handlers.core import start, nav_callback
from handlers.poll import poll_command, emotion_poll_command, set_lms_poll_time, set_emotion_poll_time
from handlers.canva import canva_droplink_command
from handlers.motivation import testmotivation_command
from handlers.motivation import send_motivation
from handlers.stats import stats_command
from handlers.testpoll import testpoll_command
from jobs import schedule_jobs
from handlers.ignore import ignore_nonadmin

logging.basicConfig(level=logging.WARNING, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is not set in .env!")
        return
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.post_init = lambda app: schedule_jobs(app)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("poll", poll_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("testpoll", testpoll_command))
    app.add_handler(CommandHandler("testmotivation", testmotivation_command))
    app.add_handler(CommandHandler("emotionpoll", emotion_poll_command))
    app.add_handler(CommandHandler("setlmspolltime", set_lms_poll_time))
    app.add_handler(CommandHandler("setemotionpolltime", set_emotion_poll_time))
    app.add_handler(CommandHandler("canvadroplink", canva_droplink_command))
    app.add_handler(CallbackQueryHandler(nav_callback, pattern="^nav_"))
    app.add_handler(MessageHandler(filters.ALL, ignore_nonadmin))
    logger.warning("LMS Bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()
