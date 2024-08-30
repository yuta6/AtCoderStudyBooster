from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup as bs
from rich import print
from rich.align import Align
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


def print_response(response: requests.Response) -> None:
    # レスポンス情報をテーブル形式で表示
    info_table = Table(title='レスポンス情報')
    info_table.add_column('項目', justify='left', style='cyan', no_wrap=True)
    info_table.add_column('内容', justify='left', style='magenta')
    info_table.add_row('URL', response.url)
    info_table.add_row('ステータスコード', str(response.status_code))
    info_table.add_row('理由', response.reason)
    info_table = Align.center(info_table)

    # ヘッダー情報をテーブル形式で表示
    header_table = Table(title='レスポンスヘッダー')
    header_table.add_column('キー', style='cyan', no_wrap=True)
    header_table.add_column('値', style='magenta', overflow='fold')
    for key, value in response.headers.items():
        value = unquote(value)
        header_table.add_row(key, value)
    header_table = Align.center(header_table)

    # レスポンスボディの表示
    content_type = response.headers.get('Content-Type', '').lower()
    if 'application/json' in content_type:
        # JSONの整形表示
        try:
            body = Syntax(response.json(), 'json', theme='monokai', line_numbers=True)
        except Exception:
            pass
    else:
        # HTMLやその他のコンテンツの整形表示
        body = (
            Syntax(
                response.text,
                'html' if 'html' in content_type else 'text',
                theme='monokai',
                line_numbers=True,
                line_range=(0, 24),
            )
            if response.text
            else None
        )
    body_panel = Panel(body, title='レスポンスボディ') if body else None

    print(info_table)
    print(header_table)
    if body:
        print(body_panel)


def login() -> requests.Session:
    session = requests.Session()

    ATCODER_LOGIN_URL = 'https://atcoder.jp/login'
    ATCODER_HOME_URL = 'https://atcoder.jp/home'

    response = session.get(ATCODER_LOGIN_URL)

    soup = bs(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    login_data = {
        'username': 'YutaY9',  # ユーザー名を入力
        'password': '',  # パスワードを入力
        'csrf_token': csrf_token,  # 取得したCSRFトークンを使用
    }

    login_response = session.post(ATCODER_LOGIN_URL, data=login_data)
    if login_response.history:
        for resp in login_response.history:
            print_response(resp)

    print_response(login_response)

    # リクエスト後の最終URLを表示
    if login_response.url == ATCODER_HOME_URL and login_response.status_code == 200:
        print('[green][+][/] ログインに成功しました.  ')
        return session
    else:
        print('[green][-][/] ログインに失敗しました.  ')
        return session


login()
