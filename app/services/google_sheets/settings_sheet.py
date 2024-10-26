from datetime import datetime
from typing import Optional
from app.services.google_sheets.base import ModelSheetAsync, Model
from app.core.config import settings as s


class SheetDateTime:
    def __call__(self, *args, **kwds):
        pass


class Settings:
    key_words: Optional[list] = None
    last_date: Optional[datetime] = None
    prompt_pattern: Optional[str] = None

    def __init__(
        self,
        key_words: list = None,
        last_date: datetime = None,
        prompt_pattern: str = None,
    ):
        self.key_words = key_words
        self.last_date = last_date
        self.prompt_pattern = prompt_pattern


class SettingsModel(Model):
    row: Optional[int] = None
    key_words: Optional[str] = None
    last_date: Optional[str] = None
    prompt_pattern: Optional[str] = None

    class Config:
        # Pydantic будет автоматически пытаться конвертировать строку в datetime
        json_encoders = {datetime: lambda v: v.strftime("%d.%m.%Y")}


class SettingsSheetAsync(ModelSheetAsync):
    async def get_settings(self) -> Settings:
        models = await self.get_models(row=2)
        if models:
            (model,) = models
            key_words = model.key_words.split(",")
            last_date = (
                datetime.strptime(model.last_date.split()[0], "%d.%m.%Y")
                if model.last_date
                else None
            )
            return Settings(key_words, last_date, prompt_pattern=model.prompt_pattern)
        return Settings()


settings_sh = SettingsSheetAsync(
    SettingsModel,
    s.SETTINGS_SPREADSHEET_ID,
    s.SETTINGS_SHEET_NAME,
    s.SETTINGS_RANGE_COLUMN,
    s.GOOGLE_USER_INFO,
)
