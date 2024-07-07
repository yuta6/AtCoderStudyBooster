# Apple ScriptからSafariを操作することによってchatGPTを利用する.
"""
思考方法 :
chatGPTの会話のログ管理はすべてSafariのタブ上で行う.
つまりプログラムはログ管理を行わない. 
Safariのタブをプログラムは認識してそこからデータを取得する.
Safariのタブが閉じられたら, 自動でエラーになるようにする. というかインスタンスが削除されるようにする.
つまり, SafariのタブとPython上のConversationオブジェクトのインスタンスは対応している. 

"""

from abc import ABC, abstractmethod

class BaseChatGPTClient(ABC):
    @abstractmethod
    def send_message(self, message: str) -> None:
        pass

    @abstractmethod
    def read_message(self) -> str:
        pass



import subprocess

class Conversation:
    def __init__(self):
        self.tabID = self.start_conversation()
        
    def start_conversation(self) -> int:
        # AppleScriptを使ってSafariを起動し、新しいタブを開いてChatGPTにアクセスする
        script = '''
        set chatGPTURL to "https://chat.openai.com/chat?temporary-chat=true"
        tell application "Safari"
            activate
            tell window 1
                set currentTab to make new tab with properties {URL:chatGPTURL}
            end tell
            set currentTabID to id of currentTab
        end tell
        return currentTabID
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.strip())
        else:
            raise RuntimeError("Failed to start conversation in Safari")

    def send_message(self, message: str) -> None:
        # AppleScriptを使ってSafariの指定したタブにメッセージを送信する
        script = f'''
        tell application "Safari"
            do JavaScript "document.querySelector('textarea').value = '{message}'; document.querySelector('button[type=submit]').click();" in tab id {self.tabID} of window 1
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script])
        if result.returncode != 0:
            raise RuntimeError("Failed to send message")

    def read_message(self) -> str:
        # AppleScriptを使ってSafariの指定したタブからメッセージを読み取る
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

# 使用例
try:
    conversation = Conversation()
    conversation.send_message("Hello, how are you?")
    response = conversation.read_message()
    print(response)
except Exception as e:
    print(f"Error: {e}")

