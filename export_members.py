# Telethon script to export all group members to a JSON file
# Usage: python export_members.py
# You will need your own API ID and API HASH from https://my.telegram.org

from telethon import TelegramClient
import json
import asyncio

API_ID = input('Enter your API ID: ')
API_HASH = input('Enter your API HASH: ')
PHONE = input('Enter your phone number (with country code): ')

async def main():
    group = input('Enter the group username or ID: ')
    client = TelegramClient('userbot_session', API_ID, API_HASH)
    await client.start(phone=PHONE)
    print('Logged in!')
    entity = await client.get_entity(group)
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
