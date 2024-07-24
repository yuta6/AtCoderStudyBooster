from enum import Enum

import requests  # type: ignore


class Model(Enum):
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"


class ChatGPT:

    API_URL = "https://api.openai.com/v1/chat/completions"

    # APIの使い方 https://platform.openai.com/docs/api-reference/making-requests
    def __init__(
        self,
        api_key: str,
        model: Model = Model.GPT4O_MINI,
        max_tokens: int = 3000,
        temperature: float = 0.7,
        messages: list = [],
    ) -> None:

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.messages = messages
        self.__headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    def tell(self, message: str) -> str:

        self.messages.append({"role": "user", "content": message})

        settings = {
            "model": self.model,
            "messages": self.messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        response = requests.post(self.API_URL, headers=self.__headers, json=settings)
        reply = response.json["choices"][0]["message"]["content"]

        return reply
