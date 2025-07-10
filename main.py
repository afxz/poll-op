import threading
import time
import os


def run_web():
    from web import HealthHandler
    from http.server import HTTPServer
    port = int(os.environ.get("PORT", 8080))
    print(f"[LMS] Web server starting on port {port}")
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


def run_bot():
    import os
    print("[LMS] ENVIRONMENT VARIABLES (except secrets):")
    for k, v in os.environ.items():
        if 'TOKEN' in k or 'KEY' in k:
            print(f"{k}=<hidden>")
        else:
            print(f"{k}={v}")
    try:
        from bot import main
        main()
    except Exception as e:
        import traceback
        print("[LMS] FATAL ERROR in bot startup:")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    t1 = threading.Thread(target=run_web, daemon=True)
    t1.start()
    # Give the web server a moment to start
    time.sleep(1)
    run_bot()
