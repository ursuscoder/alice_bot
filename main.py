from app.core.config import settings
from app.core.log import logger as log


import asyncio
from app.services.ai.ai_client import PromptV1
from app.services.clients import TelegramClient, VKClient
from app.services.google_sheets.group_sheet import group_sh, Group, GroupTypes
from app.services.google_sheets.result_sheet import result_sh, Result
from app.services.google_sheets.settings_sheet import settings_sh, Settings
from app.services.ai.ai_client import ai_client

from app.services.telegram_bot.bot import send_message


async def process_group(
    group: Group,
    sh_settings: Settings,
    telegram_client: TelegramClient,
    vk_client: VKClient,
):
    try:
        if group.type == GroupTypes.TELEGRAM.value:
            await telegram_client.update_group_info(group)
            await group_sh.update_models(group)

            log.info(f"Группа {group.type} {group.url} {group.members_count}")

            log.info(f"Получаем сообщения из {group.url}")
            posts = await telegram_client.find_posts(
                sh_settings.key_words,
                group.url,
                offset_date=sh_settings.last_date,
            )
        elif group.type == GroupTypes.VK.value:
            await vk_client.update_group_info(group)
            await group_sh.update_models(group)

            log.info(f"Группа {group.type} {group.url} {group.members_count}")

            log.info(f"Получаем сообщения из {group.url}")
            posts = await vk_client.find_posts(
                sh_settings.key_words,
                group.url,
                offset_date=sh_settings.last_date,
            )
        else:
            posts = []
    except Exception as ex:
        return ex

    for post in posts:
        post.group = group.url
        model_in_db = await result_sh.get_models(
            key_words=post.key_words, link=post.link
        )
        if model_in_db:
            return

        log.info(f"Найден новый пост: {post.link}")
        post_promt = PromptV1.generate(
            sh_settings.prompt_pattern,
            post.text,
            post.image_count,
            post.video_count,
        )
        log.info(f"Анализирую пост: {post.link}")
        await analyze_and_update_post(post, post_promt)
        models = await result_sh.create_models(post)
        if models:
            for model in models:
                log.info(f"Сохранен новый пост: {model.link}")
                text = f"<b>Найден новый пост</b>: {post.link}" + "\n"
                text += f"Кл. слова: <code>{post.key_words}</code>" + "\n"
                text += f"Дата: <code>{post.date.split()[0]}</code>" + "\n"
                text += f"Кол-во фото: <code>{post.image_count}</code>" + "\n"
                text += f"Кол-во видео: <code>{post.image_count}</code>" + "\n"
                text += f"Категория: <code>{post.category}</code>" + "\n"
                text += f"Баллы: <code>{post.score}</code>"
                await send_message(text)


async def analyze_and_update_post(post: Result, post_promt: str):
    res = await ai_client.analyze_post(post_promt, PromptV1())
    for key, value in res.items():
        setattr(post, key, value)


async def init_telegram_client():
    try:
        client = TelegramClient(settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)
        await client.client.connect()
        await client.client.start()
        return client
    except Exception as ex:
        raise RuntimeError(f"Ошибка при подключении к Telegram: {ex}")


async def init_vk_client():
    try:
        client = VKClient(settings.VK_API_TOKEN)
        return client
    except Exception as ex:
        raise RuntimeError(f"Ошибка при подключении к Вконтакте: {ex}")


async def close_client(client, name):
    try:
        if name == "Telegram":
            await client.client.close()
        elif name == "VK":
            await client.client.disconnect()
    except Exception as ex:
        log.error(f"Ошибка при закрытии клиента {name}: {ex}")


async def main():
    await send_message("Приложение запущено")

    while True:
        try:
            telegram_client = await init_telegram_client()
            vk_client = await init_vk_client()
        except Exception as er:
            await send_message(f"Ошибка при инициализации клиента:\n{er}")
            continue  # Повторить попытку через 10 минут

        try:
            sh_settings: Settings = await settings_sh.get_settings()
            if sh_settings.key_words:
                groups: list[Group] = await group_sh.get_models()
                for group in groups:
                    await process_group(group, sh_settings, telegram_client, vk_client)

        except Exception as ex:
            log.error(f"Ошибка обработки группы: {ex}")
            await send_message(f"Ошибка обработки группы: {ex}")

        finally:
            await close_client(telegram_client, "Telegram")
            await close_client(vk_client, "VK")

        log.info("Перерыв 10 минут")
        await asyncio.sleep(10 * 60)


if __name__ == "__main__":
    asyncio.run(main())
