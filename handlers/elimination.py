from utils import admin_only
# Admin command to export group_members.json
@admin_only
async def export_members_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(GROUP_MEMBERS_FILE):
        await update.message.reply_text("No group members file found. Import one first.")
        return
    await update.message.reply_document(document=open(GROUP_MEMBERS_FILE, 'rb'), filename='group_members.json', caption="Current group members.")
GROUP_MEMBERS_FILE = os.path.join(os.path.dirname(__file__), '../group_members.json')

# Admin command to import group_members.json
from telegram import Document
@admin_only
async def import_members_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("Please send a JSON file (exported group members).")
        return
    file = await update.message.document.get_file()
    await file.download_to_drive(GROUP_MEMBERS_FILE)
    await update.message.reply_text("Group members file imported successfully.")

# Helper to load imported group members
def load_group_members():
    if os.path.exists(GROUP_MEMBERS_FILE):
        with open(GROUP_MEMBERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []
import os
import json
from telegram import Update, Document
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from utils import admin_only

ELIMINATION_VOTERS_FILE = os.path.join(os.path.dirname(__file__), '../elimination_voters.json')
ELIMINATION_POLL_ID_FILE = os.path.join(os.path.dirname(__file__), '../elimination_poll_id.txt')
def save_elimination_poll_id(poll_id):
    with open(ELIMINATION_POLL_ID_FILE, 'w') as f:
        f.write(str(poll_id))

def load_elimination_poll_id():
    if os.path.exists(ELIMINATION_POLL_ID_FILE):
        with open(ELIMINATION_POLL_ID_FILE, 'r') as f:
            return f.read().strip()
    return None
# --- Poll Answer Handler ---
from telegram.ext import PollAnswerHandler

# Call this when you create the elimination poll (store poll_id)
@admin_only
async def set_elimination_poll_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /seteliminationpoll <poll_id>
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /seteliminationpoll <poll_id>")
        return
    poll_id = context.args[0]
    save_elimination_poll_id(poll_id)
    await update.message.reply_text(f"Elimination poll ID set to: {poll_id}")

async def elimination_poll_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_id = load_elimination_poll_id()
    if not poll_id:
        return
    answer = update.poll_answer
    if not answer or answer.poll_id != poll_id:
        return
    user_id = answer.user.id
    voters = load_elimination_voters()
    voters[str(user_id)] = True
    save_elimination_voters(voters)

# --- Report and Confirmation ---
@admin_only
async def elimination_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import GROUP_CHAT_ID
    poll_id = load_elimination_poll_id()
    if not poll_id:
        await update.message.reply_text("No elimination poll ID set.")
        return
    voters = load_elimination_voters()
    admin_ids = set(member.user.id for member in await context.bot.get_chat_administrators(GROUP_CHAT_ID))
    # Use imported group members if available
    group_members = load_group_members()
    if group_members:
        all_member_ids = set(m['id'] for m in group_members)
    else:
        # fallback: only known voters + admins
        all_member_ids = set(int(uid) for uid in voters.keys()) | admin_ids
    # Remove admins from elimination
    non_admins = all_member_ids - admin_ids
    voted = set(int(uid) for uid in voters.keys())
    not_voted = non_admins - voted
    report = f"<b>Elimination Poll Report</b>\nKnown non-admin members: {len(non_admins)}\nVoted: {len(voted)}\nNot voted: {len(not_voted)}\n\n"
    report += "<b>Voted:</b>\n" + "\n".join([str(uid) for uid in voted]) + "\n\n"
    report += "<b>Not Voted:</b>\n" + "\n".join([str(uid) for uid in not_voted])
    await update.message.reply_text(report, parse_mode="HTML")
    context.user_data['elimination_not_voted'] = list(not_voted)
    await update.message.reply_text("Reply /confirmelimination to ban all users who did not vote.")

@admin_only
async def confirm_elimination_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    not_voted = context.user_data.get('elimination_not_voted', [])
    if not not_voted:
        await update.message.reply_text("No users to eliminate. Run /eliminationreport first.")
        return
    from config import GROUP_CHAT_ID
    count = 0
    for user_id in not_voted:
        try:
            await context.bot.ban_chat_member(GROUP_CHAT_ID, user_id)
            count += 1
        except Exception:
            pass
    await update.message.reply_text(f"Banned {count} users who did not vote.")
    context.user_data['elimination_not_voted'] = []

def save_elimination_voters(data):
    with open(ELIMINATION_VOTERS_FILE, 'w') as f:
        json.dump(data, f)

def load_elimination_voters():
    if os.path.exists(ELIMINATION_VOTERS_FILE):
        with open(ELIMINATION_VOTERS_FILE, 'r') as f:
            return json.load(f)
    return {}

@admin_only
async def get_elimination_voters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voters = load_elimination_voters()
    if not voters:
        await update.message.reply_text("No elimination poll voters tracked yet.")
        return
    await update.message.reply_document(document=open(ELIMINATION_VOTERS_FILE, 'rb'), filename='elimination_voters.json', caption="Current elimination poll voters.")

@admin_only
async def import_elimination_voters_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("Please send a JSON file.")
        return
    file = await update.message.document.get_file()
    file_path = ELIMINATION_VOTERS_FILE
    await file.download_to_drive(file_path)
    await update.message.reply_text("Elimination voters file imported successfully.")

# --- Send Elimination Poll Command ---
from config import GROUP_CHAT_ID
from datetime import datetime, timedelta

import asyncio

async def schedule_elimination_reminder(context: ContextTypes.DEFAULT_TYPE, admin_id: int, group_id: int, last_date: datetime):
    # Wait until the deadline
    now = datetime.now()
    wait_seconds = (last_date - now).total_seconds()
    if wait_seconds > 0:
        await asyncio.sleep(wait_seconds)
    # Ping admin in group
    try:
        await context.bot.send_message(
            chat_id=group_id,
            text=f"<b>Elimination poll deadline reached!</b>\n@{admin_id}, please run /eliminationreport and /confirmelimination to complete the process.",
            parse_mode="HTML"
        )
    except Exception:
        pass

@admin_only
async def send_elimination_poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Calculate last date (11 days from now)
    today = datetime.now()
    last_date = (today + timedelta(days=11))
    last_date_str = last_date.strftime('%d %B')
    question = (
        f"⚡️⚠️ #Elimination_Poll_1 [Vote here before {last_date_str} 🗳️]\n\n"
        f"Please vote honestly! You have until {last_date_str} to participate.\n"
        "After the deadline, all non-voters will be removed from the group (after admin confirmation).\n\n"
        "Stay accountable and help keep the challenge strong! 💪"
    )
    options = [
        "🙌 I’m active and still on the challenge!",
        "😔 I have relapsed and will leave the group ASAP"
    ]
    try:
        poll_msg = await context.bot.send_poll(
            chat_id=int(GROUP_CHAT_ID),
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        # Pin the poll
        try:
            await context.bot.pin_chat_message(chat_id=int(GROUP_CHAT_ID), message_id=poll_msg.message_id, disable_notification=True)
        except Exception:
            pass
        # Save poll_id for elimination tracking
        save_elimination_poll_id(poll_msg.poll.id)
        if update.message:
            await update.message.reply_text(f"Elimination poll sent and pinned! Poll ID: {poll_msg.poll.id}")
        # Schedule reminder to ping admin in group after deadline
        from config import ADMIN_ID
        asyncio.create_task(schedule_elimination_reminder(context, ADMIN_ID, int(GROUP_CHAT_ID), last_date))
    except Exception as e:
        if update.message:
            await update.message.reply_text(f"Failed to send elimination poll: {e}")

@admin_only
async def get_poll_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.reply_to_message:
        poll_msg = update.message.reply_to_message
        if hasattr(poll_msg, 'poll') and poll_msg.poll:
            poll_id = poll_msg.poll.id
            await update.message.reply_text(f"Poll ID: <code>{poll_id}</code>", parse_mode="HTML")
            return
    await update.message.reply_text("Reply to a poll message with /getpollid to get its poll ID.")

# To be registered in bot.py:
# CommandHandler('geteliminationvoters', get_elimination_voters_command)
# MessageHandler(filters.Document.ALL, import_elimination_voters_handler)
