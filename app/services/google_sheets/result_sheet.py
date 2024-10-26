from datetime import datetime
from typing import Optional

from pydantic import validator
from app.services.google_sheets.base import ModelSheetAsync, Model

from app.core.config import settings as s


class Result(Model):
    row: Optional[int] = None
    key_words: Optional[str] = None
    text: Optional[str] = None
    link: Optional[str] = None
    date: Optional[str] = None
    group: Optional[str] = None
    image_count: Optional[int] = None
    video_count: Optional[int] = None
    category: Optional[str] = None
    score: Optional[int] = None
    comment: Optional[str] = None

    @validator("image_count", "video_count", "score", pre=True, always=True)
    def parse_int(cls, value):
        if isinstance(value, str):
            return int(value)
        return value


result_sh = ModelSheetAsync(
    Result,
    s.RESULT_SPREADSHEET_ID,
    s.RESULT_SHEET_NAME,
    s.RESULT_RANGE_COLUMN,
    s.GOOGLE_USER_INFO,
)
