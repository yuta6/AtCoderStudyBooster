from rich import print

from atcdr.util.session import delete_session


def logout() -> None:
    delete_session()
    print('[green][+][/] ログアウトしました.  ')
