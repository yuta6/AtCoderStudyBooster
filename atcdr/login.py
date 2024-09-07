import requests
from rich.console import Console
from rich.prompt import Prompt

from atcdr.util.parse import get_csrf_token
from atcdr.util.session import load_session, save_session, validate_session


def login() -> bool:
    ATCODER_LOGIN_URL = 'https://atcoder.jp/login'
    ATCODER_HOME_URL = 'https://atcoder.jp/home'

    console = Console()
    session = load_session()
    if validate_session(session):
        console.print('[green][+][/] すでにログイン済みです.  ')
        return True

    username = Prompt.ask('[cyan]ユーザー名を入力してください[/]', console=console)
    password = Prompt.ask('[cyan]パスワードを入力してください[/]', console=console)

    session = requests.Session()
    response = session.get(ATCODER_LOGIN_URL)

    login_data = {
        'username': username,  # ユーザー名を入力
        'password': password,  # パスワードを入力
        'csrf_token': get_csrf_token(response.text),  # 取得したCSRFトークンを使用
    }

    with console.status('ログイン中'):
        login_response = session.post(ATCODER_LOGIN_URL, data=login_data)

    # リクエスト後の最終URLを表示
    if login_response.url == ATCODER_HOME_URL and login_response.status_code == 200:
        console.print('[green][+][/] ログインに成功しました.  ')
        save_session(session)
        return True
    else:
        console.print('[red][-][/] ログインに失敗しました.  ')
        return False
