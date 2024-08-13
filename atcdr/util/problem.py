import re
from enum import Enum
from typing import Match, Optional

from bs4 import BeautifulSoup as bs
from bs4 import Tag
from markdownify import MarkdownConverter  # type: ignore


def repair_html(html: str) -> str:
	html = html.replace('//img.atcoder.jp', 'https://img.atcoder.jp')
	html = html.replace(
		'<meta http-equiv="Content-Language" content="en">',
		'<meta http-equiv="Content-Language" content="ja">',
	)
	html = html.replace('LANG = "en"', 'LANG="ja"')
	return html


def get_title_from_html(html: str) -> str:
	title_match: Optional[Match[str]] = re.search(
		r'<title>(?:.*?-\s*)?([^<]*)</title>', html, re.IGNORECASE | re.DOTALL
	)
	if title_match:
		title: str = title_match.group(1).replace(' ', '')
		title = re.sub(r'[\\/*?:"<>| ]', '', title)
		return title
	return ''


def find_link_from_html(html: str) -> str:
	soup = bs(html, 'html.parser')
	meta_tag = soup.find('meta', property='og:url')
	if isinstance(meta_tag, Tag) and 'content' in meta_tag.attrs:
		content = meta_tag['content']
		if isinstance(content, list):
			return content[0]  # 必要に応じて、最初の要素を返す
		return content
	return ''


class Lang(Enum):
	JA = 'ja'
	EN = 'en'


class CustomMarkdownConverter(MarkdownConverter):
	def convert_var(self, el, text, convert_as_inline):
		var_text = el.text.strip()
		return f'\\({var_text}\\)'

	def convert_pre(self, el, text, convert_as_inline):
		pre_text = el.text.strip()
		return f'```\n{pre_text}\n```'


def custom_markdownify(html, **options):
	return CustomMarkdownConverter(**options).convert(html)


def remove_unnecessary_emptylines(md_text):
	md_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', md_text)
	md_text = md_text.strip()
	return md_text


def abstract_problem_part(html_content: str, lang: str) -> str:
	soup = bs(html_content, 'html.parser')
	task_statement = soup.find('div', {'id': 'task-statement'})

	if not isinstance(task_statement, Tag):
		return ''

	if lang == 'ja':
		lang_class = 'lang-ja'
	elif lang == 'en':
		lang_class = 'lang-en'
	else:
		pass
	span = task_statement.find('span', {'class': lang_class})
	return str(span)


def make_problem_markdown(html_content: str, lang: str) -> str:
	problem_part = abstract_problem_part(html_content, lang)
	problem_md = custom_markdownify(problem_part)
	problem_md = remove_unnecessary_emptylines(problem_md)
	return problem_md
