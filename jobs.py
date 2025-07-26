from datetime import time, datetime, timedelta
from config import MOTIVATION_TIMES, LMS_POLL_TIME
from handlers import send_daily_poll, send_motivation
import pytz
import random

IST = pytz.timezone('Asia/Kolkata')

async def schedule_jobs(app):

    # Schedule daily poll at LMS_POLL_TIME (IST, format 'HH:MM')
    lms_hour, lms_minute = map(int, LMS_POLL_TIME.split(":"))
    poll_time_ist = time(lms_hour, lms_minute)
    poll_time_utc = (datetime.combine(datetime.now(IST).date(), poll_time_ist) - timedelta(hours=5, minutes=30)).time()
    app.job_queue.run_daily(send_daily_poll, poll_time_utc)


    # Schedule motivational messages at 5:00 AM, 12:00 PM, and 8:00 PM IST
    for t in MOTIVATION_TIMES:
        # Convert IST to UTC
        utc_hour = (t.hour - 5) % 24
        utc_minute = (t.minute - 30) % 60
        app.job_queue.run_daily(send_motivation, time(utc_hour, utc_minute))
