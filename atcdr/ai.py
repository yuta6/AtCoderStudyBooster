import json
import random
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import rich_click as click
from openai import BadRequestError, OpenAI
from rich.console import Console
from rich.live import Live
from rich.markup import escape
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from atcdr.test import (
    LabeledTestCase,
    ResultStatus,
    TestCase,
    TestRunner,
)
from atcdr.util.fileops import add_file_selector
from atcdr.util.filetype import (
    COMPILED_LANGUAGES,
    FILE_EXTENSIONS,
    INTERPRETED_LANGUAGES,
    Lang,
    str2lang,
)
from atcdr.util.i18n import _
from atcdr.util.openai import set_api_key
from atcdr.util.parse import ProblemHTML


def render_result_for_GPT(test: TestRunner) -> tuple[str, bool]:
    results = list(test)
    match test.info.summary:
        case ResultStatus.CE:
            return f'Compile Error \n {test.info.compiler_message}', False
        case _:
            message_for_gpt = ''.join(
                (
                    f'\n{r.label} => {r.result.passed.value}, Execution Time : {r.result.executed_time}\n'
                    f'\nInput :\n{r.testcase.input}\nOutput :\n{r.result.output}\nExpected :\n{r.testcase.output}\n'
                    if r.result.passed == ResultStatus.WA
                    else f'\n{r.label} => {r.result.passed.value}\nInput :\n{r.testcase.input}\nOutput :\n{r.result.output}\n'
                )
                for r in results
            )
            return message_for_gpt, False


def display_test_results(console: Console, test: TestRunner) -> None:
    results = list(test)

    table = Table(title='🧪 Test Results')
    table.add_column('Test Case', style='cyan', no_wrap=True)
    table.add_column('Status', justify='center', no_wrap=True)
    table.add_column('Input', style='dim', max_width=30)
    table.add_column('Output', style='yellow', max_width=30)
    table.add_column('Expected', style='green', max_width=30)

    for r in results:
        if r.result.passed == ResultStatus.AC:
            status = '[green]✅ AC[/green]'
        elif r.result.passed == ResultStatus.WA:
            status = '[red]❌ WA[/red]'
        elif r.result.passed == ResultStatus.TLE:
            status = '[yellow]⏰ TLE[/yellow]'
        elif r.result.passed == ResultStatus.RE:
            status = '[red]💥 RE[/red]'
        else:
            status = f'[red]{r.result.passed.value}[/red]'

        input_preview = escape(
            r.testcase.input.strip()[:50] + '...'
            if len(r.testcase.input.strip()) > 50
            else r.testcase.input.strip()
        )
        output_preview = escape(
            r.result.output.strip()[:50] + '...'
            if len(r.result.output.strip()) > 50
            else r.result.output.strip()
        )
        expected_preview = escape(
            r.testcase.output.strip()[:50] + '...'
            if len(r.testcase.output.strip()) > 50
            else r.testcase.output.strip()
        )

        table.add_row(r.label, status, input_preview, output_preview, expected_preview)

    console.print(table)


def create_func(labeled_cases: list[LabeledTestCase], model: str):
    def test_example_case(code: str, language: str) -> str:
        language_enum: Lang = str2lang(language)
        source_path = Path(f'{model}{FILE_EXTENSIONS[language_enum]}')
        source_path.write_text(code, encoding='utf-8')
        test = TestRunner(str(source_path), labeled_cases)
        message_for_gpt, _ = render_result_for_GPT(test)
        return message_for_gpt

    def execute_code(input: Optional[str], code: str, language: str) -> str:
        language_enum: Lang = str2lang(language)
        random_name = random.randint(0, 100_000_000)
        source_path = Path(f'tmp{random_name}{FILE_EXTENSIONS[language_enum]}')
        source_path.write_text(code, encoding='utf-8')
        labeled_cases = [LabeledTestCase('case by gpt', TestCase(input or '', ''))]
        test = TestRunner(str(source_path), labeled_cases)
        labeled_result = next(test)
        source_path.unlink(missing_ok=True)
        return labeled_result.result.output

    return test_example_case, execute_code


