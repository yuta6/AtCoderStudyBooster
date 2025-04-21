import os
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

import rich_click as click
from rich.console import Group, RenderableType
from rich.live import Live
from rich.markup import escape
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from atcdr.util.fileops import add_file_selector
from atcdr.util.filetype import (
    COMPILED_LANGUAGES,
    INTERPRETED_LANGUAGES,
    Lang,
    detect_language,
    lang2str,
)
from atcdr.util.parse import ProblemHTML


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
    results: List[ResultStatus] = field(default_factory=list)
    compiler_message: str = ''
    compile_time: Optional[int] = None
    _summary: Optional[ResultStatus] = None

    @property
    def summary(self) -> ResultStatus:
        if self._summary:
            return self._summary
        else:
            priority_order = [
                ResultStatus.CE,
                ResultStatus.RE,
                ResultStatus.WA,
                ResultStatus.TLE,
                ResultStatus.MLE,
                ResultStatus.WJ,
                ResultStatus.AC,
            ]
            priority_dict = {
                status: index + 1 for index, status in enumerate(priority_order)
            }
            summary = min(
                self.results,
                key=lambda status: priority_dict[status],
                default=ResultStatus.WJ,
            )

            if len(self.results) == self.case_number:
                return summary

            return ResultStatus.WJ if summary == ResultStatus.AC else summary

    @summary.setter
    def summary(self, value: ResultStatus) -> None:
        self._summary = value

    def update(
        self, updator: Union[TestCaseResult, LabeledTestCaseResult, ResultStatus]
    ) -> None:
        match updator:
            case TestCaseResult():
                self.results.append(updator.passed)
            case LabeledTestCaseResult():
                self.results.append(updator.result.passed)
            case ResultStatus():
                self.results.append(updator)

    def __iadd__(
        self, other: Union[TestCaseResult, LabeledTestCaseResult, ResultStatus]
    ) -> 'TestInformation':
        self.update(other)
        return self


class TestRunner:
    def __init__(self, path: str, lcases: List[LabeledTestCase]) -> None:
        self.source = path
        self.lcases = iter(lcases)
        self.info = TestInformation(
            lang=detect_language(self.source),
            sourcename=path,
            case_number=len(lcases),
        )

    def __iter__(self):
        lang = self.info.lang
        if lang in COMPILED_LANGUAGES:
            exe_path, compile_result, compile_time = run_compile(self.source, lang)
            self.info.compiler_message = compile_result.stderr
            self.info.compile_time = compile_time
            if compile_result.returncode != 0:
                self.info.results = [ResultStatus.CE]
                return iter([])

            self.cmd = [
                arg.format(source_path=self.source, exec_path=exe_path)
                for arg in LANGUAGE_RUN_COMMANDS[lang]
            ]
            self.exe = exe_path
            run_code(self.cmd, TestCase(input='', output=''))  # バイナリーの慣らし運転
        elif lang in INTERPRETED_LANGUAGES:
            self.cmd = [
                arg.format(source_path=self.source)
                for arg in LANGUAGE_RUN_COMMANDS[lang]
            ]
            self.exe = None
        else:
            raise ValueError(f'{lang}の適切な言語のランナーが見つかりませんでした.')

        return self

    def __next__(self):
        try:
            lcase = next(self.lcases)
            result = run_code(self.cmd, lcase.case)
            self.info += result
            return LabeledTestCaseResult(lcase.label, lcase.case, result)
        except StopIteration:
            if self.exe and os.path.exists(self.exe):
                os.remove(self.exe)
            raise


def run_code(cmd: list, case: TestCase) -> TestCaseResult:
    start_time = time.time()
    try:
        proc = subprocess.run(
            cmd, input=case.input, text=True, capture_output=True, timeout=4
        )
        end_time = time.time()
        executed_time = int((end_time - start_time) * 1000)
    except subprocess.TimeoutExpired as e_proc:
        end_time = time.time()
        executed_time = int((end_time - start_time) * 1000)
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
    Lang.C: ['{exec_path}'],
    Lang.CPP: ['{exec_path}'],
    Lang.RUST: ['{exec_path}'],
    Lang.JAVA: ['java', os.path.splitext(os.path.basename('{source_path}'))[0]],
}

LANGUAGE_COMPILE_COMMANDS: Dict[Lang, list] = {
    Lang.C: ['gcc', '{source_path}', '-o', '{exec_path}'],
    Lang.CPP: ['g++', '{source_path}', '-o', '{exec_path}'],
    Lang.RUST: ['rustc', '{source_path}', '-o', '{exec_path}'],
    Lang.JAVA: ['javac', '{source_path}'],
}


