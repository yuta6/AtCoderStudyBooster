import os
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Generator, List, Tuple, Union

from bs4 import BeautifulSoup as bs
from rich.console import Console, Group, RenderableType
from rich.markup import escape
from rich.panel import Panel
from rich.rule import Rule
from rich.style import Style
from rich.table import Table
from rich.text import Text

from atcdr.util.execute import execute_files
from atcdr.util.filetype import (
	COMPILED_LANGUAGES,
	INTERPRETED_LANGUAGES,
	Lang,
	detect_language,
)


@dataclass
class TestCase:
	input: str
	output: str


@dataclass
class LabeledTestCase:
	label: str
	case: TestCase


class ResultStatus(Enum):
	AC = 'Accepted'
	WA = 'Wrong Answer'
	TLE = 'Time Limit Exceeded'
	MLE = 'Memory Limit Exceeded'
	RE = 'Runtime Error'
	CE = 'Compilation Error'
	WJ = 'Juding ...'


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
	result: TestCaseResult


@dataclass
class TestInformation:
	lang: Lang
	sourcename: str
	case_number: int
	result_summary: ResultStatus = ResultStatus.WJ
	resultlist: List[LabeledTestCaseResult] = field(default_factory=list)  # 修正
	compiler_message: str = ''


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
	start_time = time.time()
	try:
		proc = subprocess.run(
			cmd, input=case.input, text=True, capture_output=True, timeout=4
		)
		executed_time = int(time.time() - start_time) * 1000
	except subprocess.TimeoutExpired as e_proc:
		executed_time = int(time.time() - start_time) * 1000
		stdout_text = e_proc.stdout.decode('utf-8') if e_proc.stdout is not None else ''
		stderr_text = e_proc.stderr.decode('utf-8') if e_proc.stderr is not None else ''
		text = stdout_text + '\n' + stderr_text
		return TestCaseResult(
			output=text, executed_time=executed_time, passed=ResultStatus.TLE
		)

	# プロセスの終了コードを確認し、異常終了ならREを返す
	if proc.returncode != 0:
		return TestCaseResult(
			output=proc.stdout + '\n' + proc.stderr,
			executed_time=executed_time,
			passed=ResultStatus.RE,
		)

	# 実際の出力と期待される出力を比較
	actual_output = proc.stdout.strip()
	expected_output = case.output.strip()

	if actual_output != expected_output:
		return TestCaseResult(
			output=actual_output,
			executed_time=executed_time,
			passed=ResultStatus.WA,
		)
	else:
		return TestCaseResult(
			output=actual_output, executed_time=executed_time, passed=ResultStatus.AC
		)


LANGUAGE_RUN_COMMANDS: Dict[Lang, list] = {
	Lang.PYTHON: ['python3', '{source_path}'],
	Lang.JAVASCRIPT: ['node', '{source_path}'],
	Lang.C: ['./{exec_path}'],
	Lang.CPP: ['{exec_path}'],
	Lang.RUST: ['./{exec_path}'],
	Lang.JAVA: ['java', '{exec_path}'],
}

LANGUAGE_COMPILE_COMMANDS: Dict[Lang, list] = {
	Lang.C: ['gcc', '{source_path}', '-o', '{exec_path}'],
	Lang.CPP: ['g++', '{source_path}', '-o', '{exec_path}'],
	Lang.RUST: ['rustc', '{source_path}', '-o', '{exec_path}'],
	Lang.JAVA: ['javac', '{source_path}'],
}


def run_compile(path: str, lang: Lang) -> Tuple[str, subprocess.CompletedProcess]:
	with tempfile.NamedTemporaryFile(delete=True) as tmp:
		exec_path = tmp.name
	cmd = [
		arg.format(source_path=path, exec_path=exec_path)
		for arg in LANGUAGE_COMPILE_COMMANDS[lang]
	]
	compile_result = subprocess.run(cmd, capture_output=True, text=True)

	return exec_path, compile_result


