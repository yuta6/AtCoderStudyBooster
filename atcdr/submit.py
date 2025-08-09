import os
import re
import time
from typing import Dict, List, NamedTuple, Optional

import questionary as q
import requests
import rich_click as click
import webview
from bs4 import BeautifulSoup as bs
from rich import print
from rich.live import Live
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.status import Status

from atcdr.login import login
from atcdr.test import (
    ResultStatus,
    TestInformation,
    TestRunner,
    create_renderable_test_info,
)
from atcdr.util.fileops import add_file_selector
from atcdr.util.filetype import (
    COMPILED_LANGUAGES,
    INTERPRETED_LANGUAGES,
    Lang,
    detect_language,
    lang2str,
    str2lang,
)
from atcdr.util.i18n import _
from atcdr.util.parse import ProblemHTML, get_submission_id
from atcdr.util.session import load_session, validate_session


class LanguageOption(NamedTuple):
    id: int
    display_name: str
    lang: Lang


def convert_options_to_langs(options: Dict[str, int]) -> List[LanguageOption]:
    lang_options = []
    for display_name, id_value in options.items():
        lang_name = display_name.split()[
            0
        ].lower()  # 例えば,C++ 23 (Clang 16.0.6)から「c++」を取り出す
        try:
            lang = str2lang(lang_name)
        except KeyError:
            continue
        lang_options.append(
            LanguageOption(id=id_value, display_name=display_name, lang=lang)
        )

    return lang_options