def run_compile(
    path: str, lang: Lang
) -> Tuple[str, subprocess.CompletedProcess, Optional[int]]:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        exec_path = tmp.name
    cmd = [
        arg.format(source_path=path, exec_path=exec_path)
        for arg in LANGUAGE_COMPILE_COMMANDS[lang]
    ]
    start_time = time.time()
    compile_result = subprocess.run(cmd, capture_output=True, text=True)
    compile_time = int((time.time() - start_time) * 1000)

    return exec_path, compile_result, compile_time


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
    ResultStatus.AC: Text.assemble(
        ('\u2713 ', 'green'),
        (
            f'{ResultStatus.AC.value}',
            Style(bgcolor=COLOR_MAP[ResultStatus.AC], bold=True),
        ),
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


def create_renderable_test_info(
    test_info: TestInformation, progress: Optional[Progress] = None
) -> RenderableType:
    components = []

    success_count = sum(1 for result in test_info.results if result == ResultStatus.AC)
    total_count = test_info.case_number

    status_text = STATUS_TEXT_MAP[test_info.summary]

    header_text = Text.assemble(
        Text.from_markup(f'[cyan]{test_info.sourcename}[/]のテスト \n'),
        Text.from_markup(
            f'[italic #0f0f0f]コンパイルにかかった時間: [not italic cyan]{test_info.compile_time}[/] ms[/]\n'
        )
        if test_info.compile_time
        else Text(''),
        status_text,
        Text.from_markup(
            f'  [{COLOR_MAP[test_info.summary]} bold]{success_count}[/] / [white bold]{total_count}[/]'
        ),
    )

    if progress:
        components.append(Panel(Group(header_text, progress), expand=False))
    else:
        components.append(Panel(header_text, expand=False))

    if test_info.compiler_message:
        rule = Rule(
            title='コンパイラーのメッセージ',
            style=COLOR_MAP[ResultStatus.CE],
        )
        components.append(rule)
        error_message = Syntax(
            test_info.compiler_message, lang2str(test_info.lang), line_numbers=False
        )
        components.append(error_message)

    return Group(*components)


def create_renderable_test_result(
    i: int,
    test_result: LabeledTestCaseResult,
) -> RenderableType:
    rule = Rule(
        title=f'No.{i+1} {test_result.label}',
        style=COLOR_MAP[test_result.result.passed],
    )

    # 以下の部分は if-else ブロックの外に移動
    status_header = Text.assemble(
        'ステータス ',
        STATUS_TEXT_MAP[test_result.result.passed],  # status_text をここに追加
    )

    execution_time_text = None
    if test_result.result.executed_time is not None:
        execution_time_text = Text.from_markup(
            f'実行時間   [cyan]{test_result.result.executed_time}[/cyan] ms'
        )

    table = Table(show_header=True, header_style='bold')
    table.add_column('入力', style='cyan', min_width=10)

    if test_result.result.passed != ResultStatus.AC:
        table.add_column(
            '出力',
            style=COLOR_MAP[test_result.result.passed],
            min_width=10,
            overflow='fold',
        )
        table.add_column('正解の出力', style=COLOR_MAP[ResultStatus.AC], min_width=10)
        table.add_row(
            escape(test_result.testcase.input),
            escape(test_result.result.output),
            escape(test_result.testcase.output),
        )
    else:
        table.add_column(
            '出力', style=COLOR_MAP[test_result.result.passed], min_width=10
        )
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


def render_results(test: TestRunner) -> None:
    progress = Progress(
        SpinnerColumn(style='white', spinner_name='circleHalves'),
        TextColumn('{task.description}'),
        SpinnerColumn(style='white', spinner_name='simpleDots'),
        BarColumn(),
    )
    task_id = progress.add_task(description='テスト進行中', total=test.info.case_number)

    current_display = [create_renderable_test_info(test.info, progress)]

    with Live(Group(*current_display)) as live:
        for i, result in enumerate(test):
            progress.advance(task_id, advance=1)
            current_display[-1] = create_renderable_test_info(test.info, progress)
            current_display.insert(-1, (create_renderable_test_result(i, result)))
            live.update(Group(*current_display))

        progress.update(task_id, description='テスト完了')  # 完了メッセージに更新
        current_display[-1] = create_renderable_test_info(test.info, progress)
        live.update(Group(*current_display))


def run_test(path_of_code: str) -> None:
    html_paths = [f for f in os.listdir('.') if f.endswith('.html')]
    if not html_paths:
        print(
            '問題のファイルが見つかりません。\n問題のファイルが存在するディレクトリーに移動してから実行してください。'
        )
        return

    with open(html_paths[0], 'r') as file:
        html = file.read()

    lcases = ProblemHTML(html).load_labeled_testcase()
    test = TestRunner(path_of_code, lcases)
    render_results(test)


@click.command(short_help='テストを実行')
@add_file_selector('files', filetypes=COMPILED_LANGUAGES + INTERPRETED_LANGUAGES)
def test(files):
    """指定したソースコードをサンプルケースでテストします。"""
    for path in files:
        run_test(path)
