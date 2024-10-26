from enum import Enum
from typing import Optional

from pydantic import validator
from app.services.google_sheets.base import ModelSheetAsync, Model

from app.core.config import settings as s


class GroupTypes(Enum):
    TELEGRAM = "TELEGRAM"
    VK = "VK"


class Group(Model):
    row: Optional[int] = None
    url: Optional[str] = None
    type: Optional[GroupTypes] = None
    title: Optional[str] = None
    members_count: Optional[int] = None

    # Валидаторы для приведения типов
    @validator("row", "members_count", pre=True, always=True)
    def parse_int(cls, value):
        if isinstance(value, str):
            return int(value)
        return value


group_sh = ModelSheetAsync(
    Group,
    s.GROUP_SPREADSHEET_ID,
    s.GROUP_SHEET_NAME,
    s.GROUP_RANGE_COLUMN,
    s.GOOGLE_USER_INFO,
)
