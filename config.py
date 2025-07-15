import os
from datetime import datetime, time
from dotenv import load_dotenv

load_dotenv()

DROP_LINK_API_TOKEN = os.getenv('DROP_LINK_API_TOKEN', '467b2c6bb71304bd3b84ac818703b578ec6439fe')
CANVA_CHANNEL_ID = os.getenv('CANVA_CHANNEL_ID', '-1002134567890')  # Set your channel ID here
CANVA_TUTORIAL_URL = os.getenv('CANVA_TUTORIAL_URL', 'https://t.me/CanvaProInviteLinks/881')
CANVA_PROOF_URL = os.getenv('CANVA_PROOF_URL', 'https://t.me/+ejp2_sjBtJczY2I9')
CANVA_PREVIEW_IMAGE = os.getenv('CANVA_PREVIEW_IMAGE', 'https://i.ibb.co/h1nbJXL1/photo-2025-07-15-21-38-07.jpg')
LMS_POLL_TIME = os.getenv('LMS_POLL_TIME', '20:00')  # Default 8:00 PM IST
EMOTION_POLL_TIME = os.getenv('EMOTION_POLL_TIME', '14:00')  # Default 2:00 PM IST
EMOTIONAL_STATE_OPTIONS = [
    "😊 Happy and positive",
    "😐 Neutral/okay",
    "😔 Sad or down",
    "😠 Angry or frustrated",
    "😰 Anxious or stressed",
    "😤 Motivated and determined",
    "😴 Tired or exhausted",
    "🤗 Grateful or content",
    "😕 Confused or lost",
    "🙁 Lonely or isolated"
]
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID', '')
ADMIN_ID = int(os.getenv('ADMIN_ID', '7068007001'))
CHALLENGE_START_DATE = datetime.strptime(os.getenv('CHALLENGE_START_DATE', '2025-07-01'), '%Y-%m-%d')
CHALLENGE_DAYS = int(os.getenv('CHALLENGE_DAYS', 150))
POLL_OPTIONS = [
    "✅ Stayed strong, no urges!",
    "💪 Fought urges, didn't relapse!",
    "🧘 Did meditation today",
    "🏃‍♂️ Did exercise today",
    "📚 Productive day overall",
    "😐 Struggled, but didn't relapse",
    "😓 Unproductive day, but didn't relapse",
    "❌ Relapsed today"
]
MOTIVATION_TIMES = [
    time(5, 0),
    time(12, 0),
    time(20, 0)
]
