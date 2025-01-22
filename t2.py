from app.core.config import settings
from asyncio import run

from app.services.clients.telegram_client import TelegramClient


async def test():
    client = TelegramClient(settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)
    await client.client.connect()
    await client.client.start()
    url = "https://t.me/sofianri/11238"
    res = await client.get_post(url)
    print(res.text, res.image_count, res.date)


run(test())
