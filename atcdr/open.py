import webbrowser  # noqa: I001
from rich.panel import Panel
from rich.console import Console

from atcdr.util.filetype import Lang
from atcdr.util.fileops import add_file_selector
import rich_click as click
from atcdr.util.parse import ProblemHTML


def open_html(file: str) -> None:
    console = Console()
    try:
        with open(file, 'r') as f:
            html_content = f.read()
    except FileNotFoundError:
        console.print(
            Panel(
                f"{file}' [red]が見つかりません[/]",
                border_style='red',
            )
        )
        return

    url = ProblemHTML(html_content).link
    if url:
        webbrowser.open_new_tab(url)
        console.print(
            Panel(
                f'[green]URLを開きました[/] {url}',
                border_style='green',
            )
        )
    else:
        console.print(
            Panel(
                f'{file} [yellow]にURLが見つかりませんでした[/]',
                border_style='yellow',
            )
        )


@click.command(short_help='HTMLファイルを開く')
@add_file_selector('files', filetypes=[Lang.HTML])
def open_files(files):
    """指定したHTMLファイルをブラウザで開きます。"""
    for path in files:
        open_html(path)
