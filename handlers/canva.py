# Add missing imports for Telegram types
from telegram import Update
from telegram.ext import ContextTypes
from config import CANVA_SHORTLINK_ENABLED

# Toggle state (in-memory, will reset on restart)
canva_shortlink_enabled = CANVA_SHORTLINK_ENABLED

# Command to toggle Canva shortlinking
async def toggle_canva_shortlink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global canva_shortlink_enabled
    canva_shortlink_enabled = not canva_shortlink_enabled
    state = 'enabled' if canva_shortlink_enabled else 'disabled'
    msg_obj = update.message
    if msg_obj:
        await msg_obj.reply_text(f"Canva shortlinking is now <b>{state}</b>.", parse_mode="HTML")
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
    # --- FAKE VOTE RESTORE LOGIC (always runs, even for old posts) ---
    w, n = get_vote_counts(msg_id)
    # If the post has 0 or 1 working votes and no notworking votes, likely lost fake votes after restart
    if w <= 1 and n == 0:
        # Re-apply fake votes (same logic as schedule_fake_votes)
        fake_n = random.randint(10, 20)
        set_fake_votes(msg_id, fake_n)
        # Optionally update the markup immediately
        try:
            await query.edit_message_reply_markup(reply_markup=build_vote_markup(msg_id))
        except Exception:
            pass
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
        # This should not be triggered anymore, as the button is now a link, but keep for safety
        await query.answer("Please use the new link provided.", show_alert=True)
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
    'toggle_canva_shortlink_command',
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
    from config import CANVA_TUTORIAL_URL
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"✅ Working ({w})", callback_data=f"canva_vote:{msg_id}:working"),
            InlineKeyboardButton(f"💸 Paid Plans ({n})", url="https://t.me/CanvaProInviteLinks/583")
        ],
        [
            InlineKeyboardButton("📷 HOW TO JOIN TUTORIAL 🧑‍💻", url=CANVA_TUTORIAL_URL)
        ]
    ])

async def schedule_fake_votes(bot, chat_id, msg_id):
    await asyncio.sleep(random.randint(120, 300))
    n = random.randint(10, 20)
    set_fake_votes(msg_id, n)
    try:
        markup = build_vote_markup(msg_id)
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id, reply_markup=markup)
    except Exception as e:
        import logging
        logging.warning(f"[FakeVotes] Could not update message {msg_id} in chat {chat_id}: {e}")


# --- New Canva Post Format and Command ---
def build_canva_post_text(canva_url):
    # Format links bold and underline
    link_fmt = f"<b><u>{canva_url}</u></b>"
    return (
        "<b>FREE GIVEAWAY ✅😉 (ACTIVE)</b>\n"
        "<b>❤️ CANVA PRO ACTIVATED 💛</b>\n"
        "<b>👑 UPTO 30 Days 👑</b>\n\n"
        "<b>NEW CANVA LINK ❤️✅</b>\n"
        f"{link_fmt}\n{link_fmt}\n\n"
        "🖼 Proof: After joining, send a screenshot to @aenzBot\n\n"
        "<b>⚡️ Heads up</b>: Everyone who joins needs to complete the shortlink twice. After the second completion, you’ll be automatically added to the Pro plan — 100% guaranteed. 💚\n"
        "✅ Close pop up ads if appears."
    )

@admin_only
async def canva_droplink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    if not context.args or len(context.args) < 1:
        if msg_obj:
            await msg_obj.reply_text("Please provide a Canva invite link.")
        return
    original_canva_url = context.args[0] if context.args else ""
    alias = context.args[1] if len(context.args) > 1 else ""
    converted_url = original_canva_url
    global canva_shortlink_enabled
    if canva_shortlink_enabled:
        api_url = f"https://droplink.co/api?api={DROP_LINK_API_TOKEN}&url={original_canva_url}"
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
            converted_url = short_url
        except Exception as e:
            if msg_obj:
                await msg_obj.reply_text(f"Droplink API error: {e}")
            return
    canva_url = converted_url
    try:
        channel_id = int(CANVA_CHANNEL_ID)
    except Exception:
        if msg_obj:
            await msg_obj.reply_text("Invalid CANVA_CHANNEL_ID. Please check your .env and use the numeric channel ID (e.g., -1001234567890). Channel URLs are not supported.")
        return
    post_text = build_canva_post_text(canva_url)
    try:
        sent = await context.bot.send_photo(
            chat_id=channel_id,
            photo=CANVA_PREVIEW_IMAGE,
            caption=post_text,
            parse_mode="HTML",
            reply_markup=build_vote_markup('pending')
        )
    except Exception as e:
        error_text = str(e)
        if msg_obj:
            await msg_obj.reply_text(f"Failed to post to channel: {error_text}")
        return
    data = load_votes()
    data[str(sent.message_id)] = {'working': 0, 'notworking': 0, 'voters': {}, 'timestamp': datetime.datetime.utcnow().timestamp()}
    save_votes(data)
    await context.bot.edit_message_reply_markup(chat_id=channel_id, message_id=sent.message_id, reply_markup=build_vote_markup(sent.message_id))
    asyncio.create_task(schedule_fake_votes(context.bot, channel_id, sent.message_id))
    cleanup_old_votes()
    if msg_obj:
        try:
            await msg_obj.delete()
        except Exception:
            pass
    try:
        user_id = None
        if msg_obj and msg_obj.from_user:
            user_id = msg_obj.from_user.id
        elif update.effective_user:
            user_id = update.effective_user.id
        if user_id:
            summary = (
                "<b>Canva Link Posted</b>\n"
                f"<b>Original:</b> <code>{original_canva_url}</code>\n"
                f"<b>Converted:</b> <code>{converted_url}</code>\n"
                f"<b>Channel:</b> <code>{CANVA_CHANNEL_ID}</code>"
            )
            await context.bot.send_message(chat_id=user_id, text=summary, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        pass

# --- New /canva command for direct posting ---
@admin_only
async def canva_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message
    if not context.args or len(context.args) < 1:
        if msg_obj:
            await msg_obj.reply_text("Usage: /canva <canva-link>")
        return
    # Use the same logic as canva_droplink_command
    await canva_droplink_command(update, context)

## (Removed duplicate function definitions and unreachable code at the end of the file)