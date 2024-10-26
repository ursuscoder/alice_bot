from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List
import asyncio
from pydantic import BaseModel
import logging as log


class GoogleSheetAsync:
    def __init__(self, spreadsheet_id, sheet_name, column_range, user_info):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.column_range: str = column_range
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = self._authenticate(user_info)

    def _authenticate(self, user_info):
        creds = Credentials.from_authorized_user_info(user_info, self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.scopes
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    async def get(self, range_name=None):
        range_name = range_name or self.column_range
        try:
            service = await asyncio.to_thread(
                build, "sheets", "v4", credentials=self.creds
            )
            sheet = service.spreadsheets()

            request = sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!{range_name}",
            )

            result = await asyncio.to_thread(request.execute)
            return result.get("values", [])
        except HttpError as err:
            log.error(f"An error occurred: {err}")
            return []

    async def set(self, values, range_name=None):
        range_name = range_name or self.column_range
        try:
            service = await asyncio.to_thread(
                build, "sheets", "v4", credentials=self.creds
            )
            body = {"values": values}
            request = (
                service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{self.sheet_name}!{range_name}",
                    valueInputOption="RAW",
                    body=body,
                )
            )
            result = await asyncio.to_thread(request.execute)
            log.info(f"{result.get('updatedCells')} cells updated.")
        except HttpError as err:
            log.error(f"An error occurred: {err}")


class Model(BaseModel):
    class Config:
        extra = "ignore"
        use_enum_values = True

    def __str__(self):

        attrs = ",\t".join([f"{key}: {value}" for key, value in self.dict().items()])
        return f"{self.__class__.__name__}[ {attrs} ]"

    @classmethod
    def from_data(cls, data: List[List]):
        """
        Создает список экземпляров класса на основе предоставленных данных.
        :param data: Список списков, где каждый вложенный список соответствует атрибутам класса.
        :raises ValueError: Если количество предоставленных значений не соответствует количеству атрибутов.
        """
        attributes = list(cls.__annotations__.keys())
        res = []
        for row in data:
            if len(row) > len(attributes):
                raise ValueError(
                    f"Column mismatch: expected {len(attributes)} columns, "
                    f"but got {len(row)}. Expected attributes: {attributes}"
                )

            row_data = {attr: value for attr, value in zip(attributes, row)}
            res.append(cls(**row_data))

        return res


class ModelSheetAsync:
    def __init__(
        self,
        model: Model,
        spreadsheet_id,
        sheet_name,
        column_range,
        user_info,
        start_row=2,
    ):
        self._sheet = GoogleSheetAsync(
            spreadsheet_id, sheet_name, column_range, user_info
        )
        self._model = model
        self._start_row = start_row
        self._lock = asyncio.Lock()

    def _clean_data(self, data) -> list:
        data = data[self._start_row - 1 :]
        return [[i] + row for i, row in enumerate(data, self._start_row) if row]

    async def get_models(self, **filters) -> list[Model]:
        data = await self._sheet.get()
        cleaned_data = self._clean_data(data)
        models = self._model.from_data(cleaned_data)

        filtered_models = [
            model
            for model in models
            if all(getattr(model, key, None) == value for key, value in filters.items())
        ]
        return filtered_models

    async def update_models(self, *models: Model) -> None:

        rows = sorted(
            [
                getattr(model, "row", None)
                for model in models
                if getattr(model, "row", None) is not None
            ]
        )

        modeled_rows = []
        current_model = []

        for row in rows:
            if not current_model or row == current_model[-1] + 1:
                current_model.append(row)
            else:
                modeled_rows.append(current_model)
                current_model = [row]

        if current_model:
            modeled_rows.append(current_model)

        for model in modeled_rows:
            values = []
            for row in model:

                corresponding_models = [
                    g for g in models if getattr(g, "row", None) == row
                ]
                for g in corresponding_models:
                    row_values = [
                        getattr(g, key, "")
                        for key, value in g.__annotations__.items()
                        if key != "row"
                    ]
                    values.append(row_values)

            if values:
                column_letters = [col for col in self._sheet.column_range.split(":")]

                range_start = f"{column_letters[0]}{min(model)}"
                range_end = f"{column_letters[1]}{max(model)}"
                range_name = f"{range_start}:{range_end}"

                await self._sheet.set(values, range_name)

    async def create_models(self, *models: Model) -> None:
        async with self._lock:
            if not models:
                return None

            existing_data = await self._sheet.get()

            start_row = len(existing_data) + 1

            values = []
            for i, model in enumerate(models):

                if model.row:
                    raise ValueError("Can't create an existing row.")
                attrs = model.__annotations__
                model.row = start_row + i
                row_values = [
                    getattr(model, key, "")
                    for key, value in attrs.items()
                    if key != "row"
                ]
                values.append(row_values)

            column_letters = [col for col in self._sheet.column_range.split(":")]
            range_start = f"{column_letters[0]}{start_row}"
            range_end = f"{column_letters[1]}{start_row + len(values) - 1}"
            range_name = f"{range_start}:{range_end}"

            await self._sheet.set(values, range_name)
            return models
