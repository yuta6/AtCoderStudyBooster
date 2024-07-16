# Apple ScriptからSafariを操作することによってchatGPTを利用する.
"""
思考方法 :
chatGPTの会話のログ管理はすべてSafariのタブ上で行う.
つまりプログラムはログ管理を行わない. 
Safariのタブをプログラムは認識してそこからデータを取得する.
Safariのタブが閉じられたら, 自動でエラーになるようにする. というかインスタンスが削除されるようにする.
つまり, SafariのタブとPython上のConversationオブジェクトのインスタンスは対応している. 

"""
import time

from .operate_gpt import BaseChatGPTClient
from .safari_operator_by_applescript import SafariWindow


class SafariChatGPTClient(BaseChatGPTClient):
    def __init__(self) -> None :
        CHAT_GPT_URL = "https://chat.openai.com/chat?temporary-chat=true"
        self.window = SafariWindow()
        self.tab = self.window.create_new_tab(CHAT_GPT_URL)

    def send_message(self, message: str) -> None:
        script = f"""
        const textarea = document.getElementById('prompt-textarea');
        editableDiv.innerText = '{message}';
        """
        result = self.tab.do_javascript(script)
        print(result)
    def read_message(self) -> str:
        self.tab.do_javascript()

if __name__ == "__main__":
    gpt=SafariChatGPTClient()
    gpt.send_message("Hello, how are you?")


