import os
import re
import time
from typing import Callable, List, Union, cast

import questionary as q
import rich_click as click
from rich import print
from rich.prompt import Prompt

from atcdr.util.filetype import FILE_EXTENSIONS, Lang
from atcdr.util.parse import ProblemHTML
from atcdr.util.problem import Contest, Diff, Problem
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


def mkdir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f'[bold green][+][/bold green] フォルダー: {path} を作成しました')


class GenerateMode:
    @staticmethod
    def gene_path_on_diff(base: str, problem: Problem) -> str:
        return (
            os.path.join(base, problem.label, f'{problem.contest.number:03}')
            if problem.contest.number
            else os.path.join(base, problem.label, problem.contest.contest)
        )

    @staticmethod
    def gene_path_on_num(base: str, problem: Problem) -> str:
        return (
            os.path.join(base, f'{problem.contest.number:03}', problem.label)
            if problem.contest.number
            else os.path.join(base, problem.contest.contest, problem.label)
        )


def title_to_filename(title: str) -> str:
    title = re.sub(r'[\\/*?:"<>| !@#$%^&()+=\[\]{};,\']', '', title)
    title = re.sub(r'.*?-', '', title)
    return title


def generate_problem_directory(
    base_path: str, problems: List[Problem], gene_path: Callable[[str, Problem], str]
) -> None:
    downloader = Downloader()
    for problem in problems:
        problem_content = downloader.get(problem)
        if not problem_content:
            print(f'[bold red][Error][/] {problem}の保存に失敗しました')
            continue

        dir_path = gene_path(base_path, problem)
        mkdir(dir_path)

        problem_content.repair_me()

        title = problem_content.title or problem.label
        title = title_to_filename(title)

        html_path = os.path.join(dir_path, title + FILE_EXTENSIONS[Lang.HTML])
        with open(html_path, 'w', encoding='utf-8') as file:
            file.write(problem_content.html)
        print(f'[bold green][+][/bold green] ファイルを保存しました :{html_path}')

        md = problem_content.make_problem_markdown('ja')
        md_path = os.path.join(dir_path, title + FILE_EXTENSIONS[Lang.MARKDOWN])
        with open(md_path, 'w', encoding='utf-8') as file:
            file.write(md)
        print(f'[bold green][+][/bold green] ファイルを保存しました :{md_path}')


def parse_range(match: re.Match) -> List[int]:
    start, end = map(int, match.groups())
    start, end = min(start, end), max(start, end)
    return list(range(start, end + 1))


def parse_diff_range(match: re.Match) -> List[Diff]:
    start, end = match.groups()
    start_index = min(ord(start.upper()), ord(end.upper()))
    end_index = max(ord(start.upper()), ord(end.upper()))
    return [Diff(chr(i)) for i in range(start_index, end_index + 1)]


def convert_arg(arg: str) -> Union[List[int], List[Diff]]:
    if arg.isdigit():
        return [int(arg)]
    elif arg.isalpha() and len(arg) == 1:
        return [Diff(arg)]
    elif match := re.match(r'^(\d+)\.\.(\d+)$', arg):
        return parse_range(match)
    elif match := re.match(r'^([A-Z])\.\.([A-Z])$', arg, re.IGNORECASE):
        return parse_diff_range(match)
    else:
        raise ValueError(f'{arg}は認識できません')


def are_all_integers(args: Union[List[int], List[Diff]]) -> bool:
    return all(isinstance(arg, int) for arg in args)


def are_all_diffs(args: Union[List[int], List[Diff]]) -> bool:
    return all(isinstance(arg, Diff) for arg in args)


