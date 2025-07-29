import os
# Toggle for Canva shortlinking (default: True)
CANVA_SHORTLINK_ENABLED = os.getenv('CANVA_SHORTLINK_ENABLED', 'true').lower() == 'true'
from datetime import datetime, time
from dotenv import load_dotenv

load_dotenv()

DROP_LINK_API_TOKEN = os.getenv('DROP_LINK_API_TOKEN', '')
CANVA_CHANNEL_ID = os.getenv('CANVA_CHANNEL_ID', '-1002134567890')  # Set your channel ID here
CANVA_TUTORIAL_URL = os.getenv('CANVA_TUTORIAL_URL', 'https://t.me/CanvaProInviteLinks/881')
CANVA_PROOF_URL = os.getenv('CANVA_PROOF_URL', 'https://t.me/+ejp2_sjBtJczY2I9')
CANVA_PREVIEW_IMAGE = os.getenv('CANVA_PREVIEW_IMAGE', 'https://i.ibb.co/h1nbJXL1/photo-2025-07-15-21-38-07.jpg')
LMS_POLL_TIME = os.getenv('LMS_POLL_TIME', '20:00')  # Default 8:00 PM IST
# EMOTION_POLL_TIME and EMOTIONAL_STATE_OPTIONS are deprecated and not used.
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID', '')
ADMIN_ID = int(os.getenv('ADMIN_ID', '7068007001'))
CHALLENGE_START_DATE = datetime.strptime(os.getenv('CHALLENGE_START_DATE', '2025-07-01'), '%Y-%m-%d')
CHALLENGE_DAYS = int(os.getenv('CHALLENGE_DAYS', 150))
POLL_OPTIONS = [
    "✅ Strong & focused – No urges, full control, got things done 💪🧠",
    "📈 On the grind – Productive flow, learning, creating, or moving forward 🚀",
    "🏃‍♂️ Body in motion – Worked out, walked, or stayed physically active 🔋",
    "🧘 Centered & calm – Meditated, journaled, or stayed mindful 🌱",
    "🎧 Inspired – Had creative sparks or consumed meaningful content 🎨🎶",
    "😤 Urges hit hard – But I resisted and stayed clean 🛡️",
    "🌪️ Mentally chaotic – Overstimulated, anxious, or scattered but no relapse 😵‍💫",
    "😔 Down & drained – Low energy or mood, but I didn’t give in 🌧️",
    "☕ Neutral zone – Chill, not super productive, but stayed on track 📦",
    "❌ Relapsed – Slipped today, but I’m resetting and not giving up 🔄"
]

MOTIVATION_TIMES = [
    time(5, 0),
    time(12, 0),
    time(20, 0)
]
