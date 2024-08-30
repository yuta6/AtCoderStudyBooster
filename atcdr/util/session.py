import json
import os
import re
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup as bs
from rich import print
from rich.align import Align
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


def print_rich_response(
    response: requests.Response, body_range: tuple = (0, 24)
) -> None:
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
                line_range=body_range,
            )
            if response.text
            else None
        )
    body_panel = Panel(body, title='レスポンスボディ') if body else None

    print(info_table)
    print(header_table)
    if body:
        print(body_panel)


def load_session() -> requests.Session:
    ATCODER_URL = 'https://atcoder.jp'
    cookie_file = os.path.join('~', 'cache', 'atcder', 'session.json')
    if not os.path.exists(cookie_file):
        return requests.Session()
    else:
        with open(cookie_file) as file:
            session = requests.Session()
            session.cookies.update(json.load(file))
        if validate_session(session):
            response = session.get(ATCODER_URL)
            username = get_username_from_html(response.text)
            if username:
                print(f'こんにちは！[cyan]{username}[/] さん')
            return session
        else:
            return requests.Session()


def save_session(session: requests.Session) -> None:
    if validate_session(session):
        cookie_file = os.path.join('~', 'cache', 'atcder', 'session.json')
        os.makedirs(os.path.dirname(cookie_file), exist_ok=True)
        with open(cookie_file, 'w') as file:
            json.dump(session.cookies.get_dict(), file)
    else:
        pass


def validate_session(session: requests.Session) -> bool:
    ATCODER_SETTINGS_URL = 'https://atcoder.jp/settings'
    try:
        response = session.get(
            ATCODER_SETTINGS_URL, allow_redirects=False
        )  # リダイレクトを追跡しない
        if response.status_code == 200:
            return True
        elif response.status_code in (301, 302) and 'Location' in response.headers:
            redirect_url = response.headers['Location']
            if 'login' in redirect_url:
                return False
        return False
    except requests.RequestException as e:
        print(f'[red][-][/] セッションチェック中にエラーが発生しました: {e}')
        return False


def get_username_from_html(html: str) -> str:
    soup = bs(html, 'html.parser')
    script_tags = soup.find_all('script')

    user_screen_name = ''
    for script in script_tags:
        # <script>タグに内容がある場合のみ処理を行う
        if script.string:
            # 正規表現でuserScreenNameの値を抽出
            match = re.search(r'userScreenName\s*=\s*"([^"]+)"', script.string)
            if match:
                user_screen_name = match.group(1)
                break  # 見つかったらループを抜ける

    return user_screen_name


def delete_session() -> None:
    cookie_file = os.path.join('~', 'cache', 'atcder', 'session.json')
    if os.path.exists(cookie_file):
        os.remove(cookie_file)
