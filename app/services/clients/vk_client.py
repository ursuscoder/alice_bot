from collections import Counter
from datetime import datetime, timedelta
from typing import Union

from aiohttp import ClientSession, TCPConnector
from app.services.clients.base import BaseClient
from app.services.google_sheets.result_sheet import Result
from app.services.google_sheets.group_sheet import Group


class VKClient(BaseClient):
    def __init__(self, access_token: str):
        self.client = ClientSession(connector=TCPConnector(ssl=False))
        self.access_token = access_token

    async def update_group_info(self, group: Group):
        domain = self._extract_username(group.url)
        params = dict(
            access_token=self.access_token,
            group_id=domain,
            fields=["members_count"],
            v=5.199,
        )
        url = f"https://api.vk.com/method/groups.getById"
        try:
            async with self.client.post(url=url, data=params) as request:
                info: dict = (await request.json())["response"]["groups"][0]
                group.title = info["name"]
                group.members_count = info["members_count"]
                return group
        except Exception as er:
            print(er)
            return None

    async def find_posts(
        self,
        key_words: list[str],
        group_link: str,
        offset_date: datetime = None,
    ) -> Union[list[Result], ValueError]:
        lower_key_words = list(map(str.lower, key_words))
        try:
            domain = self._extract_username(group_link)
            params = dict(
                access_token=self.access_token,
                domain=domain,
                count=100,
                offset=0,
                v=5.199,
            )
            url = f"https://api.vk.com/method/wall.get"
            result: list[Result] = []
            while True:
                async with self.client.post(url=url, data=params) as request:
                    vk_posts: list[dict] = (await request.json())["response"]["items"]
                    for post in vk_posts:
                        date = datetime.fromtimestamp(post["date"])
                        if date <= offset_date:
                            break
                        text = ""
                        if post.get("text"):
                            text += post["text"].lower().replace("ё", "е")
                        if copy_history := post.get("copy_history"):
                            for copy_post in copy_history:
                                if copy_text := copy_post.get("text"):
                                    text += copy_text.lower()
                        if text:
                            lower_text = text.lower()
                            words = [
                                key_word
                                for key_word in lower_key_words
                                if key_word in lower_text
                            ]

                            if words:
                                attachment_counts = Counter(
                                    att["type"] for att in post["attachments"]
                                )
                                result.append(
                                    Result(
                                        key_words=", ".join(sorted(words)),
                                        text=text,
                                        link=f"https://vk.com/wall{post['owner_id']}_{post['id']}",
                                        date=(date + timedelta(hours=3)).strftime(
                                            "%d.%m.%Y %H:%M:%S"
                                        ),
                                        image_count=attachment_counts["photo"],
                                        video_count=attachment_counts["video"],
                                    )
                                )

                    if len(vk_posts) < params["count"]:
                        break
                    params["offset"] += params["count"]

                return result
        except ValueError as ex:
            return ex
