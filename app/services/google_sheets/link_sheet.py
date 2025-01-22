from enum import Enum
from typing import Optional

from pydantic import validator
from app.services.google_sheets.base import ModelSheetAsync, Model

from app.core.config import settings as s


class Link(Model):
    row: Optional[int] = None
    url: Optional[str] = None
    is_analyzed: str | None = None

    # Валидаторы для приведения типов
    @validator("row", pre=True, always=True)
    def parse_int(cls, value):
        if isinstance(value, str):
            return int(value)
        return value


link_sh = ModelSheetAsync(
    Link,
    s.LINKS_SPREADSHEET_ID,
    s.LINKS_SHEET_NAME,
    s.LINKS_RANGE_COLUMN,
)