def judge_code_from(
	lcases: List[LabeledTestCase], path: str
) -> Generator[
	Union[LabeledTestCaseResult, TestInformation],  # type: ignore
	None,
	None,
]:
	lang = detect_language(path)
	if lang in COMPILED_LANGUAGES:
		exe_path, compile_result = run_compile(path, lang)
		if compile_result.returncode != 0:
			yield TestInformation(
				lang=lang,
				sourcename=path,
				case_number=len(lcases),
				result_summary=ResultStatus.CE,
				compiler_message=compile_result.stderr,
			)
			return
		else:
			yield TestInformation(
				lang=lang,
				sourcename=path,
				case_number=len(lcases),
				compiler_message=compile_result.stderr,
			)

			cmd = [
				arg.format(exec_path=exe_path) for arg in LANGUAGE_RUN_COMMANDS[lang]
			]

			for lcase in lcases:
				yield LabeledTestCaseResult(
					lcase.label, lcase.case, run_code(cmd, lcase.case)
				)

			if os.path.exists(exe_path):
				os.remove(exe_path)

	elif lang in INTERPRETED_LANGUAGES:
		yield TestInformation(
			lang=lang,
			sourcename=path,
			case_number=len(lcases),
		)
		cmd = [arg.format(source_path=path) for arg in LANGUAGE_RUN_COMMANDS[lang]]
		for lcase in lcases:
			yield LabeledTestCaseResult(
				lcase.label, lcase.case, run_code(cmd, lcase.case)
			)
	else:
		raise ValueError('適切な言語が見つかりませんでした.')


COLOR_MAP = {
	ResultStatus.AC: 'green',
	ResultStatus.WA: 'red',
	ResultStatus.TLE: 'yellow',
	ResultStatus.MLE: 'yellow',
	ResultStatus.RE: 'yellow',
	ResultStatus.CE: 'yellow',
	ResultStatus.WJ: 'grey',
}

STATUS_TEXT_MAP = {
	ResultStatus.AC: Text(
		f'\u2713 {ResultStatus.AC.value}',
		style=Style(color='white', bgcolor=COLOR_MAP[ResultStatus.AC], bold=True),
	),
	ResultStatus.WA: Text(
		f'\u00d7 {ResultStatus.WA.value}', style=COLOR_MAP[ResultStatus.WA]
	),
	ResultStatus.TLE: Text(
		f'\u00d7 {ResultStatus.TLE.value}', style=COLOR_MAP[ResultStatus.TLE]
	),
	ResultStatus.MLE: Text(
		f'\u00d7 {ResultStatus.MLE.value}', style=COLOR_MAP[ResultStatus.MLE]
	),
	ResultStatus.RE: Text(
		f'\u00d7 {ResultStatus.RE.value}', style=COLOR_MAP[ResultStatus.RE]
	),
	ResultStatus.CE: Text(
		f'\u00d7 {ResultStatus.CE.value}', style=COLOR_MAP[ResultStatus.CE]
	),
	ResultStatus.WJ: Text(
		f'\u23f3 {ResultStatus.WJ.value}', style=COLOR_MAP[ResultStatus.WJ]
	),
}


def create_renderable_test_info(test_info: TestInformation) -> RenderableType:
	components = []

	CHECK_MARK = '\u2713'
	CROSS_MARK = '\u00d7'

	success_count = sum(
		1 for result in test_info.resultlist if result.result.passed == ResultStatus.AC
	)
	total_count = test_info.case_number

	mark = CHECK_MARK if test_info.result_summary == ResultStatus.AC else CROSS_MARK

	header_text = Text.assemble(
		f'{test_info.sourcename}のテスト結果',
		(
			f'{success_count}/{total_count}',
			'green' if test_info.result_summary == ResultStatus.AC else 'red',
		),
		(
			f' {mark} {test_info.result_summary.value}',
			'green' if test_info.result_summary == ResultStatus.AC else 'red',
		),
	)

	components.append(header_text)

	if test_info.compiler_message:
		compiler_message_text = Text.from_markup(
			f'[white bold]コンパイルエラーのメッセージ[/]\n[red]{test_info.compiler_message}[/]'
		)
		components.append(compiler_message_text)

	# 全体をパネルで囲む（Groupは不要）
	return Panel(Group(*components), expand=True)


