from pydantic_settings import BaseSettings
import json


class Settings(BaseSettings):
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    VK_API_TOKEN: str
    GROUP_SPREADSHEET_ID: str
    GROUP_SHEET_NAME: str
    GROUP_RANGE_COLUMN: str
    RESULT_SPREADSHEET_ID: str
    RESULT_SHEET_NAME: str
    RESULT_RANGE_COLUMN: str
    SETTINGS_SPREADSHEET_ID: str
    SETTINGS_SHEET_NAME: str
    SETTINGS_RANGE_COLUMN: str
    GOOGLE_USER_INFO: dict

    TELEGRAM_BOT_API_TOKEN: str
    TELEGRAM_GROUP_ID: int

    class Config:
        env_file = ".env"

    @property
    def google_user_info(self):
        return json.loads(self.GOOGLE_USER_INFO)


settings = Settings()
