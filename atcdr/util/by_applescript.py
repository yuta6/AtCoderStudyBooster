# Apple ScriptからSafariを操作することによってchatGPTを利用する.
from .operate_gpt import BaseChatGPTClient
from .safari_operator_by_applescript import SafariWindow


class SafariChatGPTClient(BaseChatGPTClient):
    def __init__(self) -> None :
        CHAT_GPT_URL = "https://chat.openai.com/chat?temporary-chat=true"
        self.window = SafariWindow()
        self.tab = self.window.create_new_tab(CHAT_GPT_URL)

    def send_message(self, message: str) -> None:
        script = f"""
        // textareaを取得
        let textarea = document.querySelector('#prompt-textarea');

        // Shadow Rootにアクセス（textareaの中の）
        let shadowRoot = textarea.shadowRoot;

        // Shadow Rootからcontenteditableなdivを取得
        let contentEditableDiv = shadowRoot.querySelector('div[contenteditable=\\"plaintext-only\\"]');

        // テキストを入力
        contentEditableDiv.textContent = '{message}';

        // イベントを発火させて、ユーザーの操作をエミュレート
        let event = new Event('input', {{
            bubbles: true,
            cancelable: true,
        }});
        contentEditableDiv.dispatchEvent(event);
        """
        result = self.tab.do_javascript(script)
        print(result)
    def read_message(self) -> str:
        self.tab.do_javascript()

if __name__ == "__main__":
    gpt=SafariChatGPTClient()
    gpt.send_message("Hello, how are you?")



