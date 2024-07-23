import subprocess
import uuid


def execute_javascript_for_automation(script: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode == 0:
        return result
    else:
        raise RuntimeError("AppleScript Error: " + result.stderr)


class SafariTab:

    def _get_tab_info(self, id: str):
        script = f"""
        tell application "Safari"
            set win to (first window whose id is {id})
            set tab to (first tab of win)
            set URL of tab to "about:blank"
        end tell
        """
        execute_javascript_for_automation(script)
        self.index
        self.name
        self.url
        self.visible
        self.source
        self.text
        pass

    def __init__(self) -> None:
        self.id = None

    def do_javascript(self, script: str) -> str:
        applescript = f"""
        tell application "Safari"
            set targetTab to missing value
            repeat with w in every window
                repeat with t in every tab of w
                    try
                        set tabId to (do JavaScript "sessionStorage.getItem('safariTabIdentifier') || '';" in t)
                        if tabId is "{self.id}" then
                            set targetTab to t
                            exit repeat
                        end if
                    on error
                        -- エラーが発生した場合は何もせず次のタブに進む
                    end try
                end repeat
                if targetTab is not missing value then
                    exit repeat
                end if
            end repeat

            if targetTab is missing value then
                return "Error: Tab not found"
            else
                return (do JavaScript "{script}" in targetTab)
            end if
        end tell
        """

        result = execute_javascript_for_automation(applescript)

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            raise RuntimeError(f"JavaScript execution failed: {result.stderr}")

    def close(self) -> None:
        pass

    def reload(self) -> None:
        pass

    def go_back(self) -> None:
        pass

    def go_forward(self) -> None:
        pass

    def set_url(self, url: str) -> None:
        pass

    # 取得したWindow IDに基づいた処理を行う.


class SafariWindow:

    def __init__(self) -> None:
        script = """
        tell application "Safari"
            set windowCount to count of windows
            make new document
            set newWindow to window (windowCount + 1)
            set index of newWindow to 1
            return id of newWindow
        end tell
        """
        result = execute_javascript_for_automation(script)
        self.id = int(result.stdout.strip())
        print(f"Window ID: {self.id}")
        self.tabs = []

    def _give_tabid_to_tabs(self) -> None:
        script = f"""
        tell application "Safari"
            set win to (first window whose id is {self.id})
            set tabs to (every tab of win)
        end tell
        """
        pass

    def _update_tabs(self) -> None:
        script = f"""
        tell application "Safari"
            set win to (first window whose id is {self.id})
            set tabs to (every tab of win)
        end tell
        """
        pass

    def create_new_tab(self, url: str | None = None) -> SafariTab:
        print(f"新規タブを{self.id}ウィンドウに作成し、{url}のサイトにアクセスします")
        tab_id = str(uuid.uuid4())
        if url is None:
            url = "about:blank"

        script = f"""
        tell application "Safari"
            set targetWindow to missing value
            repeat with w in every window
                if (id of w) is {self.id} then
                    set targetWindow to w
                    exit repeat
                end if
            end repeat

            if targetWindow is missing value then
                return "Error: Window not found"
            else
                tell targetWindow
                    set newTab to make new tab at end
                    set current tab to newTab
                    set URL of newTab to "{url}"
                    delay 1
                    do JavaScript "sessionStorage.setItem('safariTabIdentifier', '{tab_id}');" in newTab
                end tell
            end if
        end tell
        """
        result = execute_javascript_for_automation(script)

        if "Error:" in result.stdout:
            raise RuntimeError(result.stdout)

        new_tab = SafariTab()
        new_tab.id = tab_id
        self.tabs.append(new_tab)
        return new_tab

    def find_tab_from_id(self):
        pass
