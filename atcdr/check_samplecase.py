from typing import Callable, Dict, List, Union, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup as bs
import itertools
import subprocess
import os
from enum import Enum
import resource
import time

import colorama
from colorama import Fore, Style
import tempfile

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
    output: str  # エラーの場合はサブプロセスのメッセージを表示させる。ResultStatusがCEならコンパイルエラーを格納し,WAやACならsubprocessのoutputを格納して, REならそのエラーを格納します
    executed_time: Union[int, None]  # プログラムの実行時間を格納します, RE, CEの場合はNoneになります
    memory_usage: Union[int, None]  # プログラムの実行時のメモリーサイズです. RE, CEなどの場合はNoneになります
    passed: ResultStatus


def parse_html(html: str) -> List[LabeledTestCase]:
    soup = bs(html, 'html.parser')
    test_cases = []

    for i in itertools.count(1):
        sample_input_section = soup.find('h3', text=f'Sample Input {i}').find_next('pre')
        sample_output_section = soup.find('h3', text=f'Sample Output {i}').find_next('pre')
        if not sample_input_section or not sample_output_section:
            break

        sample_input = sample_input_section.get_text(strip=True)
        sample_output = sample_output_section.get_text(strip=True)

        test_case = TestCase(input=sample_input, output=sample_output)
        labeled_test_case = LabeledTestCase(label=f'Sample {i}', case=test_case)
        test_cases.append(labeled_test_case)

    return test_cases

def run_code(cmd: list, case: TestCase) -> TestCaseResult:
    try:
        start_time = time.time()
        proc = subprocess.run(cmd, input=case.input, text=True, capture_output=True, timeout=4)
        end_time = time.time()

        execution_time = int((end_time - start_time) * 1000)
        memory_usage = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss // 1024

        if proc.returncode != 0:
            return TestCaseResult(output=proc.stderr, executed_time=None, memory_usage=None, passed=ResultStatus.RE)

        actual_output = proc.stdout.strip()
        expected_output = case.output.strip()

        if actual_output != expected_output:
            return TestCaseResult(output=actual_output, executed_time=execution_time, memory_usage=memory_usage, passed=ResultStatus.WA)

        return TestCaseResult(output=actual_output, executed_time=execution_time, memory_usage=memory_usage, passed=ResultStatus.AC)
    except subprocess.TimeoutExpired:
        return TestCaseResult(output="Time Limit Exceeded", executed_time=None, memory_usage=None, passed=ResultStatus.TLE)
    except Exception as e:
        return TestCaseResult(output=str(e), executed_time=None, memory_usage=None, passed=ResultStatus.RE)

def run_python(path: str, case: TestCase) -> TestCaseResult:
    return run_code(['python3', path], case)

def run_cpp(path: str, case: TestCase) -> TestCaseResult:
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        exec_path = tmp.name
        compile_result = subprocess.run(['g++', path, '-o', exec_path], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return TestCaseResult(output=compile_result.stderr, executed_time=None, memory_usage=None, passed=ResultStatus.CE)
        return run_code([exec_path], case)

def run_c(path: str, case: TestCase) -> TestCaseResult:
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        exec_path = tmp.name
        compile_result = subprocess.run(['gcc', path, '-o', exec_path], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return TestCaseResult(output=compile_result.stderr, executed_time=None, memory_usage=None, passed=ResultStatus.CE)
        return run_code([exec_path], case)

def run_rust(path: str, case: TestCase) -> TestCaseResult:
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        exec_path = tmp.name
        compile_result = subprocess.run(['rustc', path, '-o', exec_path], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return TestCaseResult(output=compile_result.stderr, executed_time=None, memory_usage=None, passed=ResultStatus.CE)
        return run_code([exec_path], case)

def run_java(path: str, case: TestCase) -> TestCaseResult:
    compile_result = subprocess.run(['javac', path], capture_output=True, text=True)
    if compile_result.returncode != 0:
        return TestCaseResult(output=compile_result.stderr, executed_time=None, memory_usage=None, passed=ResultStatus.CE)
    class_file = os.path.splitext(path)[0]
    try:
        return run_code(['java', class_file], case)
    finally:
        class_path = class_file + '.class'
        if os.path.exists(class_path):
            os.remove(class_path)

def run_javascript(path: str, case: TestCase) -> TestCaseResult:
    return run_code(['node', path], case)


LANGUAGE_RUNNERS: Dict[str, Callable[[str, TestCase], TestCaseResult]] = {
    '.py': run_python,
    '.cpp': run_cpp,
    '.c': run_c,
    '.rs': run_rust,
    '.java': run_java,
    '.js': run_javascript
}

def choose_lang(path: str) -> Optional[Callable[[str, TestCase], TestCaseResult]]:
    ext = os.path.splitext(path)[1]
    return LANGUAGE_RUNNERS[ext] if ext not in LANGUAGE_RUNNERS else None

def print_result(lcase:LabeledTestCase , result:TestCaseResult)->None :
    print(f"{lcase.label}のテスト")
    # ここを書いてください。色でわかりやすくかいてもらうとありがたいです。


def judge_code_from( lcases:List[LabeledTestCase], path:str)-> None :
    runner = choose_lang(path) 
    if runner is None : return 
    
    print(f"{path}をテストします\n")
    for lcase in lcases :
        result = runner(path, lcase.case)
        print_result(lcase, result)

def run_test(path:str=None)->None :
    if path is None:
        # TODO :pathがない場合は自動で指定する, フォルダー内を検索してテストする, LANGUAGE_RUNNERに該当する拡張子をチェックし, 自動でpathを指定する.
        return 

    # TODO; htmlファイルが場合はインターネットから取得する？コンテストのリンクなどを別ファイルにlink.py, link.ini, link.txtなどにまとめる. 
    html_path = [f for f in os.listdir(path) if f.endswith('.html')]
    if not html_path: return

    with open(os.path.join(path, html_path[0]), 'r') as file:
        html = file.read()
    
    test_cases = parse_html(html)
    judge_code_from(test_cases, path)

if __name__ == "__main__":
    run_test()



