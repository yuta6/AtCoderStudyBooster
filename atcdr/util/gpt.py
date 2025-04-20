import os
from enum import Enum
from typing import Dict, List, Optional

import requests


class Model(Enum):
    GPT4O = 'gpt-4o'
    GPT41 = 'gpt-4.1'
    GPT41_MINI = 'gpt-4.1-mini'
    GPT41_NANO = 'gpt-4.1-nano'
    GPT4O_MINI = 'gpt-4o-mini'
    O1_PREVIEW = 'o1-preview'
    O1 = 'o1'
    O3 = 'o3'
    O1_MINI = 'o1-mini'
    O3_MINI = 'o3-mini'
    O4_MINI = 'o4-mini'


def set_api_key() -> Optional[str]:
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and validate_api_key(api_key):
        return api_key
    elif api_key:
        print('環境変数に設定されているAPIキーの検証に失敗しました ')
    else:
        pass

    api_key = input(
        'https://platform.openai.com/api-keys からchatGPTのAPIキーを入手しましょう。\nAPIキー入力してください: '
    )
    if validate_api_key(api_key):
        print('APIキーのテストに成功しました。')
        print('以下, ~/.zshrcにAPIキーを保存しますか? [y/n]')
        if input() == 'y':
            zshrc_path = os.path.expanduser('~/.zshrc')
            with open(zshrc_path, 'a') as f:
                f.write(f'export OPENAI_API_KEY={api_key}\n')
            print(
                f'APIキーを {zshrc_path} に保存しました。次回シェル起動時に読み込まれます。'
            )
        os.environ['OPENAI_API_KEY'] = api_key
        return api_key
    else:
        print('コード生成にはAPIキーが必要です。')
        return None


def validate_api_key(api_key: str) -> bool:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    response = requests.get('https://api.openai.com/v1/models', headers=headers)

    if response.status_code == 200:
        return True
    else:
        print('APIキーの検証に失敗しました。')
        return False


class ChatGPT:
    API_URL = 'https://api.openai.com/v1/chat/completions'

    # APIの使い方 https://platform.openai.com/docs/api-reference/making-requests
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Model = Model.GPT41_MINI,
        max_tokens: int = 3000,
        temperature: float = 0.7,
        messages: Optional[List[Dict[str, str]]] = None,
        system_prompt: str = 'You are a helpful assistant.',
    ) -> None:
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.messages = (
            messages
            if messages is not None
            else [{'role': 'system', 'content': system_prompt}]
        )

        self.__headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

    def tell(self, message: str) -> str:
        self.messages.append({'role': 'user', 'content': message})

        settings = {
            'model': self.model.value,
            'messages': self.messages,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
        }

        response = requests.post(self.API_URL, headers=self.__headers, json=settings)
        responsej = response.json()
        try:
            reply = responsej['choices'][0]['message']['content']
        except KeyError:
            print('Error:レスポンスの形式が正しくありません. \n' + str(responsej))
            return 'Error: Unable to retrieve response.'

        self.messages.append({'role': 'assistant', 'content': reply})

        # usage = responsej['usage']
        # input_tokens = usage.get('prompt_tokens', 0)
        # output_tokens = usage.get('completion_tokens', 0)

        return reply
