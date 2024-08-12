import os
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Match, Optional, Union, cast

import requests

from atcdr.util.problem import make_problem_markdown


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
			print(
				f'[Error{response.status_code}] 再試行します. abc{problem.number} {problem.difficulty.value}'
			)
			time.sleep(retry_wait)
		elif 300 <= response.status_code < 400:
			print(
				f'[Erroe{response.status_code}] リダイレクトが発生しました。abc{problem.number} {problem.difficulty.value}'
			)
		elif 400 <= response.status_code < 500:
			print(
				f'[Error{response.status_code}] 問題が見つかりません。abc{problem.number} {problem.difficulty.value}'
			)
			break
		elif 500 <= response.status_code < 600:
			print(
				f'[Error{response.status_code}] サーバーエラーが発生しました。abc{problem.number} {problem.difficulty.value}'
			)
			break
		else:
			print(
				f'[Error{response.status_code}] abc{problem.number} {problem.difficulty.value}に対応するHTMLファイルを取得できませんでした。'
			)
			break
	return None


def repair_html(html: str) -> str:
	html = html.replace('//img.atcoder.jp', 'https://img.atcoder.jp')
	html = html.replace(
		'<meta http-equiv="Content-Language" content="en">',
		'<meta http-equiv="Content-Language" content="ja">',
	)
	html = html.replace('LANG = "en"', 'LANG="ja"')
	return html


def get_title_from_html(html: str) -> Optional[str]:
	title_match: Optional[Match[str]] = re.search(
		r'<title>(?:.*?-\s*)?([^<]*)</title>', html, re.IGNORECASE | re.DOTALL
	)
	if title_match:
		title: str = title_match.group(1).replace(' ', '')
		title = re.sub(r'[\\/*?:"<>| ]', '', title)
		return title
	return None


def save_file(file_path: str, html: str) -> None:
	with open(file_path, 'w', encoding='utf-8') as file:
		file.write(html)
	print(f'[+] ファイルを保存しました :{file_path}')


def mkdir(path: str) -> None:
	if not os.path.exists(path):
		os.makedirs(path)
		print(f'[+] フォルダー: {path} を作成しました')


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
		if title is None:
			print('[Error] タイトルが取得できませんでした')
			title = f'problem{problem.number}{problem.difficulty.value}'

		mkdir(dir_path)
		repaired_html = repair_html(html)

		html_path = os.path.join(dir_path, f'{title}.html')
		save_file(html_path, repaired_html)
		md = make_problem_markdown(html, 'ja')
		save_file(os.path.join(dir_path, f'{title}.md'), md)


def parse_range(range_str: str) -> List[int]:
	match = re.match(r'^(\d+)\.\.(\d+)$', range_str)
	if match:
		start, end = map(int, match.groups())
		return list(range(start, end + 1))
	else:
		raise ValueError('Invalid range format')


def parse_diff_range(range_str: str) -> List[Diff]:
	match = re.match(r'^([A-F])\.\.([A-F])$', range_str)
	if match:
		start, end = match.groups()
		start_index = ord(start) - ord('A')
		end_index = ord(end) - ord('A')
		if start_index <= end_index:
			return [Diff(chr(i + ord('A'))) for i in range(start_index, end_index + 1)]
	raise ValueError('A..C の形式になっていません')


def convert_arg(arg: Union[str, int]) -> Union[List[int], List[Diff]]:
	if isinstance(arg, int):
		return [arg]
	elif isinstance(arg, str):
		if arg.isdigit():
			return [int(arg)]
		elif arg in Diff.__members__:
			return [Diff[arg]]
		elif re.match(r'^\d+\.\.\d+$', arg):
			return parse_range(arg)
		elif re.match(r'^[A-F]\.\.[A-F]$', arg):
			return parse_diff_range(arg)
	raise ValueError(f'{arg}は認識できません')


def are_all_integers(args: Union[List[int], List[Diff]]) -> bool:
	return all(isinstance(arg, int) for arg in args)


def are_all_diffs(args: Union[List[int], List[Diff]]) -> bool:
	return all(isinstance(arg, Diff) for arg in args)


def download(
	first: Union[str, int, None] = None,
	second: Union[str, int, None] = None,
	base_path: str = '.',
) -> None:
	if first is None:
		main()
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


def main() -> None:
	print('AtCoderの問題のHTMLファイルをダウンロードします')
	print(
		"""
    1. 番号の範囲を指定してダウンロードする
    2. 1ファイルだけダウンロードする
    q: 終了
    """
	)

	choice = input('選択してください: ')

	if choice == '1':
		start_end = input(
			'開始と終了のコンテストの番号をスペースで区切って指定してください (例: 223 230): '
		)
		start, end = map(int, start_end.split(' '))
		difficulty = Diff[
			input(
				'ダウンロードする問題の難易度を指定してください (例: A, B, C): '
			).upper()
		]
		problem_list = [Problem(number, difficulty) for number in range(start, end + 1)]
		generate_problem_directory('.', problem_list, GenerateMode.gene_path_on_diff)
	elif choice == '2':
		number = int(input('コンテストの番号を指定してください: '))
		difficulty = Diff[
			input(
				'ダウンロードする問題の難易度を指定してください (例: A, B, C): '
			).upper()
		]
		generate_problem_directory(
			'.', [Problem(number, difficulty)], GenerateMode.gene_path_on_diff
		)
	elif choice == 'q':
		print('終了します')
	else:
		print('無効な選択です')


if __name__ == '__main__':
	main()
