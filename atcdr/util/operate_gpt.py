from typing import Dict, List, Optional

import requests  # type: ignore

from .calc_api_cost import CostType, Currency, Model, Rate


class ChatGPT:

    API_URL = "https://api.openai.com/v1/chat/completions"

    # APIの使い方 https://platform.openai.com/docs/api-reference/making-requests
    def __init__(
        self,
        api_key: str,
        model: Model = Model.GPT4O_MINI,
        max_tokens: int = 3000,
        temperature: float = 0.7,
        messages: Optional[List[Dict[str, str]]] = None,
        system_prompt: str = "You are a helpful assistant.",
    ) -> None:

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.messages = (
            messages
            if messages is not None
            else [{"role": "system", "content": system_prompt}]
        )

        self.sum_cost: Currency = Currency(usd=0)
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

        response = response.json()
        reply = response["choices"][0]["message"]["content"]
        usage = response["usage"]

        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        self.sum_cost += Rate.calc_cost(
            model=self.model, cost_type=CostType.INPUT, token_count=input_tokens
        )
        self.sum_cost += Rate.calc_cost(
            model=self.model, cost_type=CostType.OUTPUT, token_count=output_tokens
        )

        return reply
