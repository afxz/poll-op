import requests
import logging
from config import GEMINI_API_KEY

def get_motivation():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{
                "text": (
                    "Send a short, powerful, original motivational message for a Last Man Standing (LMS) nofap challenge group. "
                    "The message should be relevant to nofap, self-control, discipline, and perseverance. Avoid generic quotes. "
                    "Make it sound like a daily encouragement for people fighting urges and aiming for self-mastery."
                )
            }]
        }]
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return "Stay strong! Every day you resist, you become the master of your mind."
