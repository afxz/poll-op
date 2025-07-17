
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
    # Start cache cleanup thread
    import shutil
    def cleanup_cache():
        while True:
            try:
                # Remove .ogg and .wav files in current directory
                for f in os.listdir('.'):
                    if f.endswith('.ogg') or f.endswith('.wav'):
                        try:
                            os.remove(f)
                        except Exception:
                            pass
                # Remove all files in __pycache__ directories
                for root, dirs, files in os.walk('.'):
                    for d in dirs:
                        if d == '__pycache__':
                            pycache_path = os.path.join(root, d)
                            try:
                                shutil.rmtree(pycache_path)
                            except Exception:
                                pass
            except Exception:
                pass
            time.sleep(600)  # Clean every 10 minutes
    cleanup_thread = threading.Thread(target=cleanup_cache, daemon=True)
    cleanup_thread.start()
