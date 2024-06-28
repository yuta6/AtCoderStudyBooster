from typing import Callable, Dict, List, Union, Optional,Tuple
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

def run_code(cmd: list, case: TestCase, memory_limit_kb: int = 256000) -> TestCaseResult:
    def set_memory_limit():
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit_kb * 1024, memory_limit_kb * 1024))

    try:
        start_time = time.time()
        proc = subprocess.run(cmd, input=case.input, text=True, capture_output=True, timeout=4, preexec_fn=set_memory_limit)
        end_time = time.time()

        execution_time = int((end_time - start_time) * 1000)
        memory_usage = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss // 1024

        if memory_usage > memory_limit_kb:
            return TestCaseResult(output=f"Memory usage exceeded {memory_limit_kb} KB", executed_time=execution_time, memory_usage=memory_usage, passed=ResultStatus.MLE)

        if proc.returncode != 0:
            return TestCaseResult(output=proc.stderr, executed_time=None, memory_usage=memory_usage, passed=ResultStatus.RE)

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

CHECK_MARK = '\u2713'

def print_result(lcase: LabeledTestCase, result: TestCaseResult) -> None:
    print(f"\n{Fore.CYAN}{lcase.label}のテスト結果:")

    if result.passed == ResultStatus.AC:
        print(Fore.GREEN + f"   [AC] {CHECK_MARK} パスしました\n   出力:\n{result.output}\n   実行時間: {result.executed_time} ms\n   メモリ使用量: {result.memory_usage} KB")
    elif result.passed == ResultStatus.WA:
        print(Fore.RED + f"   [WA] 不正解\n   出力:\n{result.output}\n   期待された出力:\n{lcase.case.output}")
    elif result.passed == ResultStatus.RE:
        print(Fore.YELLOW + f"   [RE] ランタイムエラー\n   エラー:\n{result.output}")
    elif result.passed == ResultStatus.TLE:
        print(Fore.YELLOW + "   [TLE] タイムアウトエラー")
    elif result.passed == ResultStatus.CE:
        print(Fore.YELLOW + f"   [CE] コンパイルエラー\n   エラー:\n{result.output}")
    elif result.passed == ResultStatus.MLE:
        print(Fore.YELLOW + f"   [ME] メモリ超過エラー\n   使用メモリ量: {result.memory_usage} KB")


def judge_code_from( lcases:List[LabeledTestCase], path:str)-> None :
    runner = choose_lang(path) 
    if runner is None : return 
    
    print(f"{path}をテストします.\n")
    print("-"*20)
    for lcase in lcases :
        result = runner(path, lcase.case)
        print_result(lcase, result)

def run_test(path:str)->None :
    # TODO; htmlファイルが場合はインターネットから取得する？コンテストのリンクなどを別ファイルにlink.py, link.ini, link.txtなどにまとめる. 
    html_path = [f for f in os.listdir('.') if f.endswith('.html')]
    if not html_path: return

    with open(os.path.join(path, html_path[0]), 'r') as file:
        html = file.read()
    
    test_cases = parse_html(html)
    judge_code_from(test_cases, path)

def list_files_with_extensions(extensions: List[str]) -> List[str]:
    return [f for f in os.listdir('.') if os.path.isfile(f) and os.path.splitext(f)[1] in extensions]

def test(*paths: Tuple[str, ...]) -> None:
    if not paths:
        files = list_files_with_extensions(list(LANGUAGE_RUNNERS.keys()))
        if len(files) == 1:
            run_test(files[0])
        elif len(files) > 1:
            print("複数のファイルが見つかりました。以下のファイルから選択してください:")
            for i, file in enumerate(files):
                print(f"{i+1}. {file}")
            choice = int(input("ファイル番号を入力してください: ")) - 1
            if 0 <= choice < len(files):
                run_test(files[choice])
            else:
                print("無効な選択です")
        else:
            print("テスト可能なファイルが見つかりません")
    elif paths == ('*',):
        files = list_files_with_extensions(list(LANGUAGE_RUNNERS.keys()))
        for file in files:
            run_test(file)
    else:
        for path in paths:
            ext = os.path.splitext(path)[1]
            if ext in LANGUAGE_RUNNERS:
                run_test(path)
            else:
                print(f"エラー: {path}はサポートされていないファイルタイプです")

def main() :
    test()
    
if __name__ == "__main__":
    main()


