# Apple ScriptからSafariを操作することによってchatGPTを利用する.
"""
思考方法 :
chatGPTの会話のログ管理はすべてSafariのタブ上で行う.
つまりプログラムはログ管理を行わない. 
Safariのタブをプログラムは認識してそこからデータを取得する.
Safariのタブが閉じられたら, 自動でエラーになるようにする. というかインスタンスが削除されるようにする.
つまり, SafariのタブとPython上のConversationオブジェクトのインスタンスは対応している. 

"""
import subprocess
from .base import BaseChatGPTClient

class SafariChatGPTClient(BaseChatGPTClient):
    def __init__(self):
        self.tabID = self.start_conversation()
        
    def start_conversation(self) -> int:
        CHAT_GPT_URL = "https://chat.openai.com/chat?temporary-chat=true"
        script = f'''
        tell application "Safari"
            activate
            tell window 1
                set currentTab to make new tab with properties {CHAT_GPT_URL}
            end tell
            set currentTabID to id of currentTab
        end tell
        return currentTabID
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        print(result)
        if result.returncode == 0:
            return int(result.stdout.strip())
        else:
            raise RuntimeError("Safari経由でchat GPTにアクセスできません")

    def send_message(self, message: str) -> None:
        script = f'''
        tell application "Safari"
            do JavaScript "document.querySelector('textarea').value = '{message}'; document.querySelector('button[type=submit]').click();" in tab id {self.tabID} of window 1
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script])
        if result.returncode != 0:
            raise RuntimeError("Failed to send message")

    def read_message(self) -> str:
        script = f'''
        tell application "Safari"
            set responseText to do JavaScript "document.querySelector('.response-class').innerText;" in tab id {self.tabID} of window 1
        end tell
        return responseText
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            raise RuntimeError("Failed to read message")

# 　テスト
def main():
    SafariChatGPTClient().start_conversation()


if __name__ == "__main__":
    main()


