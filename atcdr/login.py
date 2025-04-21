import threading
import time

import rich_click as click
import webview
from requests import Session
from rich.console import Console

from atcdr.util.session import load_session, save_session, validate_session

ATCODER_LOGIN_URL = 'https://atcoder.jp/login'
ATCODER_HOME_URL = 'https://atcoder.jp/home'

console = Console()


@click.command(short_help='AtCoderへログイン')
def login() -> None:
    """AtCoderへログインします."""
    session = load_session()
    if validate_session(session):
        console.print('[green][+][/] すでにログインしています. ')
        return

    # Prompt in CLI
    username = console.input('[cyan]ユーザー名: [/]').strip()
    password = console.input('[cyan]パスワード: [/]').strip()

    window = webview.create_window('AtCoder Login', ATCODER_LOGIN_URL, hidden=False)

    def on_start():
        js_fill = f"""
        document.getElementById('username').value = '{username}';
        document.getElementById('password').value = '{password}';
        """
        window.evaluate_js(js_fill)

        def poll_and_submit():
            with console.status(
                'キャプチャー認証を解決してください', spinner='circleHalves'
            ):
                while True:
                    try:
                        token = window.evaluate_js(
                            'document.querySelector(\'input[name=\\"cf-turnstile-response\\"]\').value'
                        )
                        if token:
                            console.print('[green][+][/] ログインします')
                            window.evaluate_js(
                                "document.getElementById('submit').click();"
                            )
                            break
                    except Exception:
                        pass

                    time.sleep(0.5)

            with console.status('ログインの結果の待機中...', spinner='circleHalves'):
                while True:
                    try:
                        current_url = window.get_current_url()
                    except Exception:
                        current_url = None

                    if current_url and current_url.startswith(ATCODER_HOME_URL):
                        console.print('[green][+][/] ログイン成功!')

                        session = Session()
                        session = move_cookies_from_webview_to_session(window, session)
                        save_session(session)
                        window.destroy()
                        break

                    try:
                        err = window.evaluate_js(
                            'Array.from(document.querySelectorAll('
                            '\'div.alert.alert-danger[role="alert"]\'))'
                            ".map(e=>e.textContent.trim()).filter(t=>t).join(' ')"
                        )
                        err = err.replace('\n', '').replace('\r', '').replace('\t', '')
                    except Exception:
                        err = ''

                    if err:
                        console.print(f'[red][-][/] エラー: {err}')
                        session = Session()
                        session = move_cookies_from_webview_to_session(window, session)
                        save_session(session)
                        window.destroy()
                        return

                    time.sleep(0.5)

        t = threading.Thread(target=poll_and_submit, daemon=True)
        t.start()

    webview.start(on_start, private_mode=False)


def move_cookies_from_webview_to_session(
    window: webview.Window, session: Session
) -> Session:
    cookie_list = window.get_cookies()
    for cookie_obj in cookie_list:
        for cookie_name, morsel in cookie_obj.items():
            # morselからデータを取得
            value = morsel.value

            domain = morsel.get('domain')
            if domain is None:
                domain = '.atcoder.jp'

            path = morsel.get('path', '/')
            secure = 'secure' in morsel

            expires = None  # __NSTaggedDateオブジェクトを回避

            http_only = 'httponly' in morsel

            # HttpOnlyをrestに含める
            rest = {}
            if http_only:
                rest['HttpOnly'] = True

            # セッションにクッキーを設定
            session.cookies.set(
                name=cookie_name,
                value=value,
                domain=domain,
                path=path,
                secure=secure,
                expires=expires,  # Noneを渡す
                rest=rest,
            )

    return session
