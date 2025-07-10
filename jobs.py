from datetime import time, datetime, timedelta
from config import MOTIVATION_TIMES
from handlers import send_daily_poll, send_motivation
import pytz
import random

IST = pytz.timezone('Asia/Kolkata')

async def schedule_jobs(app):
    # Schedule daily poll at a random time between 8:00 PM and 9:00 PM IST
    now = datetime.now(IST)
    random_minute = random.randint(0, 59)
    poll_time_ist = time(20, random_minute)  # 20:00 to 20:59 IST
    # Convert IST to UTC
    poll_time_utc = (datetime.combine(now.date(), poll_time_ist) - timedelta(hours=5, minutes=30)).time()
    app.job_queue.run_daily(send_daily_poll, poll_time_utc)

    # Schedule emotional state poll at 11:00 AM IST
    from handlers import emotion_poll_command
    emotion_time_ist = time(11, 0)
    emotion_time_utc = (datetime.combine(now.date(), emotion_time_ist) - timedelta(hours=5, minutes=30)).time()
    app.job_queue.run_daily(emotion_poll_command, emotion_time_utc)

    # Schedule motivational messages at 5:00 AM, 12:00 PM, and 8:00 PM IST
    for t in MOTIVATION_TIMES:
        # Convert IST to UTC
        utc_hour = (t.hour - 5) % 24
        utc_minute = (t.minute - 30) % 60
        app.job_queue.run_daily(send_motivation, time(utc_hour, utc_minute))