def solve_problem(path: Path, lang: Lang, model: str) -> None:
    console = Console()
    content = path.read_text(encoding='utf-8')
    html = ProblemHTML(content)
    md = html.make_problem_markdown('en')
    labeled_cases = html.load_labeled_testcase()

    test_example_case, execute_code = create_func(labeled_cases, model)

    # Responses API 形式のツール定義（トップレベル）
    TOOLS = [
        {
            'type': 'function',
            'name': 'test_example_case',
            'description': 'Run the given source code against example test cases and return a summarized result.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'language': {
                        'type': 'string',
                        'enum': [
                            lang.value
                            for lang in (COMPILED_LANGUAGES + INTERPRETED_LANGUAGES)
                        ],
                    },
                },
                'required': ['code', 'language'],
                'additionalProperties': False,
            },
            'strict': True,
        },
        {
            'type': 'function',
            'name': 'execute_code',
            'description': 'Execute the given source code with a single input and return the actual output.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'input': {'type': 'string'},
                    'code': {'type': 'string'},
                    'language': {
                        'type': 'string',
                        'enum': [
                            lang.value
                            for lang in (COMPILED_LANGUAGES + INTERPRETED_LANGUAGES)
                        ],
                    },
                },
                'required': ['input', 'code', 'language'],
                'additionalProperties': False,
            },
            'strict': True,
        },
    ]

    client = OpenAI()
    if set_api_key() is None:
        console.print('[red]OpenAI API key is not set.[/red]')
        return

    system_prompt = f"""You are a competitive programming assistant for {lang.value}.
The user will provide problems in Markdown format.
Read the problem carefully and output a complete, correct, and efficient solution in {lang.value}.
Use standard input and output. Do not omit any code.
Always pay close attention to algorithmic complexity (time and space).
Choose the most optimal algorithms and data structures so that the solution runs within time limits even for the largest possible inputs.

Use the provided tool test_example_case to run the example test cases from the problem statement.
If tests do not pass, fix the code and repeat.
The last tested code will be automatically saved to a local file on the user's computer.
You do not need to include the final source code in your response.
Simply confirm to the user that all tests passed, or briefly explain if they did not.
Once you run test_example_case, the exact code you tested will already be saved locally on the user's machine, so sending it again in the response is unnecessary."""

    # ツール名→ローカル実装のディスパッチ
    tool_impl: Dict[str, Callable[..., Any]] = {
        'test_example_case': test_example_case,
        'execute_code': lambda **p: execute_code(
            p.get('input', ''),  # ← 空なら空文字に
            p.get('code', ''),
            p.get('language', lang.value),
        ),
    }

    console.print(f'Solving :{path} Language: {lang.value} / Model: {model}')

    context_msgs = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': md},
    ]
    turn = 1
    assistant_text = Text()

    def call_model():
        try:
            return client.responses.create(
                model=model,
                input=context_msgs,
                tools=TOOLS,
                tool_choice='auto',
                include=['reasoning.encrypted_content'],
                store=False,
            )
        except BadRequestError as e:
            body = getattr(getattr(e, 'response', None), 'json', lambda: None)()
            console.print(
                Panel.fit(f'{e}\n\n{body}', title='API Error', border_style='red')
            )
            raise

    while True:
        start_time = time.time()
        with Live(
            Panel(
                f'[bold blue]🤔 Thinking... (turn {turn})[/bold blue]\n[dim]Elapsed: 0.0s[/dim]',
                border_style='blue',
            ),
            console=console,
            refresh_per_second=10,
        ) as live:

            def update_timer():
                elapsed = time.time() - start_time
                live.update(
                    Panel(
                        f'[bold blue]🤔 Thinking... (turn {turn})[/bold blue]\n[dim]Elapsed: {elapsed:.1f}s[/dim]',
                        border_style='blue',
                    )
                )

            import threading

            resp = None
            error = None

            def model_call():
                nonlocal resp, error
                try:
                    resp = call_model()
                except Exception as e:
                    error = e

            thread = threading.Thread(target=model_call)
            thread.start()

            while thread.is_alive():
                update_timer()
                time.sleep(0.1)

            thread.join()

            if error:
                raise error

            elapsed = time.time() - start_time
            live.update(
                Panel(
                    f'[bold green]✓ Completed thinking (turn {turn})[/bold green]\n[dim]Time taken: {elapsed:.1f}s[/dim]',
                    border_style='green',
                )
            )

        # Display token usage
        if resp and hasattr(resp, 'usage') and resp.usage:
            usage = resp.usage
            input_tokens = getattr(usage, 'input_tokens', 0)
            output_tokens = getattr(usage, 'output_tokens', 0)
            total_tokens = getattr(usage, 'total_tokens', 0)

            # Check for cached tokens
            cached_tokens = 0
            if hasattr(usage, 'input_tokens_details'):
                details = usage.input_tokens_details
                if hasattr(details, 'cached_tokens'):
                    cached_tokens = details.cached_tokens

            # Check for reasoning tokens
            reasoning_tokens = 0
            if hasattr(usage, 'output_tokens_details'):
                details = usage.output_tokens_details
                if hasattr(details, 'reasoning_tokens'):
                    reasoning_tokens = details.reasoning_tokens

            token_msg = f'[dim]Tokens - Input: {input_tokens:,}'
            if cached_tokens > 0:
                token_msg += f' (cached: {cached_tokens:,})'
            token_msg += f' | Output: {output_tokens:,}'
            if reasoning_tokens > 0:
                token_msg += f' (reasoning: {reasoning_tokens:,})'
            token_msg += f' | Total: {total_tokens:,}[/dim]'
            console.print(token_msg)

        if resp and getattr(resp, 'output_text', None):
            assistant_text.append(resp.output_text)

            output_content = str(resp.output_text).strip()
            if any(
                keyword in output_content
                for keyword in [
                    'def ',
                    'class ',
                    'import ',
                    'from ',
                    '#include',
                    'public class',
                ]
            ):
                try:
                    syntax = Syntax(
                        output_content, lang, theme='monokai', line_numbers=True
                    )
                    console.print(
                        Panel(
                            syntax,
                            title='Assistant Output (Code)',
                            border_style='green',
                        )
                    )
                except Exception:
                    console.print(
                        Panel(
                            assistant_text,
                            title='Assistant Output',
                            border_style='green',
                        )
                    )
            else:
                console.print(
                    Panel(
                        assistant_text, title='Assistant Output', border_style='green'
                    )
                )

        if resp and hasattr(resp, 'output'):
            context_msgs += resp.output

            # function_call を収集
            calls: List[dict] = []
            for o in resp.output:
                if getattr(o, 'type', '') == 'function_call':
                    try:
                        args = json.loads(o.arguments or '{}')
                    except Exception:
                        args = {}
                    call_id = getattr(o, 'call_id', None) or getattr(
                        o, 'id'
                    )  # ★ ここがポイント
                    calls.append({'name': o.name, 'call_id': call_id, 'args': args})
        else:
            calls = []

        if not calls:
            console.print(
                Panel.fit('✅ Done (no more tool calls).', border_style='green')
            )
            break

        # ツールを実行し、function_call_output を context に積む
        for c in calls:
            args_str = json.dumps(c['args'], ensure_ascii=False) if c['args'] else ''
            console.print(
                Panel.fit(
                    f"Tool: [bold]{c['name']}[/bold]\nargs: {args_str}",
                    title=f"function_call ({c['call_id']})",
                    border_style='cyan',
                )
            )

            impl = tool_impl.get(c['name'])
            if not impl:
                out = f"[ERROR] Unknown tool: {c['name']}"
            else:
                try:
                    with console.status(f"Running {c['name']}...", spinner='dots'):
                        out = impl(**c['args']) if c['args'] else impl()
                except TypeError:
                    out = impl(
                        **{
                            k: v
                            for k, v in c['args'].items()
                            if k in impl.__code__.co_varnames
                        }
                    )
                except Exception as e:
                    out = f"[Tool '{c['name']}' error] {e}"

            console.print(
                Panel(
                    str(out) or '(no output)',
                    title=f"{c['name']} result",
                    border_style='magenta',
                )
            )

            context_msgs.append(
                {
                    'type': 'function_call_output',
                    'call_id': c['call_id'],
                    'output': str(out),
                }
            )

        turn += 1


@click.command(short_help=_('cmd_generate'), help=_('cmd_generate'))
@add_file_selector('files', filetypes=[Lang.HTML])
@click.option('--lang', default='Python', help=_('opt_output_lang'))
@click.option('--model', default='gpt-5-mini', help=_('opt_model'))
def ai(files, lang, model):
    """HTMLファイルからコード生成またはテンプレート出力を行います。"""
    lang_enum: Lang = str2lang(lang)
    for path in files:
        solve_problem(Path(path), lang_enum, model)
