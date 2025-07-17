
# Telegram bot handler using python-telegram-bot v20+ that processes voice messages.
# Uses Hugging Face's hosted Whisper model for transcription instead of local Whisper install.
import os
import requests
from telegram import Update
from telegram.ext import ContextTypes
from utils import admin_only
from config import ADMIN_ID, HF_TOKEN

async def transcribe_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user_id = msg.from_user.id if msg and msg.from_user else None
    if user_id != ADMIN_ID:
        if msg:
            await msg.reply_text("Sorry, only the bot admin can use this feature.")
        return
    if not msg or not getattr(msg, 'reply_to_message', None) or not getattr(msg.reply_to_message, 'voice', None):
        if msg:
            await msg.reply_text("Reply to a voice message with /transcribe to use speech-to-text.")
        return
    # Clean up any leftover .ogg files
    for f in os.listdir('.'):
        if f.endswith('.ogg'):
            try:
                os.remove(f)
            except Exception:
                pass
    reply_msg = getattr(msg, 'reply_to_message', None)
    voice = getattr(reply_msg, 'voice', None)
    if not voice:
        if msg:
            await msg.reply_text("No voice message found to transcribe.")
        return
    file_id = getattr(voice, 'file_id', None)
    if not file_id:
        if msg:
            await msg.reply_text("Could not get file ID from voice message.")
        return
    ogg_path = "voice.ogg"
    try:
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(ogg_path)
    except Exception as e:
        if msg:
            await msg.reply_text(f"Failed to download voice file: {e}")
        return
    if not HF_TOKEN:
        await msg.reply_text("Hugging Face API token (HF_TOKEN) is not set in the environment.")
        try:
            os.remove(ogg_path)
        except Exception:
            pass
        return
    api_url = "https://api-inference.huggingface.co/models/openai/whisper-tiny"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        with open(ogg_path, "rb") as f:
            response = requests.post(api_url, headers=headers, data=f, timeout=60)
        if response.status_code == 503:
            await msg.reply_text("Model is loading on Hugging Face. Please try again in a few seconds.")
        elif response.status_code != 200:
            await msg.reply_text(f"Transcription failed: {response.status_code} {response.text}")
        else:
            result = response.json()
            text = result.get("text", "").strip()
            if not text:
                await msg.reply_text("No speech detected or transcription failed.")
            else:
                await msg.reply_text(f"📝 Transcription:\n{text}")
    except Exception as e:
        await msg.reply_text(f"Transcription failed: {e}")
    finally:
        try:
            os.remove(ogg_path)
        except Exception:
            pass

__all__ = ["transcribe_voice"]
