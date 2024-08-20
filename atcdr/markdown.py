import os

from rich.console import Console
from rich.markdown import Markdown

from atcdr.util.execute import execute_files
from atcdr.util.filetype import FILE_EXTENSIONS, Lang
from atcdr.util.problem import make_problem_markdown


def save_markdown(html_path: str, lang: str) -> None:
	console = Console()
	with open(html_path, 'r', encoding='utf-8') as f:
		html = f.read()
	md = make_problem_markdown(html, lang)
	file_without_ext = os.path.splitext(html_path)[0]
	md_path = file_without_ext + FILE_EXTENSIONS[Lang.MARKDOWN]

	with open(md_path, 'w', encoding='utf-8') as f:
		f.write(md)
		console.print('[green][+][/green] Markdownファイルを作成しました.')


def print_markdown(md_path: str) -> None:
	console = Console()
	with open(md_path, 'r', encoding='utf-8') as f:
		md = f.read()
	console.print(Markdown(md))


def markdown(*args: str, lang: str = 'ja', save: bool = False) -> None:
	if save:
		execute_files(
			*args,
			func=lambda html_path: save_markdown(html_path, lang),
			target_filetypes=[Lang.HTML],
		)
	else:
		execute_files(*args, func=print_markdown, target_filetypes=[Lang.MARKDOWN])
