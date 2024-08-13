import webbrowser

from atcdr.util.filename import Lang, execute_files
from atcdr.util.problem import find_link_from_html


def open_html(file: str) -> None:
	try:
		with open(file, 'r') as f:
			html_content = f.read()
	except FileNotFoundError:
		print(f"HTMLファイル '{file}' が見つかりません。")
		return

	url = find_link_from_html(html_content)
	if url:
		webbrowser.open(url)
	else:
		print('URLが見つかりませんでした。')


def open_files(*args: str) -> None:
	execute_files(*args, func=open_html, target_filetypes=[Lang.HTML])
