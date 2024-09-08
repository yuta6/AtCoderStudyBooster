import os
from dataclasses import dataclass
from typing import Dict, List

import questionary as q
import requests
from rich import print

from atcdr.login import login
from atcdr.test import ResultStatus, TestRunner, render_results
from atcdr.util.execute import execute_files
from atcdr.util.filetype import (
    COMPILED_LANGUAGES,
    INTERPRETED_LANGUAGES,
    Lang,
    detect_language,
    lang2str,
    str2lang,
)
from atcdr.util.parse import ProblemHTML, get_csrf_token
from atcdr.util.session import load_session, validate_session


@dataclass
class LanguageOption:
    id: int
    display_name: str
    lang: Lang


def convert_options_to_langs(options: Dict[str, int]) -> List[LanguageOption]:
    lang_options = []
    for display_name, id_value in options.items():
        lang_name = display_name.split()[
            0
        ].lower()  # 例えば,C++ 23 (Clang 16.0.6)から「c++」を取り出す
        try:
            lang = str2lang(lang_name)
        except KeyError:
            continue
        lang_options.append(
            LanguageOption(id=id_value, display_name=display_name, lang=lang)
        )

    return lang_options


def choose_langid_interactively(lang_dict: dict, lang: Lang) -> int:
    options = convert_options_to_langs(lang_dict)
    options = [*filter(lambda option: option.lang == lang, options)]

    langid = q.select(
        message=f'以下の一覧から{lang2str(lang)}の実装/コンパイラーを選択してください',
        qmark='',
        pointer='❯❯❯',
        choices=[
            q.Choice(title=f'{option.display_name}', value=option.id)
            for option in options
        ],
        instruction='\n 十字キーで移動,[enter]で実行',
        style=q.Style(
            [
                ('question', 'fg:#2196F3 bold'),
                ('answer', 'fg:#FFB300 bold'),
                ('pointer', 'fg:#FFB300 bold'),
                ('highlighted', 'fg:#FFB300 bold'),
                ('selected', 'fg:#FFB300 bold'),
            ]
        ),
    ).ask()

    return langid


def post_source(
    source_path: str, url: str, session: requests.Session
) -> requests.Response:
    with open(source_path, 'r') as file:
        source = file.read()

    problem = ProblemHTML(session.get(url).text)

    task_screen_name = problem.find_task_screen_name_from_form()
    submit_url = problem.find_submit_link_from_form()
    lang_dict = problem.get_languages_options_from_form()

    csrf_token = get_csrf_token(problem.html)

    lang = detect_language(source_path)
    langid = choose_langid_interactively(lang_dict, lang)

    post_data = {
        'data.LanguageId': str(langid),
        'data.TaskScreenName': task_screen_name,
        'sourceCode': source,
        'csrf_token': csrf_token,
    }

    response = session.post(submit_url, data=post_data)
    if response.status_code != 200:
        print(f'[red][Error{response.status_code}][/] 提出に失敗しました.')
        print(response.text)

    return response


def submit_source(path: str) -> None:
    session = load_session()
    if not validate_session(session):
        print('[red][-][/] ログインしていません.')
        login()
        if not validate_session(session):
            print('[red][-][/] ログインに失敗しました.')
            return

    html_files = [file for file in os.listdir('.') if file.endswith('.html')]
    if not html_files:
        print(
            '問題のファイルが見つかりません \n問題のファイルが存在するディレクトリーに移動してから実行してください'
        )
        return

    with open(html_files[0], 'r') as file:
        problem = ProblemHTML(file.read())

    lcases = problem.load_labeled_testcase()
    url = problem.link
    test = TestRunner(path, lcases)
    render_results(test)

    if test.info.results_summary != ResultStatus.AC:
        print('[red][-][/]サンプルケースが AC していないので提出できません')
        return

    post_source(path, url, session)


def submit(*args: str) -> None:
    execute_files(
        *args,
        func=submit_source,
        target_filetypes=COMPILED_LANGUAGES + INTERPRETED_LANGUAGES,
    )
