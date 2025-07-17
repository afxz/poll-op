import os
import subprocess
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import admin_only

logger = logging.getLogger(__name__)

async def transcribe_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user_id = msg.from_user.id if msg and msg.from_user else None
    admin_id = int(os.getenv('ADMIN_ID', '7068007001'))
    if user_id != admin_id:
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
    file = await context.bot.get_file(file_id)
    ogg_path = f"voice_{file_id}.ogg"
    wav_path = f"voice_{file_id}.wav"
    try:
        await file.download_to_drive(ogg_path)
    except Exception as e:
        if msg:
            await msg.reply_text(f"Failed to download voice file: {e}")
        return
    # Check ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        await msg.reply_text("ffmpeg is not installed or not in PATH. Please install ffmpeg to use this feature.")
        os.remove(ogg_path)
        return
    # Convert ogg to wav
    try:
        subprocess.run(["ffmpeg", "-y", "-i", ogg_path, wav_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        await msg.reply_text(f"Failed to convert audio: {e}")
        os.remove(ogg_path)
        return
    # Transcribe with whisper-tiny
    try:
        # Requires: pip install openai-whisper
        import whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(wav_path)
        text_raw = result.get('text', '')
        if isinstance(text_raw, list):
            text = ' '.join(str(x) for x in text_raw).strip()
        else:
            text = str(text_raw).strip()
        if msg:
            if not text:
                await msg.reply_text("No speech detected or transcription failed.")
            else:
                await msg.reply_text(f"📝 Transcription:\n{text}")
    except Exception as e:
        if msg:
            await msg.reply_text(f"Transcription failed: {e}")
    finally:
        try:
            os.remove(ogg_path)
        except Exception:
            pass
        try:
            os.remove(wav_path)
        except Exception:
            pass

__all__ = ["transcribe_voice"]
