import os
import re
import time
from typing import Dict, List, NamedTuple, Optional

import questionary as q
import requests
from bs4 import BeautifulSoup as bs
from rich import print
from rich.live import Live
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.status import Status

from atcdr.login import login
from atcdr.test import (
    ResultStatus,
    TestInformation,
    TestRunner,
    create_renderable_test_info,
)
from atcdr.util.execute import execute_files
from atcdr.util.filetype import (
    COMPILED_LANGUAGES,
    INTERPRETED_LANGUAGES,
    Lang,
    detect_language,
    lang2str,
    str2lang,
)
from atcdr.util.parse import ProblemHTML, get_csrf_token, get_submission_id
from atcdr.util.session import load_session, validate_session


class LanguageOption(NamedTuple):
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


def post_source(source_path: str, url: str, session: requests.Session) -> Optional[str]:
    with open(source_path, 'r') as file:
        source = file.read()

    problem = ProblemHTML(session.get(url).text)

    task_screen_name = problem.form.find_task_screen_name()
    submit_url = problem.form.find_submit_link()
    lang_dict = problem.form.get_languages_options()

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
        print(
            f'[red][Error{response.status_code}][/] サーバーエラーの関係で提出に失敗しました.'
        )
        return None

    if response.url == submit_url:  # リダイレクトが発生してないから提出失敗
        print(
            f'[red][Error{response.status_code}][/] 提出しましたが,受理されませんでした.'
        )
        return None

    submission_id = get_submission_id(response.text)
    print(f'[green][+][/green] 提出に成功しました！提出ID: {submission_id}')

    return response.url.replace('/me', f'/{submission_id}/status/json')


class SubmissionStatus(NamedTuple):
    status: ResultStatus
    current: Optional[int]
    total: Optional[int]
    is_finished: bool


def parse_submission_status_json(data: Dict) -> SubmissionStatus:
    html_content = data.get('Html', '')
    interval = data.get('Interval', None)

    soup = bs(html_content, 'html.parser')
    span = soup.find('span', {'class': 'label'})
    status_text = span.text.strip()

    current, total = None, None
    is_finished = interval is None

    match = re.search(r'(\d+)/(\d+)', status_text)
    if match:
        current = int(match.group(1))
        total = int(match.group(2))

    status_mapping = {
        'AC': ResultStatus.AC,
        'WA': ResultStatus.WA,
        'TLE': ResultStatus.TLE,
        'MLE': ResultStatus.MLE,
        'RE': ResultStatus.RE,
        'CE': ResultStatus.CE,
        'WJ': ResultStatus.WJ,
    }
    status = next(
        (status_mapping[key] for key in status_mapping if key in status_text),
        ResultStatus.WJ,
    )

    return SubmissionStatus(
        status=status, current=current, total=total, is_finished=is_finished
    )


def print_status_submission(
    api_url: str,
    path: str,
    session: requests.Session,
) -> None:
    progress = Progress(
        SpinnerColumn(style='white', spinner_name='circleHalves'),
        TextColumn('{task.description}'),
        SpinnerColumn(style='white', spinner_name='simpleDots'),
        BarColumn(),
    )

    with Status('ジャッジ待機中', spinner='dots'):
        for _ in range(10):
            time.sleep(1)
            data = session.get(api_url).json()
            status = parse_submission_status_json(data)
            if status.total or status.current:
                break
        else:
            print('[red][-][/]10秒待ってもジャッジが開始されませんでした')
            return

    total = status.total or 0
    task_id = progress.add_task(description='ジャッジ中', total=total)

    test_info = TestInformation(
        lang=detect_language(path),
        sourcename=path,
        case_number=total,
    )

    with Live(create_renderable_test_info(test_info, progress)) as live:
        current = 0
        while not status.is_finished:
            time.sleep(1)
            data = session.get(api_url).json()
            status = parse_submission_status_json(data)
            current = status.current or current or 0

            test_info.summary = status.status
            test_info.results = [ResultStatus.AC] * current

            progress.update(task_id, completed=current)
            live.update(create_renderable_test_info(test_info, progress))

        test_info.summary = status.status
        test_info.results = [ResultStatus.AC] * total

        progress.update(task_id, description='ジャッジ完了', completed=total)
        live.update(create_renderable_test_info(test_info, progress))


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
    list(test)
    print(create_renderable_test_info(test.info))

    if test.info.summary != ResultStatus.AC:
        print('[red][-][/] サンプルケースが AC していないので提出できません')
        return

    api_status_link = post_source(path, url, session)
    if api_status_link is None:
        return

    print_status_submission(api_status_link, path, session)


def submit(*args: str) -> None:
    execute_files(
        *args,
        func=submit_source,
        target_filetypes=COMPILED_LANGUAGES + INTERPRETED_LANGUAGES,
    )
