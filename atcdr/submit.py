import os

import requests

from atcdr.test import create_testcases_from_html, judge_code_from
from atcdr.util.execute import execute_files
from atcdr.util.filetype import (
    COMPILED_LANGUAGES,
    INTERPRETED_LANGUAGES,
    Lang,
    detect_language,
)
from atcdr.util.parse import find_link_from_html
from atcdr.util.session import load_session


def post_source(source_path: str, task_url: str, session: requests.Session) -> None:
    lang = detect_language(source_path)
    print(f'{lang}')
    pass


def submit_source(path: str) -> None:
    session = load_session()

    html_files = [
        file
        for file in os.listdir('.')
        if os.path.isfile(file) and os.path.splitext(file)[1] in [Lang.HTML]
    ]
    if not html_files:
        print(
            '問題のファイルが見つかりません。\n問題のファイルが存在するディレクトリーに移動してから実行してください。'
        )
        return

    with open(html_files[0], 'r') as file:
        html = file.read()

    ltestcases = create_testcases_from_html(html)
    results = judge_code_from(ltestcases, path)

    print(results)

    task_url = find_link_from_html(html)
    if not task_url:
        print('URLを見つけられません。')
        return

    post_source(path, task_url, session)


def submit(*args: str) -> None:
    execute_files(
        *args,
        func=submit_source,
        target_filetypes=COMPILED_LANGUAGES + INTERPRETED_LANGUAGES,
    )