def interactive_download() -> None:
    CONTEST = '1. コンテストの問題を解きたい'
    PRACTICE = '2. 特定の難易度の問題を集中的に練習したい'
    ONE_FILE = '3. 1問だけダウンロードする'
    END = '4. 終了する'

    choice = q.select(
        message='AtCoderの問題のHTMLファイルをダウンロードします',
        qmark='',
        pointer='❯❯❯',
        choices=[CONTEST, PRACTICE, ONE_FILE, END],
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
        name = Prompt.ask(
            'コンテスト名を入力してください (例: abc012, abs, typical90)',
        )

        problems = Contest(name=name).problems(session=load_session())
        if not problems:
            print(f'[red][Error][/red] コンテスト名が間違っています: {name}')
            return

        generate_problem_directory('.', problems, GenerateMode.gene_path_on_num)

    elif choice == PRACTICE:
        difficulty = Prompt.ask(
            '難易度を入力してください (例: A)',
        )
        try:
            difficulty = Diff(difficulty)
        except KeyError:
            raise ValueError('入力された難易度が認識できません')
        number_str = Prompt.ask(
            'コンテスト番号または範囲を入力してください (例: 120..130)'
        )
        if number_str.isdigit():
            contest_numbers = [int(number_str)]
        elif match := re.match(r'^\d+\.\.\d+$', number_str):
            contest_numbers = parse_range(match)
        else:
            raise ValueError('数字の範囲の形式が間違っています')

        problems = [
            Problem(contest=Contest('abc', number), difficulty=difficulty)
            for number in contest_numbers
        ]

        generate_problem_directory('.', problems, GenerateMode.gene_path_on_diff)

    elif choice == ONE_FILE:
        name = Prompt.ask(
            'コンテスト名を入力してください (例: abc012, abs, typical90)',
        )

        problems = Contest(name=name).problems(session=load_session())

        problem = q.select(
            message='どの問題をダウンロードしますか?',
            qmark='',
            pointer='❯❯❯',
            choices=[
                q.Choice(title=f'{problem.label:10} | {problem.url}', value=problem)
                for problem in problems
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

        generate_problem_directory('.', [problem], GenerateMode.gene_path_on_num)

    elif choice == END:
        print('[bold red]終了します[/]')
    else:
        print('[bold red]無効な選択です[/]')


@click.command(short_help='AtCoderの問題をダウンロード')
@click.argument('first', nargs=1, type=str, required=False)
@click.argument('second', nargs=1, type=str, required=False)
def download(
    first: Union[str, None] = None,
    second: Union[str, None] = None,
    base_path: str = '.',
) -> None:
    """
    AtCoderの問題をダウンロードします

    download
    対話形式でダウンロードを開始します。

    download abc012
        コンテスト abc012 の全問題をダウンロード

    download A 120
        難易度Aの120番問題をダウンロード

    download 120..130 B
        ABCの120～130番のB問題をダウンロード

    download 120
        ABCの120番問題をダウンロード
    """
    if first is None:
        interactive_download()
        return

    if second is None:
        try:
            first_args = convert_arg(str(first))
        except ValueError:
            first = str(first)
            problems = Contest(name=first).problems(session=load_session())
            if not problems:
                print(f'[red][Error][red/] コンテスト名が間違っています: {first}')
                return
            generate_problem_directory('.', problems, GenerateMode.gene_path_on_num)
            return

        if are_all_diffs(first_args):
            raise ValueError(
                """難易度だけでなく, 問題番号も指定してコマンドを実行してください.
                    例 atcdr -d A 120  : A問題の120をダウンロードます
                    例 atcdr -d A 120..130  : A問題の120から130をダウンロードます
                """
            )
    else:
        second_args = convert_arg(str(second))

    if are_all_integers(first_args) and are_all_diffs(second_args):
        first_args_int = cast(List[int], first_args)
        second_args_diff = cast(List[Diff], second_args)
        problems = [
            Problem(Contest('abc', number), difficulty=diff)
            for number in first_args_int
            for diff in second_args_diff
        ]
        generate_problem_directory(base_path, problems, GenerateMode.gene_path_on_num)
    elif are_all_diffs(first_args) and are_all_integers(second_args):
        first_args_diff = cast(List[Diff], first_args)
        second_args_int = cast(List[int], second_args)
        problems = [
            Problem(Contest('abc', number), difficulty=diff)
            for diff in first_args_diff
            for number in second_args_int
        ]
        generate_problem_directory(base_path, problems, GenerateMode.gene_path_on_diff)
    else:
        raise ValueError(
            """次のような形式で問題を指定してください
                例 atcdr -d A 120..130  : A問題の120から130をダウンロードします
                例 atcdr -d 120         : ABCのコンテストの問題をダウンロードします
            """
        )
