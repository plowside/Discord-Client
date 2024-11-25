import asyncio, websockets, logging, httpx, json

from config import *


class DiscordClient:
    def __init__(self, token):
        self.token = token
        self.websocket = None
        self.heartbeat_interval = None
        self.DISCORD_GATEWAY = "wss://gateway.discord.gg/?v=10&encoding=json"
        self.user = None

    async def connect(self):
        self.websocket = await websockets.connect(self.DISCORD_GATEWAY)
        await self.identify()
        try:
            await self.listen()
        except Exception as e:
            if 'Authentication failed' in str(e):
                return print(f'[-] Invalid discord token')
            raise e

    async def identify(self):
        payload = {"op": 2, "d": {"token": DISCORD_TOKEN, "capabilities": 30717,
                                  "properties": {"os": "Windows", "browser": "Chrome", "device": "",
                                                 "system_locale": "ru",
                                                 "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                                                 "browser_version": "131.0.0.0", "os_version": "10",
                                                 "referring_domain": "discord.com", "referrer_current": "",
                                                 "referring_domain_current": "", "release_channel": "stable",
                                                 "client_build_number": 347699, "client_event_source": None},
                                  "presence": {"status": "unknown", "since": 0, "activities": [], "afk": False},
                                  "compress": False, "client_state": {"guild_versions": {}}}}
        await self.websocket.send(json.dumps(payload))

    async def start_receiving_messages(self):
        for message in messages_to_search:
            payload = {"op": 36,"d": {"guild_id": message['guild_id']}}
            await self.websocket.send(json.dumps(payload))
            payload = {"op":37,"d":{"subscriptions":{message['guild_id']:{"typing":True,"threads":True,"activities":True,"members":[],"member_updates":False,"channels":{},"thread_member_lists":[]}}}}
            await self.websocket.send(json.dumps(payload))
            print(f"[+] Сервер активирован: {message['guild_id']}")

    async def heartbeat(self):
        while True:
            await asyncio.sleep(self.heartbeat_interval / 1000)
            await self.websocket.send(json.dumps({"op": 1, "d": None}))

    async def listen(self):
        async for message in self.websocket:
            data = json.loads(message)

            if data["op"] == 10:  # HELLO
                self.heartbeat_interval = data["d"]["heartbeat_interval"]
                asyncio.create_task(self.heartbeat())
                asyncio.create_task(self.start_receiving_messages())

            elif data['t'] == 'READY':
                message = data.get('d', {})
                self.user = message.get('user', None)
                if not self.user:
                    print('[-] Не получен юзер, возможно неверный токен либо версия сборки')
                else:
                    print(f"[+] Вход выполнен как {self.user['username']}#{self.user['discriminator']}")

            elif data['t'] == 'MESSAGE_CREATE':
                message = data.get('d', {})
                author = message.get('author', {})
                member = message.get('member', {})
                author = {
                    'id': author.get('id', 0),
                    'username': author.get('username', None),
                    'discriminator': author.get('discriminator', 0),
                    'global_name': author.get('global_name', ''),
                    'avatar': author.get('global_name', '')
                }
                member = {
                    'nick': member.get('nickname', None),
                    'joined_at': member.get('joined_at', ''),
                    'roles': member.get('roles', []),
                    'flags': member.get('flags', False),
                    'premium_since': member.get('premium_since', None),
                    'mute': member.get('mute', False),
                    'deaf': member.get('deaf', False),
                    'communication_disabled_until': member.get('communication_disabled_until', None),
                    'avatar': member.get('nickname', ''),
                    'banner': member.get('nickname', ''),
                }
                message = {
                    'id': message.get('id', 0),
                    'content': message.get('content', ''),
                    'channel_id': message.get('channel_id', 0),
                    'guild_id': message.get('guild_id', None),
                    'author': author,
                    'member': member
                }
                # print(f"> guild {message['guild_id']} channel {message['channel_id']} | {message['author']['username']}#{message['author']['discriminator']}: {message['content']}")
                asyncio.create_task(self.handle_message(message))

    async def handle_message(self, message):
        message_found = False
        for filter_message in messages_to_search:
            message_content = message['content']
            text_to_search = filter_message['text_to_search']
            if filter_message['search_parameters']['is_lower']:
                message_content = message_content.lower()
                text_to_search = text_to_search.lower()

            text_to_send = f"<b>🔍 Найдено сообщение</b>\n├ Автор: <b>{message['author']['global_name']} | {message['author']['username']}#{message['author']['discriminator']}</b>\n└ Слово: <code>{text_to_search}</code>"
            if filter_message['search_parameters']['is_equal'] and text_to_search == message_content:
                await self.tg_notify(text_to_send)
                message_found = True
            elif not filter_message['search_parameters']['is_equal'] and text_to_search in message_content:
                await self.tg_notify(text_to_send)
                message_found = True

        if message_found:
            print(f"[+] Сообщение найдено: Сервер={message['guild_id']}|Канал={message['channel_id']}")

    @staticmethod
    async def tg_notify(text):
        async with httpx.AsyncClient(timeout=60) as client:
            for user_id in TELEGRAM_USER_IDs:
                resp = await client.post(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage', json={
                    'chat_id': user_id,
                    'text': text,
                    'parse_mode': 'HTML'
                })
                if resp.status_code != 200:
                    print(f'[-] Не удалось отправить в тг: {resp.status_code} | {resp.json()}')


async def main():
    client = DiscordClient(DISCORD_TOKEN)
    await client.connect()

if __name__ == "__main__":
    asyncio.run(main())