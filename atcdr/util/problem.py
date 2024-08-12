import re
from enum import Enum
from typing import Optional, Union

from bs4 import BeautifulSoup as bs
from bs4 import NavigableString, Tag
from markdownify import MarkdownConverter  # type: ignore


# TODO : そのうちgenerate.pyやtest.py, open.pyのHTMLのparse処理を全部まとめる
class Lang(Enum):
	JA = 'ja'
	EN = 'en'


class ProblemStruct:
	def __init__(self) -> None:
		self.problem_part: Optional[str] = None
		self.condition_part: Optional[str] = None
		self.io_part: Optional[str] = None
		self.test_part: Optional[list[str]] = None

	def divide_problem_part(self, task_statement: Union[Tag, NavigableString]) -> None:
		if not isinstance(task_statement, Tag):
			return

		parts = task_statement.find_all('div', {'class': 'part'})

		if len(parts) >= 2:
			self.problem_part = str(parts[0])
			self.condition_part = str(parts[1])

		io_div = task_statement.find('div', {'class': 'io-style'})
		if isinstance(io_div, Tag):
			io_parts = io_div.find_all('div', {'class': 'part'})

			if len(io_parts) > 0:
				self.io_part = str(
					io_parts[0]
				)  # .find_all() はリストを返すので、str()でキャスト

			# 2つ目以降のdivをtest_partに格納
			self.test_part = [str(part) for part in io_parts[1:]]


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
