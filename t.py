from telethon.sync import TelegramClient, events
from app.core.config import settings

with TelegramClient(
    "new", settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH
) as client:
    client.send_message("me", "Hello, myself!")
    print(client.download_profile_photo("me"))

    @client.on(events.NewMessage(pattern="(?i).*Hello"))
    async def handler(event):
        await event.reply("Hey!")

    client.run_until_disconnected()
