import asyncio
from aiogram.enums.parse_mode import ParseMode
from aiogram import Bot, types
from aiogram.client.bot import DefaultBotProperties
from app.core.config import settings

bot = Bot(
    token=settings.TELEGRAM_BOT_API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


async def send_message(
    text: str,
    channel_id: int = settings.TELEGRAM_GROUP_ID,
):
    await bot.send_message(channel_id, text)
