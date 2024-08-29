import os
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional, Union, cast

import questionary as q
import requests
from rich.console import Console
from rich.prompt import IntPrompt, Prompt

from atcdr.util.filetype import FILE_EXTENSIONS, Lang
from atcdr.util.problem import (
	get_title_from_html,
	make_problem_markdown,
	repair_html,
	title_to_filename,
)

console = Console()


class Diff(Enum):
	A = 'A'
	B = 'B'
	C = 'C'
	D = 'D'
	E = 'E'
	F = 'F'
	G = 'G'


@dataclass
class Problem:
	number: int
	difficulty: Diff


def get_problem_html(problem: Problem) -> Optional[str]:
	url = f'https://atcoder.jp/contests/abc{problem.number}/tasks/abc{problem.number}_{problem.difficulty.value.lower()}'
	response = requests.get(url)
	retry_attempts = 3
	retry_wait = 1  # 1 second

	for _ in range(retry_attempts):
		response = requests.get(url)
		if response.status_code == 200:
			return response.text
		elif response.status_code == 429:
			console.print(
				f'[bold yellow][Error {response.status_code}][/bold yellow] 再試行します。abc{problem.number} {problem.difficulty.value}'
			)
			time.sleep(retry_wait)
		elif 300 <= response.status_code < 400:
			console.print(
				f'[bold yellow][Error {response.status_code}][/bold yellow] リダイレクトが発生しました。abc{problem.number} {problem.difficulty.value}'
			)
		elif 400 <= response.status_code < 500:
			console.print(
				f'[bold red][Error {response.status_code}][/bold red] 問題が見つかりません。abc{problem.number} {problem.difficulty.value}'
			)
			break
		elif 500 <= response.status_code < 600:
			console.print(
				f'[bold red][Error {response.status_code}][/bold red] サーバーエラーが発生しました。abc{problem.number} {problem.difficulty.value}'
			)
			break
		else:
			console.print(
				f'[bold red][Error {response.status_code}][/bold red] abc{problem.number} {problem.difficulty.value}に対応するHTMLファイルを取得できませんでした。'
			)
			break
	return None


def save_file(file_path: str, html: str) -> None:
	with open(file_path, 'w', encoding='utf-8') as file:
		file.write(html)
	console.print(f'[bold green][+][/bold green] ファイルを保存しました :{file_path}')


def mkdir(path: str) -> None:
	if not os.path.exists(path):
		os.makedirs(path)
		console.print(f'[bold green][+][/bold green] フォルダー: {path} を作成しました')


class GenerateMode:
	@staticmethod
	def gene_path_on_diff(base: str, number: int, diff: Diff) -> str:
		return os.path.join(base, diff.name, str(number))

	@staticmethod
	def gene_path_on_num(base: str, number: int, diff: Diff) -> str:
		return os.path.join(base, str(number), diff.name)


def generate_problem_directory(
	base_path: str, problems: List[Problem], gene_path: Callable[[str, int, Diff], str]
) -> None:
	for problem in problems:
		dir_path = gene_path(base_path, problem.number, problem.difficulty)

		html = get_problem_html(problem)
		if html is None:
			continue

		title = get_title_from_html(html)
		if not title:
			console.print('[bold red][Error][/bold red] タイトルが取得できませんでした')
			title = f'problem{problem.number}{problem.difficulty.value}'

		title = title_to_filename(title)

		mkdir(dir_path)
		repaired_html = repair_html(html)

		html_path = os.path.join(dir_path, title + FILE_EXTENSIONS[Lang.HTML])
		save_file(html_path, repaired_html)
		md = make_problem_markdown(html, 'ja')
		md_path = os.path.join(dir_path, title + FILE_EXTENSIONS[Lang.MARKDOWN])
		save_file(md_path, md)


def parse_range(range_str: str) -> List[int]:
	match = re.match(r'^(\d+)\.\.(\d+)$', range_str)
	if match:
		start, end = map(int, match.groups())
		return list(range(start, end + 1))
	else:
		raise ValueError('数字の範囲の形式が間違っています')


