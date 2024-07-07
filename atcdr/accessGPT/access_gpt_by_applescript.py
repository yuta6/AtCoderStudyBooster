import subprocess
import time




# Safariで指定のページを開くAppleScript
open_page_script = """
tell application "Safari"
    activate
    open location "https://chatgpt.com"
end tell
"""

# AppleScriptを実行してSafariでページを開く
subprocess.Popen(['osascript', '-e', open_page_script])

# ページのロードを待機
time.sleep(10)

# 指定された要素に文字を入力するJavaScriptを実行するAppleScript
input_text_script = """
tell application "Safari"
    do JavaScript "document.querySelector('textarea#prompt-textarea').value = 'Your input text here';" in document 1
end tell
"""

# AppleScriptを実行して文字を入力
subprocess.Popen(['osascript', '-e', input_text_script])