def update_test_info(
	test_info: TestInformation, test_result: LabeledTestCaseResult
) -> None:
	test_info.resultlist.append(test_result)

	priority_order = [
		ResultStatus.RE,
		ResultStatus.MLE,
		ResultStatus.TLE,
		ResultStatus.WA,
		ResultStatus.WJ,
		ResultStatus.AC,
	]

	# 現在の結果の中で最も高い優先順位のステータスを見つける
	highest_priority_status = (
		test_info.result_summary
	)  # デフォルトはWJまたは現在のサマリー
	for result in test_info.resultlist:
		status = result.result.passed
		if priority_order.index(status) < priority_order.index(highest_priority_status):
			highest_priority_status = status

	# 特殊ケース: すべてのテストケースがACである場合（途中でも）
	if all(result.result.passed == ResultStatus.AC for result in test_info.resultlist):
		test_info.result_summary = ResultStatus.AC
	else:
		test_info.result_summary = highest_priority_status


def create_renderable_test_result(
	i: int,
	test_result: LabeledTestCaseResult,
) -> RenderableType:
	CHECK_MARK = '\u2713'
	CROSS_MARK = '\u00d7'

	if test_result.result.passed == ResultStatus.AC:
		status_text = Text.from_markup(
			f'[green]{CHECK_MARK}[/] [white on green]{test_result.result.passed.value}[/]'
		)
		rule = Rule(title=f'No.{i+1} {test_result.label}', style='green')
	else:
		status_text = Text.from_markup(
			f'[red]{CROSS_MARK} {test_result.result.passed.value}[/]'
		)
		rule = Rule(title=f'No.{i+1} {test_result.label}', style='red')

	# 以下の部分は if-else ブロックの外に移動
	status_header = Text.assemble(
		'ステータス ',
		status_text,  # status_text をここに追加
	)

	execution_time_text = None
	if test_result.result.executed_time is not None:
		execution_time_text = Text.from_markup(
			f'実行時間   [cyan]{test_result.result.executed_time}[/cyan] ms'
		)

	table = Table(show_header=True, header_style='bold')
	table.add_column('入力', style='cyan', min_width=10)

	if test_result.result.passed != ResultStatus.AC:
		table.add_column('出力', style='red', min_width=10)
		table.add_column('正解の出力', style='green', min_width=10)
		table.add_row(
			escape(test_result.testcase.input),
			escape(test_result.result.output),
			escape(test_result.testcase.output),
		)
	else:
		table.add_column('出力', style='green', min_width=10)
		table.add_row(
			escape(test_result.testcase.input), escape(test_result.result.output)
		)

	components = [
		rule,
		status_header,
		execution_time_text if execution_time_text else '',
		table,
	]

	return Group(*components)


def render_results(
	results: Generator[Union[LabeledTestCaseResult, TestInformation], None, None],
) -> None:
	console = Console()

	# 最初の結果は TestInformation として取得
	first_result = next(results)
	if not isinstance(first_result, TestInformation):
		raise ValueError('最初のジェネレーターの結果はTestInformationです')
	test_info: TestInformation = first_result

	# 各テストケースの結果表示
	for i, result in enumerate(results):
		if isinstance(result, LabeledTestCaseResult):
			console.print(create_renderable_test_result(i, result))
			update_test_info(test_info, result)
		else:
			raise ValueError('テスト結果がyieldする型はLabeledTestCaseResultです')

	console.print(create_renderable_test_info(test_info))


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
	render_results(test_results)


def test(*args: str) -> None:
	execute_files(
		*args,
		func=run_test,
		target_filetypes=INTERPRETED_LANGUAGES + COMPILED_LANGUAGES,
	)
