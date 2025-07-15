import requests
from telegram import Update
from telegram.ext import ContextTypes
from config import DROP_LINK_API_TOKEN, CANVA_CHANNEL_ID, CANVA_TUTORIAL_URL, CANVA_PROOF_URL, CANVA_PREVIEW_IMAGE
from utils import admin_only

@admin_only
async def canva_droplink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    if not context.args or len(context.args) < 1:
        if msg_obj:
            await msg_obj.reply_text("Usage: /canvadroplink <canva-invite-link> [custom-alias]")
        return
    long_url = context.args[0]
    alias = context.args[1] if len(context.args) > 1 else ""
    api_url = f"https://droplink.co/api?api={DROP_LINK_API_TOKEN}&url={long_url}"
    if alias:
        api_url += f"&alias={alias}"
    api_url += "&format=text"
    try:
        resp = requests.get(api_url, timeout=10)
        short_url = resp.text.strip()
        if not short_url or not short_url.startswith("http"):
            if msg_obj:
                await msg_obj.reply_text("Failed to shorten link. Droplink API error.")
            return
    except Exception as e:
        if msg_obj:
            await msg_obj.reply_text(f"Droplink API error: {e}")
        return
    post_text = (
        "NEW CANVA LINK ❤️✅\n"
        f"{short_url}\n{short_url}\n\n"
        f"📷 HOW TO JOIN TUTORIAL ({CANVA_TUTORIAL_URL}) 🧑‍💻\n\n"
        f"({CANVA_PROOF_URL})🖼 Proof: After joining, send a screenshot to @aenzBot.\n\n"
        f"⚠️ JOIN BACKUP ⚡️ ({CANVA_PROOF_URL})"
    )
    try:
        await context.bot.send_photo(
            chat_id=int(CANVA_CHANNEL_ID),
            photo=CANVA_PREVIEW_IMAGE,
            caption=post_text,
            parse_mode="HTML"
        )
        if msg_obj:
            await msg_obj.reply_text("Posted to channel successfully!")
    except Exception as e:
        if msg_obj:
            await msg_obj.reply_text(f"Failed to post to channel: {e}")