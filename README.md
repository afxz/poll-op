# LMS Telegram Bot

This project is a Python Telegram bot to automate a Last Man Standing (LMS) challenge group. Features:
- Sends daily polls (e.g., "How was your day? DD/MM/YYYY 🌌") with options like "Productive day, not relapsed ✅", etc.
- Sends daily and random motivational messages (using Gemini API).
- Only the admin (ID: 7068007001) can use commands or change settings. All other users are ignored.
- /stats command for admin only.
- /testpoll command for admin to test poll in DM before sending to group.
- All configuration is managed via a `.env` file.

## Setup
1. Copy `.env` and fill in your values:
   ```
   TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   GEMINI_API_KEY=AORO********
   GROUP_CHAT_ID=YOUR_GROUP_CHAT_ID
   ADMIN_ID=7068007001
   CHALLENGE_START_DATE=2025-07-01
   CHALLENGE_DAYS=150
   MOTIVATION_TIMES=08:00,20:00
   ```
2. Install dependencies:
   ```bash
   pip install python-telegram-bot requests python-dotenv
   ```
3. Run the bot:
   ```bash
   python bot.py
   ```

---

For more details, see the code and comments in `lms_bot.py`.
