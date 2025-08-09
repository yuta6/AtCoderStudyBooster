import rich_click as click
import webview
from rich import print

from atcdr.util.i18n import _
from atcdr.util.session import delete_session, load_session, validate_session

ATCODER_LOGIN_URL = 'https://atcoder.jp/login'


@click.command(short_help=_('cmd_logout'), help=_('cmd_logout'))
def logout() -> None:
    """AtCoderからログアウトします."""
    session = load_session()
    if not validate_session(session):
        print('[red][-][/] ' + _('not_logged_in'))
        return

    delete_session()
    print('[green][+][/] ' + _('logout_success'))

    window = webview.create_window('AtCoder Logout', ATCODER_LOGIN_URL, hidden=True)

    def on_start():
        window.clear_cookies()
        window.destroy()

    webview.start(on_start, private_mode=False)
