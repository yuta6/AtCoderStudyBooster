import webbrowser

from bs4 import BeautifulSoup as bs
from bs4.element import Tag

from atcdr.util.filename import Lang, execute_files


def find_link_from(html: str) -> str | None:
	soup = bs(html, 'html.parser')
	meta_tag = soup.find('meta', property='og:url')
	if isinstance(meta_tag, Tag) and 'content' in meta_tag.attrs:
		content = meta_tag['content']
		if isinstance(content, list):
			return content[0]  # 必要に応じて、最初の要素を返す
		return content
	return None


def open_html(file: str) -> None:
	try:
		with open(file, 'r') as f:
			html_content = f.read()
	except FileNotFoundError:
		print(f"HTMLファイル '{file}' が見つかりません。")
		return

	url = find_link_from(html_content)
	if url:
		webbrowser.open(url)
	else:
		print('URLが見つかりませんでした。')


def open_files(*args: str) -> None:
	execute_files(*args, func=open_html, target_filetypes=[Lang.HTML])
