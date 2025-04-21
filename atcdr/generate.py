import json
import os
import re

import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from atcdr.test import ResultStatus, TestRunner, create_renderable_test_info
from atcdr.util.fileops import add_file_selector
from atcdr.util.filetype import (
    FILE_EXTENSIONS,
    Filename,
    Lang,
    lang2str,
    str2lang,
)
from atcdr.util.gpt import ChatGPT, Model, set_api_key
from atcdr.util.parse import ProblemHTML


def get_code_from_gpt_output(output: str) -> str:
    pattern = re.compile(r'```(?:\w+)?\s*(.*?)\s*```', re.DOTALL)
    match = pattern.search(output)
    return match.group(1) if match else ''


def render_result_for_GPT(
    test: TestRunner,
) -> tuple[str, bool]:
    results = list(test)

    match test.info.summary:
        case ResultStatus.AC:
            return 'Accepted', True
        case ResultStatus.CE:
            return f'Compile Error \n {test.info.compiler_message}', False
        case _:
            message_for_gpt = ''.join(
                f'\n{result.label} => {result.result.passed.value}\nInput :\n{result.testcase.input}\nOutput :\n{result.result.output}\nExpected :\n{result.testcase.output}\n'
                if result.result.passed == ResultStatus.WA
                else f'\n{result.label} => {result.result.passed.value}\nInput :\n{result.testcase.input}\nOutput :\n{result.result.output}\n'
                for result in results
            )
            return message_for_gpt, False


def generate_code(file: Filename, lang: Lang, model: Model) -> None:
    console = Console()
    with open(file, 'r') as f:
        html_content = f.read()
    md = ProblemHTML(html_content).make_problem_markdown('en')

    if set_api_key() is None:
        return
    gpt = ChatGPT(
        system_prompt=f"""You are an excellent programmer. You solve problems in competitive programming.When a user provides you with a problem from a programming contest called AtCoder, including the Problem,Constraints, Input, Output, Input Example, and Output Example, please carefully consider these and solve the problem.Make sure that your output code block contains no more than two blocks. Pay close attention to the Input, Input Example, Output, and Output Example.Create the solution in {lang2str(lang)}.""",
        model=model,
    )
    with console.status(f'コード生成中 (by {gpt.model.value})'):
        reply = gpt.tell(md)

    code = get_code_from_gpt_output(reply)
    console.print('[green][+][/green] コードの生成に成功しました. ')
    console.rule(f'{gpt.model.value}による{lang2str(lang)}コード')
    console.print(Syntax(code=code, lexer=lang2str(lang)))

    saved_filename = (
        os.path.splitext(file)[0] + f'_by_{gpt.model.value}' + FILE_EXTENSIONS[lang]
    )
    with open(saved_filename, 'w') as f:
        console.print(
            f'[green][+][/green] {gpt.model.value} の出力したコードを保存しました：{f.name}'
        )
        f.write(code)


def generate_template(file: Filename, lang: Lang) -> None:
    console = Console()
    with open(file, 'r') as f:
        html_content = f.read()
    md = ProblemHTML(html_content).make_problem_markdown('en')

    if set_api_key() is None:
        return
    gpt = ChatGPT(
        system_prompt='You are a highly skilled programmer. Your role is to create a template code for competitive programming.',
        temperature=0.0,
    )

    propmpt = f"""
The user will provide a problem from a programming contest called AtCoder. This problem will include the Problem Statement, Constraints, Input, Output, Input Example, and Output Example. You should focus on the Constraints and Input sections to create the template in {lang2str(lang)}.

- First, create the part of the code that handles input. Then, you should read ###Input Block and ###Constraints Block.
- After receiving the input, define variables in the program by reading ###Constraints Block and explain how to use the variables in the comment of your code block with example.
- Last, define variables needed for output. Then you should read ###Output Block and ###Constraints Block.

You must not solve the problem. Please faithfully reproduce the variable names defined in the problem.
    """
    with console.status(f'{lang2str(lang)}のテンプレートを生成しています...'):
        reply = gpt.tell(md + propmpt)
    code = get_code_from_gpt_output(reply)

    savaed_filename = os.path.splitext(file)[0] + FILE_EXTENSIONS[lang]
    with open(savaed_filename, 'x') as f:
        console.print(
            f'[green][+][/green] テンプレートファイルを作成 :{savaed_filename}'
        )
        f.write(code)


def solve_problem(file: Filename, lang: Lang, model: Model) -> None:
    console = Console()
    with open(file, 'r') as f:
        html = ProblemHTML(f.read())

    md = html.make_problem_markdown('en')
    labeled_cases = html.load_labeled_testcase()

    if set_api_key() is None:
        return
    gpt = ChatGPT(
        system_prompt=f"""You are a brilliant programmer. Your task is to solve an AtCoder problem. AtCoder is a platform that hosts programming competitions where participants write programs to solve algorithmic challenges.Please solve the problem in {lang2str(lang)}.""",
        model=model,
    )

    file_without_ext = os.path.splitext(file)[0]

    for i in range(1, 4):
        with console.status(f'{i}回目のコード生成中 (by {gpt.model.value})'):
            if i == 1:
                test_report = ''
                reply = gpt.tell(md)
            else:
                prompt = f"""The following is the test report for the code you provided:
                {test_report}
Please provide an updated version of the code in {lang2str(lang)}."""
                console.print(
                    f'[green][+][/] 次のプロンプトを{gpt.model.value}に与え,再生成します'
                )
                console.print(Panel(prompt))
                reply = gpt.tell(prompt)

        code = get_code_from_gpt_output(reply)

        saved_filename = (
            f'{i}_'
            + file_without_ext
            + f'_by_{gpt.model.value}'
            + FILE_EXTENSIONS[lang]
        )
        with open(saved_filename, 'w') as f:
            console.print(f'[green][+][/] コードの生成に成功しました！：{f.name}')
            f.write(code)

        with console.status(
            f'{gpt.model.value}が生成したコードをテスト中', spinner='circleHalves'
        ):
            test = TestRunner(saved_filename, labeled_cases)
            test_report, is_ac = render_result_for_GPT(test)

        console.print(create_renderable_test_info(test.info))

        if is_ac:
            console.print('[green][+][/] コードのテストに成功!')
            break
        else:
            console.print('[red][-][/] コードのテストに失敗!')

    with open(
        'log_'
        + file_without_ext
        + f'_by_{gpt.model.value}'
        + FILE_EXTENSIONS[Lang.JSON],
        'w',
    ) as f:
        console.print(
            f'[green][+][/] {gpt.model.value}の出力のログを保存しました：{f.name}'
        )
        f.write(json.dumps(gpt.messages, indent=2))
    return


@click.command(short_help='コードを生成')
@add_file_selector('files', filetypes=[Lang.HTML])
@click.option('--lang', default='Python', help='出力するプログラミング言語')
@click.option('--model', default=Model.GPT41_MINI.value, help='使用するGPTモデル')
@click.option('--without-test', is_flag=True, help='テストケースを省略して生成')
@click.option('--template', is_flag=True, help='テンプレートを生成')
def generate(files, lang, model, without_test, template):
    """HTMLファイルからコード生成またはテンプレート出力を行います。"""
    la = str2lang(lang)
    model_enum = Model(model)

    for path in files:
        if template:
            generate_template(path, la)
        elif without_test:
            generate_code(path, la, model_enum)
        else:
            solve_problem(path, la, model_enum)
