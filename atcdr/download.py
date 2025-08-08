import re
import time
from itertools import groupby, product
from pathlib import Path
from typing import List, Tuple, Union, cast

import questionary as q
import requests
import rich_click as click
from rich import print
from rich.prompt import Prompt

from atcdr.util.filetype import FILE_EXTENSIONS, Lang
from atcdr.util.parse import ProblemHTML
from atcdr.util.problem import Contest, Problem
from atcdr.util.session import load_session


class Downloader:
    def __init__(self, session: requests.Session) -> None:
        self.session = session

    def get(self, problem: Problem) -> ProblemHTML:
        session = self.session
        retry_attempts = 3
        retry_wait = 1  # 1 second

        for _ in range(retry_attempts):
            response = session.get(problem.url)
            if response.status_code == 200:
                return ProblemHTML(response.text)
            elif response.status_code == 429:
                print(
                    f'[bold yellow][Error {response.status_code}][/bold yellow] 再試行します。{problem}'
                )
                time.sleep(retry_wait)
            elif 300 <= response.status_code < 400:
                print(
                    f'[bold yellow][Error {response.status_code}][/bold yellow] リダイレクトが発生しました。{problem}'
                )
            elif 400 <= response.status_code < 500:
                print(
                    f'[bold red][Error {response.status_code}][/bold red] 問題が見つかりません。{problem}'
                )
                break
            elif 500 <= response.status_code < 600:
                print(
                    f'[bold red][Error {response.status_code}][/bold red] サーバーエラーが発生しました。{problem}'
                )
                break
            else:
                print(
                    f'[bold red][Error {response.status_code}][/bold red] {problem}に対応するHTMLファイルを取得できませんでした。'
                )
                break
        return ProblemHTML('')


def title_to_filename(title: str) -> str:
    title = re.sub(r'[\\/*?:"<>| !@#$%^&()+=\[\]{};,\']', '', title)
    title = re.sub(r'.*?-', '', title)
    return title


def save_problem(problem: Problem, path: Path, session: requests.Session) -> None:
    """1つの問題を保存"""
    downloader = Downloader(session)
    problem_content = downloader.get(problem)

    if not problem_content:
        print(f'[bold red][Error][/] {problem}の保存に失敗しました')
        return

    # ディレクトリ作成（pathをそのまま使用）
    path.mkdir(parents=True, exist_ok=True)

    problem_content.repair_me()
    title = title_to_filename(problem_content.title or problem.label)

    # HTMLファイル保存
    html_path = path / (title + FILE_EXTENSIONS[Lang.HTML])
    html_path.write_text(problem_content.html, encoding='utf-8')
    print(f'[bold green][+][/bold green] ファイルを保存しました: {html_path}')

    # Markdownファイル保存
    md = problem_content.make_problem_markdown('ja')
    md_path = path / (title + FILE_EXTENSIONS[Lang.MARKDOWN])
    md_path.write_text(md, encoding='utf-8')
    print(f'[bold green][+][/bold green] ファイルを保存しました: {md_path}')


def interactive_download(session) -> None:
    CONTEST = '1. コンテストの問題を解きたい'
    ONE_FILE = '2. 1問だけダウンロードする'
    END = '3. 終了する'

    choice = q.select(
        message='AtCoderの問題のHTMLファイルをダウンロードします',
        qmark='',
        pointer='❯❯❯',
        choices=[CONTEST, ONE_FILE, END],
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

    if choice == CONTEST:
        name = Prompt.ask('コンテスト名を入力してください (例: abc012, abs, typical90)')
        try:
            contest = Contest(name, session)
            for problem in contest.problems:
                save_problem(problem, Path(contest.name) / problem.label, session)
        except ValueError as e:
            print(f'[red][Error][/red] {e}')

    elif choice == ONE_FILE:
        name = Prompt.ask('コンテスト名を入力してください (例: abc012, abs, typical90)')
        try:
            contest = Contest(name, session)
            problem = q.select(
                message='どの問題をダウンロードしますか?',
                qmark='',
                pointer='❯❯❯',
                choices=[
                    q.Choice(title=f'{p.label:10} | {p.url}', value=p)
                    for p in contest.problems
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
            save_problem(problem, Path(contest.name) / problem.label, session)
        except ValueError as e:
            print(f'[red][Error][/red] {e}')

    elif choice == END:
        print('[bold red]終了します[/]')
    else:
        print('[bold red]無効な選択です[/]')


def plan_download(
    args: List[str], session: requests.Session
) -> List[Tuple[Problem, Path]]:
    def classify(arg):
        try:
            return Contest(arg, session)
        except ValueError:
            label = arg
            return label

    parsed: List[Union['Contest', str]] = list(map(classify, args))

    groups: List[List[Union['Contest', str]]] = [
        list(group)
        for _, group in groupby(parsed, key=lambda x: isinstance(x, Contest))
    ]

    if len(groups) == 1:
        if all(isinstance(x, Contest) for x in groups[0]):
            contests = cast(List[Contest], groups[0])
            return [
                (problem, Path(contest.name) / problem.label)
                for contest in contests
                for problem in contest.problems
            ]
        else:
            raise ValueError('コンテスト名を指定してください')
    elif len(groups) == 2:
        result = []
        for i, j in product(groups[0], groups[1]):
            if isinstance(i, Contest) and isinstance(j, str):
                # Contest × Label
                for problem in i.problems:
                    if problem.label == j:
                        result.append((problem, Path(i.name) / j))
            elif isinstance(i, str) and isinstance(j, Contest):
                # Label × Contest
                for problem in j.problems:
                    if problem.label == i:
                        result.append((problem, Path(i) / j.name))
        return result
    else:
        raise ValueError('ダウンロードの引数が正しくありません')


@click.command(short_help='AtCoder の問題をダウンロード')
@click.argument('args', nargs=-1)
def download(args: List[str]) -> None:
    """
    例:
        download abc{001..012} {A..C}
        download {A..E} abc{001..012}
    """
    session = load_session()

    if not args:
        interactive_download(session)
        return

    try:
        plan = plan_download(args, session)
    except ValueError as e:
        print(f'[red][Error][/red] {e}')
        return

    for prob, path in plan:
        save_problem(prob, path, session)
