from .by_api import APIChatGPTClient
from .by_applescript import SafariChatGPTClient
from .base import BaseChatGPTClient
class ChatGPTClientFactory:
    @staticmethod
    def create_client(method: str, api_key: str = None) -> BaseChatGPTClient:
        if method == "API":
            if not api_key:
                raise ValueError("API key is required for API method")
            return APIChatGPTClient(api_key)
        elif method == "AppleScript":
            return SafariChatGPTClient()
        else:
            raise ValueError("Invalid method specified. Choose 'API' or 'AppleScript'.")

# 使用例
def main():
    try:
        # APIを使用するクライアント
        api_key = "YOUR_API_KEY"
        gptapi = ChatGPTClientFactory.create_client("API", api_key)
        gptapi.send_message("Hello, how are you?")
        api_response = gptapi.read_message()
        print(f"API Response: {api_response}")

        # AppleScriptを使用するクライアント
        gptscript = ChatGPTClientFactory.create_client("AppleScript")
        gptscript.send_message("Hello, how are you?")
        script_response = gptscript.read_message()
        print(f"Safari Response: {script_response}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
