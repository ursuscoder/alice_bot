from typing import Union
from telethon import TelegramClient as TelethonCilent, functions
from datetime import datetime, timedelta
from app.services.clients.base import BaseClient
from app.services.google_sheets.group_sheet import Group
from app.services.google_sheets.result_sheet import Result

from app.core.log import logger as log


class TelegramClient(BaseClient):
    def __init__(self, api_id, api_hash):

        self.client = TelethonCilent(
            "account", api_id, api_hash, system_version="4.16.30-vxCUSTOM"
        )

    async def update_group_info(self, group: Group):
        group_username = self._extract_username(group.url)
        try:
            chat = await self.client.get_entity(group_username)
            result = await self.client(functions.channels.GetFullChannelRequest(chat))
            group.title = chat.title
            group.members_count = result.full_chat.participants_count
            return group
        except Exception as e:
            log.error(f"Ошибка получения чата: {e}")
            return None

    async def find_posts(
        self,
        key_words: list[str],
        group_link: str,
        offset_date: datetime = None,
    ) -> Union[list[Result], ValueError]:
        lower_key_words = list(map(str.lower, key_words))
        try:
            group_username = self._extract_username(group_link)
            try:
                chat = await self.client.get_entity(group_username)
            except Exception as e:
                log.error(f"Ошибка получения чата: {e}")
                return []

            result: list[Result] = []
            limit = None if offset_date else 10
            grouped_id = None
            async for message in self.client.iter_messages(
                chat, limit=limit, reverse=True, offset_date=offset_date
            ):
                if message.message:
                    text: str = message.message
                    lower_text = text.lower()
                    words = [
                        key_word
                        for key_word in lower_key_words
                        if key_word in lower_text
                    ]

                    if words:
                        result.append(
                            Result(
                                key_words=", ".join(sorted(words)),
                                text=text,
                                link=f"{group_link.strip()}/{message.id}",
                                date=(message.date + timedelta(hours=3)).strftime(
                                    "%d.%m.%Y %H:%M:%S"
                                ),
                                image_count=int(bool(message.photo)),
                                video_count=int(bool(message.video)),
                            )
                        )

                        grouped_id = message.grouped_id or 1
                        continue

                if result and grouped_id == message.grouped_id:
                    result[-1].image_count += int(bool(message.photo))
                    result[-1].video_count += int(bool(message.video))

            return result
        except ValueError as ex:
            return ex
        except Exception as ex:
            print(f"Ошибка получения сообщений: {ex}")
