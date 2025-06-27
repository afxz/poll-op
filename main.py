import threading
import time
import os

def run_web():
    from web import HealthHandler
    from http.server import HTTPServer
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Web server running on port {port}")
    server.serve_forever()

def run_bot():
    from bot import main
    main()

if __name__ == "__main__":
    t1 = threading.Thread(target=run_web, daemon=True)
    t1.start()
    # Give the web server a moment to start
    time.sleep(1)
    run_bot()
