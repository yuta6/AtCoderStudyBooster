import json
import os
from urllib.parse import unquote

import requests
from rich import print
from rich.align import Align
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from atcdr.util.parse import get_username_from_html

COOKIE_PATH = os.path.join(os.path.expanduser('~'), '.cache', 'atcdr', 'session.json')


# デバック用のレスポンス解析用関数
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

    # リダイレクトの歴史
    redirect_table = None
    if response.history:
        redirect_table = Table(title='リダイレクト履歴')
        redirect_table.add_column('ステップ', style='cyan')
        redirect_table.add_column('ステータスコード', style='magenta')
        redirect_table.add_column('URL', style='green')
        for i, redirect_response in enumerate(response.history):
            redirect_table.add_row(
                f'Redirect {i}',
                str(redirect_response.status_code),
                redirect_response.url,
            )
        redirect_table = Align.center(redirect_table)

    # レスポンスボディの表示
    content_type = response.headers.get('Content-Type', '').lower()
    if 'application/json' in content_type:
        # JSONの整形表示
        try:
            body = Syntax(
                json.dumps(response.json(), indent=4),
                'json',
                theme='monokai',
                line_numbers=True,
                line_range=body_range,
                word_wrap=True,
            )
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
                word_wrap=True,
            )
            if response.text
            else None
        )
    body_panel = Panel(body, title='レスポンスボディ') if body else None

    print(info_table)
    print(header_table)
    if redirect_table:
        print(redirect_table)
    if body:
        print(body_panel)


def load_session() -> requests.Session:
    ATCODER_URL = 'https://atcoder.jp'
    if not os.path.exists(COOKIE_PATH):
        return requests.Session()
    else:
        with open(COOKIE_PATH) as file:
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
        os.makedirs(os.path.dirname(COOKIE_PATH), exist_ok=True)
        with open(COOKIE_PATH, 'w') as file:
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


def delete_session() -> None:
    if os.path.exists(COOKIE_PATH):
        os.remove(COOKIE_PATH)
