from abc import ABC, abstractmethod


class BaseChatGPT(ABC):
    @abstractmethod
    def send_message(self, message: str) -> None:
        pass

    @abstractmethod
    def read_message(self) -> str:
        pass


from .by_api import APIChatGPT
from .by_applescript import SafariChatGPT


class ChatGPT:
    @staticmethod
    def create(method: str, api_key: str = None) -> BaseChatGPT:
        if method == "API":
            if not api_key:
                raise ValueError("APIキーを指定してください.")
            return APIChatGPT(api_key)
        elif method == "AppleScript":
            return SafariChatGPT()
        else:
            raise ValueError("Invalid method specified. Choose 'API' or 'AppleScript'.")


# 使用例
def main():
    try:
        # APIを使用するクライアント
        api_key = "YOUR_API_KEY"
        gptapi = ChatGPT.create("API", api_key)
        gptapi.send_message("Hello, how are you?")
        api_response = gptapi.read_message()
        print(f"API Response: {api_response}")

        # AppleScriptを使用するクライアント
        gptscript = ChatGPT.create("AppleScript")
        gptscript.send_message("Hello, how are you?")
        script_response = gptscript.read_message()
        print(f"Safari Response: {script_response}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
