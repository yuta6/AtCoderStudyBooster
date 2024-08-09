import re
from enum import Enum
from typing import Optional

from bs4 import BeautifulSoup as bs
from markdownify import MarkdownConverter


# TODO : そのうちgenerate.pyやtest.py, open.pyのHTMLのparse処理を全部まとめる
class Lang(Enum):
    JA = "ja"
    EN = "en"


class ProblemStruct:
    def __init__(self) -> None:
        self.problem_part: Optional[str] = None
        self.condition_part: Optional[str] = None
        self.io_part: Optional[str] = None
        self.test_part: Optional[list[str]] = None

    def divide_problem_part(self, task_statement: bs) -> None:
        parts = task_statement.find_all("div", {"class": "part"})

        self.problem_part = str(parts[0])
        self.condition_part = str(parts[1])

        io_div = task_statement.find("div", {"class": "io-style"})
        io_parts = io_div.find_all("div", {"class": "part"})

        # 指定したdiv内の1つ目のclass="part"のdivをio_partに格納する
        self.io_part = io_parts[0]
        # 指定したdiv内の2つ目以降のclass="part"のdivをtest_partのリストに格納する


class CustomMarkdownConverter(MarkdownConverter):
    def convert_var(self, el, text, convert_as_inline):
        var_text = el.text.strip()
        return f"\\({var_text}\\)"

    def convert_pre(self, el, text, convert_as_inline):
        pre_text = el.text.strip()
        return f"```\n{pre_text}\n```"


def custom_markdownify(html, **options):
    return CustomMarkdownConverter(**options).convert(html)


def remove_unnecessary_emptylines(md_text):
    md_text = re.sub(r"\n\s*\n\s*\n+", "\n\n", md_text)
    md_text = md_text.strip()
    return md_text


def abstract_problem_part(html_content: str, lang: str) -> str:
    soup = bs(html_content, "html.parser")
    task_statement = soup.find("div", {"id": "task-statement"})
    if lang == "ja":
        lang_class = "lang-ja"
    elif lang == "en":
        lang_class = "lang-en"
    else:
        pass
    span = task_statement.find("span", {"class": lang_class})
    return str(span)


def make_problem_markdown(html_content: str, lang: str) -> str:
    problem_part = abstract_problem_part(html_content, lang)
    problem_md = custom_markdownify(problem_part)
    problem_md = remove_unnecessary_emptylines(problem_md)
    return problem_md
