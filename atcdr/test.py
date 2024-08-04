import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Union

import colorama
from bs4 import BeautifulSoup as bs
from colorama import Fore

from atcdr.util.filename import FileExtension, execute_files

colorama.init(autoreset=True)


@dataclass
class TestCase:
    input: str
    output: str


@dataclass
class LabeledTestCase:
    label: str
    case: TestCase


class ResultStatus(Enum):
    CE = "Compilation Error"
    MLE = "Memory Limit Exceeded"
    TLE = "Time Limit Exceeded"
    RE = "Runtime Error"
    WA = "Wrong Answer"
    AC = "Accepted"


@dataclass
class TestCaseResult:
    output: str
    executed_time: Union[int, None]
    # memory_usage: Union[int, None]
    passed: ResultStatus


def parse_html(html: str) -> List[LabeledTestCase]:
    soup = bs(html, "html.parser")
    test_cases = []

    for i in range(1, 20):
        sample_input_section = soup.find("h3", text=f"Sample Input {i}")
        sample_output_section = soup.find("h3", text=f"Sample Output {i}")
        if not sample_input_section or not sample_output_section:
            break

        sample_input_pre = sample_input_section.find_next("pre")
        sample_output_pre = sample_output_section.find_next("pre")

        sample_input = sample_input_pre.get_text(strip=True)
        sample_output = sample_output_pre.get_text(strip=True)

        test_case = TestCase(input=sample_input, output=sample_output)
        labeled_test_case = LabeledTestCase(label=f"Sample {i}", case=test_case)
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
            output="Time Limit Exceeded", executed_time=None, passed=ResultStatus.TLE
        )
    except Exception as e:
        return TestCaseResult(output=str(e), executed_time=None, passed=ResultStatus.RE)


def run_python(path: str, case: TestCase) -> TestCaseResult:
    return run_code(["python3", path], case)


def run_javascript(path: str, case: TestCase) -> TestCaseResult:
    return run_code(["node", path], case)


def run_c(path: str, case: TestCase) -> TestCaseResult:
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        exec_path = tmp.name
        compile_result = subprocess.run(
            ["gcc", path, "-o", exec_path], capture_output=True, text=True
        )
        if compile_result.returncode != 0:
            return TestCaseResult(
                output=compile_result.stderr, executed_time=None, passed=ResultStatus.CE
            )
        if compile_result.stderr:
            print(f"コンパイラーからのメッセージ\n{compile_result.stderr}")
        return run_code([exec_path], case)


def run_cpp(path: str, case: TestCase) -> TestCaseResult:
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        exec_path = tmp.name
        compile_result = subprocess.run(
            ["g++", path, "-o", exec_path], capture_output=True, text=True
        )
        if compile_result.returncode != 0:
            return TestCaseResult(
                output=compile_result.stderr, executed_time=None, passed=ResultStatus.CE
            )
        if compile_result.stderr:
            print(f"コンパイラーからのメッセージ\n{compile_result.stderr}")
        return run_code([exec_path], case)


def run_rust(path: str, case: TestCase) -> TestCaseResult:
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        exec_path = tmp.name
        compile_result = subprocess.run(
            ["rustc", path, "-o", exec_path], capture_output=True, text=True
        )
        if compile_result.returncode != 0:
            return TestCaseResult(
                output=compile_result.stderr, executed_time=None, passed=ResultStatus.CE
            )
        if compile_result.stderr:
            print(f"コンパイラーからのメッセージ\n{compile_result.stderr}")
        return run_code([exec_path], case)


def run_java(path: str, case: TestCase) -> TestCaseResult:
    compile_result = subprocess.run(["javac", path], capture_output=True, text=True)
    if compile_result.returncode != 0:
        return TestCaseResult(
            output=compile_result.stderr, executed_time=None, passed=ResultStatus.CE
        )
    class_file = os.path.splitext(path)[0]
    try:
        return run_code(["java", class_file], case)
    finally:
        class_path = class_file + ".class"
        if os.path.exists(class_path):
            os.remove(class_path)


LANGUAGE_RUNNERS: Dict[str, Callable[[str, TestCase], TestCaseResult]] = {
    ".py": run_python,
    ".js": run_javascript,
    ".c": run_c,
    ".cpp": run_cpp,
    ".rs": run_rust,
    ".java": run_java,
}


def choose_lang(path: str) -> Optional[Callable[[str, TestCase], TestCaseResult]]:
    ext = os.path.splitext(path)[1]
    return LANGUAGE_RUNNERS[ext] if ext in LANGUAGE_RUNNERS else None


CHECK_MARK = "\u2713"
CROSS_MARK = "\u00d7"


def print_result(lcase: LabeledTestCase, result: TestCaseResult) -> None:
    print(f"{Fore.CYAN}{lcase.label} のテスト:")

    if result.passed == ResultStatus.AC:
        print(
            Fore.GREEN
            + f"{CHECK_MARK} Accepted !! 実行時間: {result.executed_time} ms\n 出力\n{result.output}\n   "
        )
    elif result.passed == ResultStatus.WA:
        print(
            Fore.RED
            + f"{CROSS_MARK} Wrong Answer 実行時間: {result.executed_time} ms 出力:\n{result.output}\n   正解の出力:\n{lcase.case.output}"
        )
    elif result.passed == ResultStatus.RE:
        print(Fore.YELLOW + f"[RE] ランタイムエラー\n{result.output}")
    elif result.passed == ResultStatus.TLE:
        print(Fore.YELLOW + "[TLE] タイムアウトエラー\n")
    elif result.passed == ResultStatus.CE:
        print(Fore.YELLOW + f"[CE] コンパイルエラー\n{result.output}")
    elif result.passed == ResultStatus.MLE:
        print(Fore.YELLOW + "[ME] メモリ超過エラー\n")


def judge_code_from(lcases: List[LabeledTestCase], path: str) -> None:
    runner = choose_lang(path)
    if runner is None:
        return

    print(f"{path}をテストします.")
    print("-" * 20)
    for lcase in lcases:
        result = runner(path, lcase.case)
        print_result(lcase, result)


def run_test(path_of_code: str) -> None:
    html_paths = [f for f in os.listdir(".") if f.endswith(".html")]
    if not html_paths:
        return

    with open(html_paths[0], "r") as file:
        html = file.read()

    test_cases = parse_html(html)
    judge_code_from(test_cases, path_of_code)


def test(*args: str) -> None:
    execute_files(
        *args, func=run_test, target_filetypes=FileExtension.SOURCE_EXTENSIONS
    )
