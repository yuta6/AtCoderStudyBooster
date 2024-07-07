import requests
from .base import BaseChatGPTClient
class APIChatGPTClient(BaseChatGPTClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.messages = []

    def send_message(self, message: str) -> None:
        self.messages.append({"role": "user", "content": message})

    def read_message(self) -> str:
        data = {
            "model": "gpt-4",
            "messages": self.messages,
            "max_tokens": 150,
            "temperature": 0.7
        }
        response = requests.post(self.api_url, headers=self.headers, json=data)
        response.raise_for_status()
        completion = response.json()
        message = completion['choices'][0]['message']['content']
        self.messages.append({"role": "assistant", "content": message})
        return message
