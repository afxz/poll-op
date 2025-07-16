
import threading
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Koyeb will keep the app alive if it receives regular HTTP requests
# Set this to your deployed Koyeb app's public URL
KEEPALIVE_URL = os.getenv("KEEPALIVE_URL")

# Ping every 4 minutes (Koyeb free plan sleeps after 5 min idle)
PING_INTERVAL = 240

def keepalive_loop():
    if not KEEPALIVE_URL:
        return
    while True:
        try:
            requests.get(KEEPALIVE_URL, timeout=10)
        except Exception:
            pass
        time.sleep(PING_INTERVAL)

def start_keepalive():
    t = threading.Thread(target=keepalive_loop, daemon=True)
    t.start()