def choose_langid_interactively(lang_dict: dict, lang: Lang) -> int:
    options = convert_options_to_langs(lang_dict)
    options = [*filter(lambda option: option.lang == lang, options)]

    langid = q.select(
        message=_('select_implementation', lang2str(lang)),
        qmark='',
        pointer='❯❯❯',
        choices=[
            q.Choice(title=f'{option.display_name}', value=option.id)
            for option in options
        ],
        instruction='\n ' + _('navigate_with_arrows'),
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

    return langid


def post_source(source_path: str, url: str, session: requests.Session) -> Optional[str]:
    with open(source_path, 'r') as f:
        source = f.read()

    problem_html = session.get(url).text
    problem = ProblemHTML(problem_html)
    lang_dict = problem.form.get_languages_options()
    lang = detect_language(source_path)
    langid = choose_langid_interactively(lang_dict, lang)

    api = type('API', (), {'html': None, 'url': None})()
    window = webview.create_window(
        'AtCoder Submit', url, js_api=api, width=800, height=600, hidden=False
    )

    def on_loaded():
        current = window.get_current_url()

        if current != url:
            dom = window.evaluate_js('document.documentElement.outerHTML')
            api.html = dom
            api.url = current
            window.destroy()
        else:
            safe_src = source.replace('\\', '\\\\').replace('`', '\\`')
            inject_js = f"""
            (function() {{
                // Populate ACE editor
                var ed = ace.edit('editor');
                ed.setValue(`{safe_src}`, -1);
                // Sync to hidden textarea
                document.getElementById('plain-textarea').value = ed.getValue();
                // Select language
                var sel = document.querySelector('select[name=\"data.LanguageId\"]');
                sel.value = '{langid}'; sel.dispatchEvent(new Event('change', {{ bubbles: true }}));

                // CloudFlare Turnstile handling
                var cf = document.querySelector('input[name=\"cf-turnstile-response\"]');
                if (cf) {{
                    // observe token and submit when ready
                    new MutationObserver(function() {{
                        if (cf.value) {{ document.getElementById('submit').click(); }}
                    }}).observe(cf, {{ attributes: true }});
                }} else {{
                    // no Turnstile present, submit immediately
                    document.getElementById('submit').click();
                }}
            }})();
            """
            window.evaluate_js(inject_js)

    window.events.loaded += on_loaded

    with Status(_('solve_captcha'), spinner='circleHalves'):
        webview.start(private_mode=False)

    if 'submit' in api.url:
        print('[red][-][/red] ' + _('submission_failed'))
        return None
    elif 'submissions' in api.url:
        submission_id = get_submission_id(api.html)
        if not submission_id:
            print('[red][-][/red] ' + _('submission_id_not_found'))
            return None

        url = api.url.replace('/me', f'/{submission_id}')
        print('[green][+][/green] ' + _('submission_success'))
        print(_('submission_details', submission_id, url))
        return url + '/status/json'
    else:
        print('[red][-][/red] ' + _('submission_failed'))
        return None


class SubmissionStatus(NamedTuple):
    status: ResultStatus
    current: Optional[int]
    total: Optional[int]
    is_finished: bool


def parse_submission_status_json(data: Dict) -> SubmissionStatus:
    html_content = data.get('Html', '')
    interval = data.get('Interval', None)

    soup = bs(html_content, 'html.parser')
    span = soup.find('span', {'class': 'label'})
    status_text = span.text.strip()

    current, total = None, None
    is_finished = interval is None

    match = re.search(r'(\d+)/(\d+)', status_text)
    if match:
        current = int(match.group(1))
        total = int(match.group(2))

    status_mapping = {
        'AC': ResultStatus.AC,
        'WA': ResultStatus.WA,
        'TLE': ResultStatus.TLE,
        'MLE': ResultStatus.MLE,
        'RE': ResultStatus.RE,
        'CE': ResultStatus.CE,
        'WJ': ResultStatus.WJ,
    }
    status = next(
        (status_mapping[key] for key in status_mapping if key in status_text),
        ResultStatus.WJ,
    )

    return SubmissionStatus(
        status=status, current=current, total=total, is_finished=is_finished
    )


def print_status_submission(
    api_url: str,
    path: str,
    session: requests.Session,
) -> None:
    progress = Progress(
        SpinnerColumn(style='white', spinner_name='circleHalves'),
        TextColumn('{task.description}'),
        SpinnerColumn(style='white', spinner_name='simpleDots'),
        BarColumn(),
    )

    with Status(_('waiting_judge'), spinner='dots'):
        for i in range(15):
            time.sleep(1)
            data = session.get(api_url).json()
            status = parse_submission_status_json(data)
            if status.total or status.current:
                break
        else:
            print('[red][-][/] ' + _('judge_timeout'))
            return

    total = status.total or 0
    task_id = progress.add_task(description=_('judging'), total=total)

    test_info = TestInformation(
        lang=detect_language(path),
        sourcename=path,
        case_number=total,
    )

    with Live(create_renderable_test_info(test_info, progress)) as live:
        current = 0
        while not status.is_finished:
            time.sleep(1)
            data = session.get(api_url).json()
            status = parse_submission_status_json(data)
            current = status.current or current or 0

            test_info.summary = status.status
            test_info.results = [ResultStatus.AC] * current

            progress.update(task_id, completed=current)
            live.update(create_renderable_test_info(test_info, progress))

        test_info.summary = status.status
        test_info.results = [ResultStatus.AC] * total

        progress.update(task_id, description=_('judge_completed'), completed=total)
        live.update(create_renderable_test_info(test_info, progress))


def submit_source(path: str, no_test: bool, no_feedback: bool) -> None:
    session = load_session()
    if not validate_session(session):
        print('[red][-][/] ' + _('not_logged_in'))
        login()
        if not validate_session(session):
            print('[red][-][/] ' + _('login_failed'))
            return

    html_files = [file for file in os.listdir('.') if file.endswith('.html')]
    if not html_files:
        print(_('problem_file_not_found'))
        return

    with open(html_files[0], 'r') as file:
        problem = ProblemHTML(file.read())

    lcases = problem.load_labeled_testcase()
    url = problem.link

    test = TestRunner(path, lcases)
    list(test)
    print(create_renderable_test_info(test.info))

    if test.info.summary != ResultStatus.AC and not no_test:
        print('[red][-][/] ' + _('sample_not_ac'))
        return

    api_status_link = post_source(path, url, session)
    if api_status_link is None:
        return

    if not no_feedback:
        print_status_submission(api_status_link, path, session)


@click.command(short_help=_('cmd_submit'), help=_('cmd_submit'))
@add_file_selector('files', filetypes=COMPILED_LANGUAGES + INTERPRETED_LANGUAGES)
@click.option('--no-test', is_flag=True, default=False, help=_('opt_no_test'))
@click.option('--no-feedback', is_flag=True, default=False, help=_('opt_no_feedback'))
def submit(files, no_test, no_feedback):
    """指定したファイルをAtCoderへ提出します。"""
    for path in files:
        submit_source(path, no_test, no_feedback)
