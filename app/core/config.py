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

    TELEGRAM_BOT_API_TOKEN: str
    TELEGRAM_GROUP_ID: int

    class Config:
        env_file = ".env"

    @property
    def google_user_info(self):
        try:
            with open("token.json", "r") as file:
                return json.load(file)  # Загружаем JSON-данные из файла
        except FileNotFoundError:
            raise FileNotFoundError(
                "Файл 'token.json' не найден. Убедитесь, что файл существует."
            )
        except json.JSONDecodeError:
            raise ValueError("Файл 'token.json' содержит некорректный JSON.")


settings = Settings()
