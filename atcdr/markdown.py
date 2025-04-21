import os

import rich_click as click
from rich.console import Console
from rich.markdown import Markdown

from atcdr.util.fileops import add_file_selector
from atcdr.util.filetype import FILE_EXTENSIONS, Lang
from atcdr.util.parse import ProblemHTML


def save_markdown(html_path: str, lang: str) -> None:
    console = Console()
    with open(html_path, 'r', encoding='utf-8') as f:
        html = ProblemHTML(f.read())
    md = html.make_problem_markdown(lang)
    file_without_ext = os.path.splitext(html_path)[0]
    md_path = file_without_ext + FILE_EXTENSIONS[Lang.MARKDOWN]

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)
        console.print('[green][+][/green] Markdownファイルを作成しました.')


def print_markdown(html_path: str, lang: str) -> None:
    console = Console()
    with open(html_path, 'r', encoding='utf-8') as f:
        html = ProblemHTML(f.read())
    md = html.make_problem_markdown(lang)
    console.print(Markdown(md))


@click.command(short_help='Markdown形式で問題を表示します')
@add_file_selector('files', filetypes=[Lang.HTML])
@click.option('--lang', default='ja', help='出力する言語を指定')
@click.option('--save', is_flag=True, help='変換結果をファイルに保存')
def markdown(files, lang, save):
    """Markdown形式で問題を表示します"""
    for path in files:
        if save:
            save_markdown(path, lang)
        else:
            print_markdown(path, lang)
