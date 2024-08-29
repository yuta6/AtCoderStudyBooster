import webbrowser  # noqa: I001
from rich.panel import Panel
from rich.console import Console

from atcdr.util.filetype import Lang
from atcdr.util.execute import execute_files
from atcdr.util.problem import find_link_from_html


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

	url = find_link_from_html(html_content)
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


def open_files(*args: str) -> None:
	execute_files(*args, func=open_html, target_filetypes=[Lang.HTML])
