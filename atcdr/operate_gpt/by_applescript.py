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
from typing import List

class SafariChatGPTClient(BaseChatGPTClient):
    def __init__(self):
        self.windowID = self.start_conversation()
        pass

        
    def start_conversation(self) -> int:
        CHAT_GPT_URL = "https://chat.openai.com/chat?temporary-chat=true"

        script =f'''
        const safari = Application('Safari');

        // 新しいウィンドウを開く
        safari.make({{ new: "document" }});

        const windows = safari.windows;
        const newWindow = windows[windows.length - 1]; // 最後に追加されたウィンドウを取得

        delay(2); 
        newWindow.tabs[1].url = "{CHAT_GPT_URL}";

        console.log("新しいウィンドウのID: " + newWindow.id());

        newWindow.id()
        '''
        result = subprocess.run(['osascript', '-l', 'JavaScript', '-e', script], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        if result.returncode == 0:
            try:
                return result.stdout
            except ValueError:
                raise RuntimeError("Safariのウィンドウを取得できませんでした")
        else:
            print("STDERR:", result.stderr)
            raise RuntimeError("Safari経由でChatGPTにアクセスできません")

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

def execute_javascript_for_automation(script: str) -> str:


def open_window_of_safairi() -> int :
    pass


def create_tab_on_window(windowsID :int ) -> int:
    pass

def get_tabs_on_window(windowsID :int ) -> List[int]:
    pass 


# 　テスト
def main():
    SafariChatGPTClient()


if __name__ == "__main__":
    main()


