from app.core.log import logger as log
import json
import re
from g4f.client import Client
from typing import Any, Dict


class PromptV1:
    @staticmethod
    def generate(prompt: str, text: str, image_count: int, video_count: int) -> str:
        return prompt.format(
            text=text, image_count=image_count, video_count=video_count
        )

    @staticmethod
    def validate(response_content: str) -> Dict[str, Any]:
        clean_content = re.sub(r"```json|```", "", response_content).strip()
        try:
            res = json.loads(clean_content)
            required_keys = ["category", "comment", "score"]
            if not all(key in res for key in required_keys):
                raise ValueError(f"Отсутствуют необходимые ключи: {required_keys}")
            return res
        except (json.JSONDecodeError, ValueError) as e:
            log.warning(f"Ошибка в работе с AI: {e}")
            return {}


import asyncio
from collections import Counter


class AiClientAsync:
    async def _ask_gpt(self, prompt_text):
        client = Client()
        response = await client.chat.completions.async_create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_text}],
        )
        response_content = response.choices[0].message.content
        return response_content

    async def analyze_post(self, prompt_text: str, prompt) -> Dict[str, Any]:
        valid_responses = []
        while True:
            response = await self._ask_gpt(prompt_text)
            if parsed_response := prompt.validate(response):
                valid_responses.append(parsed_response)
            else:
                await asyncio.sleep(1)

            if len(valid_responses) == 3:
                break

        categories = [res["category"] for res in valid_responses]
        category_counter = Counter(categories)

        most_common_category = category_counter.most_common(1)[0][0]

        matching_responses = [
            res for res in valid_responses if res["category"] == most_common_category
        ]

        best_response = min(
            matching_responses, key=lambda res: (res["score"], len(res["comment"]))
        )

        return best_response


ai_client = AiClientAsync()
