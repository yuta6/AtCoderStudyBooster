import re
import time
from pathlib import Path

import questionary as q
import rich_click as click
from rich import print
from rich.prompt import Prompt

from atcdr.util.filetype import FILE_EXTENSIONS, Lang
from atcdr.util.parse import ProblemHTML
from atcdr.util.problem import Contest, Problem
from atcdr.util.session import load_session


class Downloader:
    def __init__(self) -> None:
        self.session = load_session()

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


def save_problem(problem: Problem, base_path: Path = Path('.')) -> None:
    """1つの問題を保存"""
    downloader = Downloader()
    problem_content = downloader.get(problem)

    if not problem_content:
        print(f'[bold red][Error][/] {problem}の保存に失敗しました')
        return

    # ディレクトリ作成: コンテスト名/ラベル
    dir_path = base_path / problem.contest.name / problem.label
    dir_path.mkdir(parents=True, exist_ok=True)

    problem_content.repair_me()
    title = title_to_filename(problem_content.title or problem.label)

    # HTMLファイル保存
    html_path = dir_path / (title + FILE_EXTENSIONS[Lang.HTML])
    html_path.write_text(problem_content.html, encoding='utf-8')
    print(f'[bold green][+][/bold green] ファイルを保存しました: {html_path}')

    # Markdownファイル保存
    md = problem_content.make_problem_markdown('ja')
    md_path = dir_path / (title + FILE_EXTENSIONS[Lang.MARKDOWN])
    md_path.write_text(md, encoding='utf-8')
    print(f'[bold green][+][/bold green] ファイルを保存しました: {md_path}')


def interactive_download() -> None:
    session = load_session()

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
                save_problem(problem)
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
            save_problem(problem)
        except ValueError as e:
            print(f'[red][Error][/red] {e}')

    elif choice == END:
        print('[bold red]終了します[/]')
    else:
        print('[bold red]無効な選択です[/]')


@click.command(short_help='AtCoderの問題をダウンロード')
@click.argument('contest_name', required=False)
@click.argument('label', required=False)
def download(contest_name: str = None, label: str = None) -> None:
    """
    AtCoderの問題をダウンロードします

    使用例:
        download                # 対話形式
        download abc012        # abc012の全問題
        download abc012 A      # abc012のA問題のみ
    """
    if contest_name is None:
        interactive_download()
        return

    session = load_session()
    try:
        contest = Contest(contest_name, session)

        if label is None:
            for problem in contest.problems:
                save_problem(problem)
        else:
            # 指定されたラベルの問題のみ
            label = label.upper()
            found = False
            for problem in contest.problems:
                if problem.label == label:
                    save_problem(problem)
                    found = True
                    break
            if not found:
                print(f'[red][Error][/red] 問題 {label} が見つかりません')

    except ValueError as e:
        print(f'[red][Error][/red] {e}')
