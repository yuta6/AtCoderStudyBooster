import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Union

from bs4 import BeautifulSoup as bs
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from atcdr.util.execute import execute_files
from atcdr.util.filetype import FILE_EXTENSIONS, SOURCE_LANGUAGES, Lang


@dataclass
class TestCase:
	input: str
	output: str


@dataclass
class LabeledTestCase:
	label: str
	case: TestCase


class ResultStatus(Enum):
	CE = 'Compilation Error'
	MLE = 'Memory Limit Exceeded'
	TLE = 'Time Limit Exceeded'
	RE = 'Runtime Error'
	WA = 'Wrong Answer'
	AC = 'Accepted'


@dataclass
class TestCaseResult:
	output: str
	executed_time: Union[int, None]
	# memory_usage: Union[int, None]
	passed: ResultStatus


@dataclass
class LabeledTestCaseResult:
	label: str
	testcase: TestCase
	# TODO : 実はラベル自体を使わない方がいいかもしれない.ラベルという概念が削除してプリントするときに適当にTest1, Test2と適当に名前をつけてもいいかも.
	result: TestCaseResult


def create_testcases_from_html(html: str) -> List[LabeledTestCase]:
	soup = bs(html, 'html.parser')
	test_cases = []

	for i in range(1, 20):
		sample_input_section = soup.find('h3', text=f'Sample Input {i}')
		sample_output_section = soup.find('h3', text=f'Sample Output {i}')
		if not sample_input_section or not sample_output_section:
			break

		sample_input_pre = sample_input_section.find_next('pre')
		sample_output_pre = sample_output_section.find_next('pre')

		sample_input = (
			sample_input_pre.get_text(strip=True)
			if sample_input_pre is not None
			else ''
		)
		sample_output = (
			sample_output_pre.get_text(strip=True)
			if sample_output_pre is not None
			else ''
		)

		test_case = TestCase(input=sample_input, output=sample_output)
		labeled_test_case = LabeledTestCase(label=f'Sample {i}', case=test_case)
		test_cases.append(labeled_test_case)

	return test_cases


def run_code(cmd: list, case: TestCase) -> TestCaseResult:
	try:
		start_time = time.time()
		proc = subprocess.run(
			cmd, input=case.input, text=True, capture_output=True, timeout=4
		)
		end_time = time.time()

		execution_time = int((end_time - start_time) * 1000)

		if proc.returncode != 0:
			return TestCaseResult(
				output=proc.stderr, executed_time=None, passed=ResultStatus.RE
			)

		actual_output = proc.stdout.strip()
		expected_output = case.output.strip()

		if actual_output != expected_output:
			return TestCaseResult(
				output=actual_output,
				executed_time=execution_time,
				passed=ResultStatus.WA,
			)

		return TestCaseResult(
			output=actual_output, executed_time=execution_time, passed=ResultStatus.AC
		)
	except subprocess.TimeoutExpired:
		return TestCaseResult(
			output='Time Limit Exceeded', executed_time=None, passed=ResultStatus.TLE
		)
	except Exception as e:
		return TestCaseResult(output=str(e), executed_time=None, passed=ResultStatus.RE)


def run_python(path: str, case: TestCase) -> TestCaseResult:
	return run_code(['python3', path], case)


def run_javascript(path: str, case: TestCase) -> TestCaseResult:
	return run_code(['node', path], case)


def run_c(path: str, case: TestCase) -> TestCaseResult:
	with tempfile.NamedTemporaryFile(delete=True) as tmp:
		exec_path = tmp.name
		compile_result = subprocess.run(
			['gcc', path, '-o', exec_path], capture_output=True, text=True
		)
		if compile_result.returncode != 0:
			return TestCaseResult(
				output=compile_result.stderr, executed_time=None, passed=ResultStatus.CE
			)
		return run_code([exec_path], case)


def run_cpp(path: str, case: TestCase) -> TestCaseResult:
	with tempfile.NamedTemporaryFile(delete=True) as tmp:
		exec_path = tmp.name
		compile_result = subprocess.run(
			['g++', path, '-o', exec_path], capture_output=True, text=True
		)
		if compile_result.returncode != 0:
			return TestCaseResult(
				output=compile_result.stderr, executed_time=None, passed=ResultStatus.CE
			)
		return run_code([exec_path], case)


