import dataclasses
import typing

import requests

from evaluation.config import LLMConfig

SYSTEM_PROMPT: typing.Final = (
    "Ты отвечаешь на вопросы только на основе предоставленного контекста. "
    "Не выдумывай информацию. "
    "Если в контексте нет ответа, скажи, что информации недостаточно."
)
USER_PROMPT_TEMPLATE: typing.Final = (
    "Контекст: {context} Вопрос пользователя: {query} Ответь на вопрос только на основе контекста."
)


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class LLMClient:
    config: LLMConfig

    def request(
        self,
        query: str,
        context: str,
    ):
        response: typing.Final = requests.post(
            self.config.url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.model,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": USER_PROMPT_TEMPLATE.format(context=context, query=query),
                    },
                ],
                "temperature": 0,
            },
            timeout=60,
        )
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]
