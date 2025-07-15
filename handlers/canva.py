import requests
from telegram import Update
from telegram.ext import ContextTypes
from config import DROP_LINK_API_TOKEN, CANVA_CHANNEL_ID, CANVA_TUTORIAL_URL, CANVA_PROOF_URL, CANVA_PREVIEW_IMAGE
from utils import admin_only

async def droplink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    if not context.args or len(context.args) < 1:
        if msg_obj:
            await msg_obj.reply_text("Usage: /droplink <url> [custom-alias]")
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
        if msg_obj:
            await msg_obj.reply_text(f"Here is your Droplink shortlink:\n{short_url}")
    except Exception as e:
        if msg_obj:
            await msg_obj.reply_text(f"Droplink API error: {e}")
        return
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

    # Validate CANVA_CHANNEL_ID
    try:
        channel_id = int(CANVA_CHANNEL_ID)
    except Exception:
        if msg_obj:
            await msg_obj.reply_text("Invalid CANVA_CHANNEL_ID. Please check your .env and use the numeric channel ID (e.g., -1001234567890). Channel URLs are not supported.")
        return
    post_text = (
        "<b>NEW CANVA LINK ❤️✅</b>\n"
        f"<b><u>{short_url}</u></b>\n<b><u>{short_url}</u></b>\n\n"
        f"<b>📷 <a href=\"{CANVA_TUTORIAL_URL}\">HOW TO JOIN TUTORIAL</a> 🧑‍💻</b>\n\n"
        f"<b>🖼 Proof:</b> After joining, send a screenshot to <a href=\"https://t.me/aenzBot\">@aenzBot</a>.\n"
    )
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚠️ JOIN BACKUP ⚡️", url=CANVA_PROOF_URL)]
    ])
    try:
        await context.bot.send_photo(
            chat_id=channel_id,
            photo=CANVA_PREVIEW_IMAGE,
            caption=post_text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        if msg_obj:
            await msg_obj.reply_text("Posted to channel successfully!")
    except Exception as e:
        # Provide more helpful error messages for common Telegram errors
        error_text = str(e)
        if "chat not found" in error_text.lower():
            help_msg = (
                "Failed to post to channel: Chat not found.\n"
                "- Make sure the bot is an admin in the channel.\n"
                "- Double-check the CANVA_CHANNEL_ID in your .env (must be a numeric ID, not a URL).\n"
                "- For private channels, the bot must be added as a member/admin.\n"
                "- After changes, restart the bot."
            )
            if msg_obj:
                await msg_obj.reply_text(help_msg)
        elif "not enough rights" in error_text.lower() or "have no rights" in error_text.lower():
            help_msg = (
                "Failed to post to channel: Bot does not have permission.\n"
                "- Make sure the bot is an admin in the channel with permission to post and send media."
            )
            if msg_obj:
                await msg_obj.reply_text(help_msg)
        else:
            if msg_obj:
                await msg_obj.reply_text(f"Failed to post to channel: {e}")