def run_rust(path: str, case: TestCase) -> TestCaseResult:
	with tempfile.NamedTemporaryFile(delete=True) as tmp:
		exec_path = tmp.name
		compile_result = subprocess.run(
			['rustc', path, '-o', exec_path], capture_output=True, text=True
		)
		if compile_result.returncode != 0:
			return TestCaseResult(
				output=compile_result.stderr, executed_time=None, passed=ResultStatus.CE
			)
		return run_code([exec_path], case)


def run_java(path: str, case: TestCase) -> TestCaseResult:
	compile_result = subprocess.run(['javac', path], capture_output=True, text=True)
	if compile_result.returncode != 0:
		return TestCaseResult(
			output=compile_result.stderr, executed_time=None, passed=ResultStatus.CE
		)
	class_file = os.path.splitext(path)[0]
	try:
		return run_code(['java', class_file], case)
	finally:
		class_path = class_file + '.class'
		if os.path.exists(class_path):
			os.remove(class_path)


LANGUAGE_RUNNERS: Dict[Lang, Callable[[str, TestCase], TestCaseResult]] = {
	Lang.PYTHON: run_python,
	Lang.JAVASCRIPT: run_javascript,
	Lang.C: run_c,
	Lang.CPP: run_cpp,
	Lang.RUST: run_rust,
	Lang.JAVA: run_java,
}


def choose_lang(path: str) -> Optional[Callable[[str, TestCase], TestCaseResult]]:
	ext = os.path.splitext(path)[1]
	lang = next(
		(lang for lang, extension in FILE_EXTENSIONS.items() if extension == ext), None
	)
	# lang が None でない場合のみ get を呼び出す
	if lang is not None:
		return LANGUAGE_RUNNERS.get(lang)
	return None


def judge_code_from(
	lcases: List[LabeledTestCase], path: str
) -> List[LabeledTestCaseResult]:
	runner = choose_lang(path)
	if runner is None:
		raise ValueError(f'ランナーが見つかりませんでした。指定されたパス: {path}')

	return [
		LabeledTestCaseResult(lcase.label, lcase.case, runner(path, lcase.case))
		for lcase in lcases
	]


class CustomFormatStyle(Enum):
	SUCCESS = 'green'
	FAILURE = 'red'
	WARNING = 'yellow'
	INFO = 'blue'


def render_results(path: str, results: List[LabeledTestCaseResult]) -> None:
	console = Console()
	success_count = sum(
		1 for result in results if result.result.passed == ResultStatus.AC
	)
	total_count = len(results)

	# ヘッダー
	header_text = Text.assemble(
		f'{path}のテスト  ',
		(
			f'{success_count}/{total_count} ',
			'green' if success_count == total_count else 'red',
		),
	)
	console.print(Panel(header_text, expand=False))

	CHECK_MARK = '\u2713'
	CROSS_MARK = '\u00d7'
	# 各テストケースの結果表示
	for i, result in enumerate(results):
		if result.result.passed == ResultStatus.AC:
			status_text = f'[green]{CHECK_MARK}[/] [white on green]{result.result.passed.value}[/]'
			console.rule(title=f'No.{i+1} {result.label}', style='green')
			console.print(f'[bold]ステータス:[/] {status_text}')

		else:
			status_text = f'[red]{CROSS_MARK} {result.result.passed.value}[/]'
			console.rule(title=f'No.{i+1} {result.label}', style='red')
			console.print(f'[bold]ステータス:[/] {status_text}')

		if result.result.executed_time is not None:
			console.print(f'[bold]実行時間:[/] {result.result.executed_time} ms')

		table = Table(show_header=True, header_style='bold')
		table.add_column('入力', style='cyan', min_width=10)
		if result.result.passed != ResultStatus.AC:
			table.add_column('出力', style='red', min_width=10)
			table.add_column('正解の出力', style='green', min_width=10)
			table.add_row(
				escape(result.testcase.input),
				escape(result.result.output),
				escape(result.testcase.output),
			)
		else:
			table.add_column('出力', style='green', min_width=10)
			table.add_row(escape(result.testcase.input), escape(result.result.output))
		console.print(table)


def run_test(path_of_code: str) -> None:
	html_paths = [f for f in os.listdir('.') if f.endswith('.html')]
	if not html_paths:
		print(
			'問題のファイルが見つかりません。\n問題のファイルが存在するディレクトリーに移動してから実行してください。'
		)
		return

	with open(html_paths[0], 'r') as file:
		html = file.read()

	test_cases = create_testcases_from_html(html)
	test_results = judge_code_from(test_cases, path_of_code)
	render_results(path_of_code, test_results)


def test(*args: str) -> None:
	execute_files(*args, func=run_test, target_filetypes=SOURCE_LANGUAGES)