def parse_diff_range(range_str: str) -> List[Diff]:
	match = re.match(r'^([A-Z])\.\.([A-Z])$', range_str)
	if match:
		start, end = match.groups()
		start_index = ord(start) - ord('A')
		end_index = ord(end) - ord('A')
		if start_index <= end_index:
			return [Diff(chr(i + ord('A'))) for i in range(start_index, end_index + 1)]
	raise ValueError('A..C の形式になっていません')


def convert_arg(arg: str) -> Union[List[int], List[Diff]]:
	if isinstance(arg, int):
		return [arg]
	elif isinstance(arg, str):
		if arg.isdigit():
			return [int(arg)]
		elif arg in Diff.__members__:
			return [Diff[arg]]
		elif re.match(r'^\d+\.\.\d+$', arg):
			return parse_range(arg)
		elif re.match(r'^[A-Z]\.\.[A-Z]$', arg):
			return parse_diff_range(arg)
	raise ValueError(f'{arg}は認識できません')


def are_all_integers(args: Union[List[int], List[Diff]]) -> bool:
	return all(isinstance(arg, int) for arg in args)


def are_all_diffs(args: Union[List[int], List[Diff]]) -> bool:
	return all(isinstance(arg, Diff) for arg in args)


def interactive_download() -> None:
	CONTEST = '1. 特定のコンテストの問題を解きたい'
	PRACTICE = '2. 特定の難易度の問題を集中的に練習したい'
	ONE_FILE = '3. 1ファイルだけダウンロードする'
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
		number = IntPrompt.ask(
			'コンテスト番号を入力してください (例: 120)',
		)
		contest_diffs = list(Diff)

		problems = [Problem(number, diff) for diff in contest_diffs]

		generate_problem_directory('.', problems, GenerateMode.gene_path_on_num)

	elif choice == PRACTICE:
		diff = Prompt.ask(
			'難易度を入力してください (例: A)',
		)
		try:
			diff = Diff[diff.upper()]
		except KeyError:
			raise ValueError('入力された難易度が認識できません')
		number_str = Prompt.ask(
			'コンテスト番号または範囲を入力してください (例: 120..130)'
		)
		if number_str.isdigit():
			contest_numbers = [int(number_str)]
		elif re.match(r'^\d+\.\.\d+$', number_str):
			contest_numbers = parse_range(number_str)
		else:
			raise ValueError('数字の範囲の形式が間違っています')

		problems = [Problem(number, diff) for number in contest_numbers]

		generate_problem_directory('.', problems, GenerateMode.gene_path_on_diff)

	elif choice == ONE_FILE:
		contest_number = IntPrompt.ask(
			'コンテスト番号を入力してください (例: 120)',
		)
		difficulty = Prompt.ask(
			'難易度を入力してください (例: A)', choices=[d.name for d in Diff]
		)

		difficulty = difficulty.upper().strip()

		problem = Problem(contest_number, Diff[difficulty])
		generate_problem_directory('.', [problem], GenerateMode.gene_path_on_num)

	elif choice == END:
		console.print('終了します', style='bold red')
	else:
		console.print('無効な選択です', style='bold red')


def download(
	first: Union[str, int, None] = None,
	second: Union[str, int, None] = None,
	base_path: str = '.',
) -> None:
	if first is None:
		interactive_download()
		return

	first_args = convert_arg(str(first))
	if second is None:
		if isinstance(first, Diff):
			raise ValueError(
				"""難易度だけでなく, 問題番号も指定してコマンドを実行してください.
                    例 atcdr -d A 120  : A問題の120をダウンロードます
                    例 atcdr -d A 120..130  : A問題の120から130をダウンロードます
                """
			)
		second_args: Union[List[int], List[Diff]] = list(Diff)
	else:
		second_args = convert_arg(str(second))

	if are_all_integers(first_args) and are_all_diffs(second_args):
		first_args_int = cast(List[int], first_args)
		second_args_diff = cast(List[Diff], second_args)
		problems = [
			Problem(number, diff)
			for number in first_args_int
			for diff in second_args_diff
		]
		generate_problem_directory(base_path, problems, GenerateMode.gene_path_on_num)
	elif are_all_diffs(first_args) and are_all_integers(second_args):
		first_args_diff = cast(List[Diff], first_args)
		second_args_int = cast(List[int], second_args)
		problems = [
			Problem(number, diff)
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
