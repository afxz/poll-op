from datetime import time, datetime, timedelta
from config import MOTIVATION_TIMES
from handlers import send_daily_poll  # Only import send_daily_poll
import pytz
import random

IST = pytz.timezone('Asia/Kolkata')

def schedule_jobs(app):
    # Schedule daily poll at a random time between 7:00 PM and 8:00 PM IST
    now = datetime.now(IST)
    random_minute = random.randint(0, 59)
    poll_time_ist = time(19, random_minute)  # 19:00 to 19:59 IST
    # Convert IST to UTC
    poll_time_utc = (datetime.combine(now.date(), poll_time_ist) - timedelta(hours=5, minutes=30)).time()
    app.job_queue.run_daily(send_daily_poll, poll_time_utc)
    # Remove send_motivation scheduling if not defined
    # If you want to schedule motivation, ensure send_motivation exists in handlers.py and import it here
