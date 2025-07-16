# Voting callback handler for canva posts
from telegram import Update
from telegram.ext import ContextTypes

async def canva_vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.data:
        return
    data = query.data.split(":")
    if len(data) != 3:
        await query.answer("Invalid vote.", show_alert=True)
        return
    _, msg_id, vote_type = data
    user_id = query.from_user.id
    if not can_vote(msg_id):
        await query.answer("Voting closed for this post.", show_alert=True)
        return
    if user_has_voted(msg_id, user_id):
        await query.answer("You already voted!", show_alert=True)
        return
    if vote_type not in ("working", "notworking"):
        await query.answer("Invalid vote type.", show_alert=True)
        return
    add_vote(msg_id, user_id, vote_type)
    # Update the button markup
    try:
        await query.edit_message_reply_markup(reply_markup=build_vote_markup(msg_id))
    except Exception:
        pass
    if vote_type == "notworking":
        await query.answer(
            "Stay joined in this channel, we will post a new fresh link soon! Only try the latest post link.\n\nLinks stop working because all seats are probably filled already, so don't worry, we will post a new link soon.\n\nAdmin has been notified about this issue.\n\nHowever, if you want paid plans, message @aenzk right now.",
            show_alert=True
        )
    else:
        await query.answer("Vote recorded!", show_alert=False)

import requests
import os
import json
import random
import asyncio
import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters
from config import DROP_LINK_API_TOKEN, CANVA_CHANNEL_ID, CANVA_TUTORIAL_URL, CANVA_PROOF_URL, CANVA_PREVIEW_IMAGE
from utils import admin_only

# Exported symbols for import in bot.py
__all__ = [
    'canva_droplink_command',
    'droplink_command',
    'canva_link_auto_handler',
    'build_vote_markup',
    'schedule_fake_votes',
]

@admin_only
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
async def canva_link_auto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    if not msg_obj or not msg_obj.text:
        return
    text = msg_obj.text.strip()
    if text.startswith("https://www.canva.com/"):
        context.args = [text]
        await canva_droplink_command(update, context)
        return

def get_votes_storage():
    return os.path.join(os.path.dirname(__file__), '../canva_votes.json')

def load_votes():
    path = get_votes_storage()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_votes(data):
    path = get_votes_storage()
    try:
        with open(path, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass

def cleanup_old_votes():
    data = load_votes()
    now = datetime.datetime.utcnow().timestamp()
    changed = False
    for k in list(data.keys()):
        if now - data[k].get('timestamp', now) > 86400:
            del data[k]
            changed = True
    if changed:
        save_votes(data)

def get_vote_counts(msg_id):
    data = load_votes()
    v = data.get(str(msg_id), {})
    return v.get('working', 0), v.get('notworking', 0)

def user_has_voted(msg_id, user_id):
    data = load_votes()
    v = data.get(str(msg_id), {})
    return str(user_id) in v.get('voters', {})

def add_vote(msg_id, user_id, vote_type):
    data = load_votes()
    v = data.setdefault(str(msg_id), {'working': 0, 'notworking': 0, 'voters': {}, 'timestamp': datetime.datetime.utcnow().timestamp()})
    if str(user_id) in v['voters']:
        return False
    if vote_type == 'working':
        v['working'] += 1
    else:
        v['notworking'] += 1
    v['voters'][str(user_id)] = vote_type
    save_votes(data)
    return True

def set_fake_votes(msg_id, n):
    data = load_votes()
    v = data.setdefault(str(msg_id), {'working': 0, 'notworking': 0, 'voters': {}, 'timestamp': datetime.datetime.utcnow().timestamp()})
    v['working'] += n
    save_votes(data)

def can_vote(msg_id):
    data = load_votes()
    v = data.get(str(msg_id), {})
    now = datetime.datetime.utcnow().timestamp()
    return (now - v.get('timestamp', now)) < 86400

def build_vote_markup(msg_id):
    w, n = get_vote_counts(msg_id)
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"✅ Working ({w})", callback_data=f"canva_vote:{msg_id}:working"),
            InlineKeyboardButton(f"❌ Not working ({n})", callback_data=f"canva_vote:{msg_id}:notworking")
        ],
        [InlineKeyboardButton("⚠️ JOIN BACKUP ⚡️", url=CANVA_PROOF_URL)]
    ])

async def schedule_fake_votes(bot, chat_id, msg_id):
    await asyncio.sleep(random.randint(120, 300))
    n = random.randint(10, 20)
    set_fake_votes(msg_id, n)
    try:
        markup = build_vote_markup(msg_id)
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id, reply_markup=markup)
    except Exception:
        pass

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
    try:
        sent = await context.bot.send_photo(
            chat_id=channel_id,
            photo=CANVA_PREVIEW_IMAGE,
            caption=post_text,
            parse_mode="HTML",
            reply_markup=build_vote_markup('pending')  # temp, will update after send
        )
    except Exception as e:
        # Provide more helpful error messages for common Telegram errors
        error_text = str(e)
        if msg_obj:
            if "chat not found" in error_text.lower():
                help_msg = (
                    "Failed to post to channel: Chat not found.\n"
                    "- Make sure the bot is an admin in the channel.\n"
                    "- Double-check the CANVA_CHANNEL_ID in your .env (must be a numeric ID, not a URL).\n"
                    "- For private channels, the bot must be added as a member/admin.\n"
                    "- After changes, restart the bot."
                )
                await msg_obj.reply_text(help_msg)
            elif "not enough rights" in error_text.lower() or "have no rights" in error_text.lower():
                help_msg = (
                    "Failed to post to channel: Bot does not have permission.\n"
                    "- Make sure the bot is an admin in the channel with permission to post and send media."
                )
                await msg_obj.reply_text(help_msg)
            else:
                await msg_obj.reply_text(f"Failed to post to channel: {e}")
        return
    # Save initial vote data
    data = load_votes()
    data[str(sent.message_id)] = {'working': 0, 'notworking': 0, 'voters': {}, 'timestamp': datetime.datetime.utcnow().timestamp()}
    save_votes(data)
    # Update markup with real msg_id
    await context.bot.edit_message_reply_markup(chat_id=channel_id, message_id=sent.message_id, reply_markup=build_vote_markup(sent.message_id))
    # Schedule fake votes
    asyncio.create_task(schedule_fake_votes(context.bot, channel_id, sent.message_id))
    cleanup_old_votes()
    if msg_obj:
        await msg_obj.reply_text("Posted to channel successfully!")
    # (removed unreachable/undefined code)

## (Removed duplicate function definitions and unreachable code at the end of the file)