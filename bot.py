import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import TELEGRAM_TOKEN
from handlers.core import start
from handlers.poll import poll_command, emotion_poll_command, set_lms_poll_time, set_emotion_poll_time
from handlers.canva import canva_droplink_command, droplink_command
from handlers.motivation import testmotivation_command
from handlers.motivation import send_motivation
from handlers.stats import stats_command
from handlers.testpoll import testpoll_command
from jobs import schedule_jobs
from handlers.ignore import ignore_nonadmin

logging.basicConfig(level=logging.WARNING, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def main():
    # Start keepalive thread for Koyeb free plan
    try:
        from keepalive import start_keepalive
        start_keepalive()
    except Exception:
        pass
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
    app.add_handler(CommandHandler("droplink", droplink_command))
    # Voice-to-text admin-only handler
    from handlers.voice_transcribe import transcribe_voice
    app.add_handler(CommandHandler("transcribe", transcribe_voice))
    # Navigation commands
    from handlers.core import polls_nav, emotion_nav, motivation_nav, stats_nav, canva_nav
    app.add_handler(CommandHandler("polls", polls_nav))
    app.add_handler(CommandHandler("emotionnav", emotion_nav))
    app.add_handler(CommandHandler("motivationnav", motivation_nav))
    app.add_handler(CommandHandler("statsnav", stats_nav))
    app.add_handler(CommandHandler("canvanav", canva_nav))


    # Canva auto-link handler (must be before ignore_nonadmin)
    from handlers.canva import canva_link_auto_handler, canva_vote_callback
    from handlers.canva_channel_auto import canva_channel_auto_handler
    from config import CANVA_CHANNEL_ID
    # Handler for Canva links in the Canva channel (delete and repost)
    canva_channel_id_int = int(CANVA_CHANNEL_ID)
    app.add_handler(MessageHandler(
        filters.Chat(canva_channel_id_int) & filters.TEXT & filters.Regex(r"^https://www\.canva\.com/"),
        canva_channel_auto_handler
    ))
    # Handler for Canva links in other chats (old behavior)
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^https://www\.canva\.com/"), canva_link_auto_handler))

    # Voting callback handler for canva posts
    app.add_handler(CallbackQueryHandler(canva_vote_callback, pattern=r"^canva_vote:"))

    # MessageHandler must be last so it doesn't block other handlers
    app.add_handler(MessageHandler(filters.ALL, ignore_nonadmin))
    logger.warning("LMS Bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()
