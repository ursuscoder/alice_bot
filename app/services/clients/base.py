from datetime import datetime
from abc import ABC, abstractmethod
from typing import Union

from app.services.google_sheets.result_sheet import Result


class BaseClient(ABC):
    def _extract_username(self, link):
        return link.split("/")[-1]

    @abstractmethod
    async def find_posts(
        self,
        key_words: list[str],
        group_link: str,
        offset_date: datetime = None,
    ) -> Union[list[Result], ValueError]:
        pass
