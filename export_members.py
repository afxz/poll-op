# Telethon script to export all group members to a JSON file
# Usage: python export_members.py
# You will need your own API ID and API HASH from https://my.telegram.org

import os
import json
from telethon import TelegramClient
import asyncio

CONFIG_FILE = 'userbot_config.json'

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    API_ID = config.get('API_ID')
    API_HASH = config.get('API_HASH')
    PHONE = config.get('PHONE')
else:
    API_ID = input('Enter your API ID: ')
    API_HASH = input('Enter your API HASH: ')
    PHONE = input('Enter your phone number (with country code): ')
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'API_ID': API_ID, 'API_HASH': API_HASH, 'PHONE': PHONE}, f)

async def main():
    group = input('Enter the group username or ID: ')
    # Handle -100 prefix for supergroups
    if group.startswith('-100'):
        try:
            group = int(group)
        except Exception:
            group = group[4:]
    elif group.lstrip('-').isdigit():
        group = int(group)
    client = TelegramClient('userbot_session', API_ID, API_HASH)
    await client.start(phone=PHONE)
    print('Logged in!')
    try:
        entity = await client.get_entity(group)
    except Exception as e:
        print(f'Could not find group: {e}')
        return
    members = []
    async for user in client.iter_participants(entity):
        members.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_bot': user.bot
        })
    with open('group_members.json', 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=2)
    print(f'Exported {len(members)} members to group_members.json')
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
