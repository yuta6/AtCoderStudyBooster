from rich import print

from atcdr.util.session import delete_session, load_session, validate_session


def logout() -> None:
    session = load_session()
    if not validate_session(session):
        print('[red][-][/] ログインしていません.  ')
        return
    else:
        delete_session()
        print('[green][+][/] ログアウトしました.  ')
