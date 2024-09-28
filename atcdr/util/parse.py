import re
from typing import Dict, Iterator, List, Optional

from bs4 import BeautifulSoup as bs
from bs4 import Tag
from markdownify import MarkdownConverter


class HTML:
    def __init__(self, html: str) -> None:
        self.soup = bs(html, 'html.parser')
        self.title = self._get_title()
        self.link = self._find_link()

    def _get_title(self) -> str:
        title_tag = self.soup.title
        return title_tag.string.strip() if title_tag else ''

    def _find_link(self) -> str:
        meta_tag = self.soup.find('meta', property='og:url')
        if isinstance(meta_tag, Tag) and 'content' in meta_tag.attrs:
            content = meta_tag['content']
            if isinstance(content, list):
                return content[0]  # 必要に応じて、最初の要素を返す
            return content
        return ''

    @property
    def html(self) -> str:
        return str(self.soup)

    def __str__(self) -> str:
        return self.html

    def __bool__(self) -> bool:
        return bool(self.html)


class CustomMarkdownConverter(MarkdownConverter):
    def convert_var(self, el, text, convert_as_inline):
        var_text = el.text.strip()
        return f'\\({var_text}\\)'

    def convert_pre(self, el, text, convert_as_inline):
        pre_text = el.text.strip()
        return f'```\n{pre_text}\n```'


class ProblemForm(Tag):
    def find_submit_link(self) -> str:
        action = self['action']
        submit_url = f'https://atcoder.jp{action}'
        return submit_url

    def find_task_screen_name(self) -> str:
        task_input = self.find('input', {'name': 'data.TaskScreenName'})
        task_screen_name = task_input['value']
        return task_screen_name

    def get_languages_options(self) -> Dict[str, int]:
        options: Iterator[Tag] = self.find_all('option')

        options = filter(
            lambda option: 'value' in option.attrs and option['value'].isdigit(),
            options,
        )
        return {option.text.strip(): int(option['value']) for option in options}


class ProblemHTML(HTML):
    def repair_me(self) -> None:
        html = self.html.replace('//img.atcoder.jp', 'https://img.atcoder.jp')
        html = html.replace(
            '<meta http-equiv="Content-Language" content="en">',
            '<meta http-equiv="Content-Language" content="ja">',
        )
        html = html.replace('LANG = "en"', 'LANG="ja"')
        self.soup = bs(html, 'html.parser')

    def abstract_problem_part(self, lang: str) -> Optional[Tag]:
        task_statement = self.soup.find('div', {'id': 'task-statement'})
        if not isinstance(task_statement, Tag):
            return None

        if lang == 'ja':
            lang_class = 'lang-ja'
        elif lang == 'en':
            lang_class = 'lang-en'
        else:
            raise ValueError(f'言語は {lang} に対応していません')
        span = task_statement.find('span', {'class': lang_class})
        return span

    def make_problem_markdown(self, lang: str) -> str:
        title = self.title
        problem_part = self.abstract_problem_part(lang)
        if problem_part is None:
            return ''

        problem_md = CustomMarkdownConverter().convert(str(problem_part))
        problem_md = f'# {title}\n{problem_md}'
        problem_md = re.sub(r'\n\s*\n\s*\n+', '\n\n', problem_md).strip()
        return problem_md

    def load_labeled_testcase(self) -> List:
        from atcdr.test import LabeledTestCase, TestCase

        problem_part = self.abstract_problem_part('en')
        if problem_part is None:
            return []

        sample_inputs = problem_part.find_all(
            'h3', text=re.compile(r'Sample Input \d+')
        )
        ltest_cases = []
        for i, sample_input_section in enumerate(sample_inputs, start=1):
            # 対応する Sample Output を取得
            sample_output_section = problem_part.find('h3', text=f'Sample Output {i}')
            if not sample_input_section or not sample_output_section:
                break

            sample_input_pre = sample_input_section.find_next('pre')
            sample_output_pre = sample_output_section.find_next('pre')

            # 入力と出力をテキスト形式で取得
            sample_input = (
                sample_input_pre.get_text(strip=True)
                if sample_input_pre is not None
                else ''
            )
            sample_output = (
                sample_output_pre.get_text(strip=True)
                if sample_output_pre is not None
                else ''
            )

            ltest_cases.append(
                LabeledTestCase(
                    f'Sample Case {i}', TestCase(sample_input, sample_output)
                )
            )

        return ltest_cases

    @property
    def form(self) -> ProblemForm:
        form = self.soup.find('form', class_='form-code-submit')
        if not isinstance(form, Tag):
            raise ValueError('問題ページにフォームが存在しません')
        form.__class__ = ProblemForm
        return form


def get_username_from_html(html: str) -> str:
    soup = bs(html, 'html.parser')
    script_tags = soup.find_all('script')

    user_screen_name = ''
    for script in script_tags:
        # <script>タグに内容がある場合のみ処理を行う
        if script.string:
            # 正規表現でuserScreenNameの値を抽出
            match = re.search(r'userScreenName\s*=\s*"([^"]+)"', script.string)
            if match:
                user_screen_name = match.group(1)
                break  # 見つかったらループを抜ける

    return user_screen_name


def get_csrf_token(html_content: str) -> str:
    soup = bs(html_content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    return csrf_token if csrf_token else ''


def get_problem_urls_from_tasks(html_content: str) -> list[tuple[str, str]]:
    soup = bs(html_content, 'html.parser')
    table = soup.find('table')
    if not table:
        raise ValueError('問題のテーブルが見つかりませんでした.')

    # tbodyタグを見つける
    tbody = table.find('tbody')
    if not tbody:
        raise ValueError('tbodyが見つかりませんでした.')

    # tbody内の1列目のaタグのリンクと中身を取得
    links = []
    for row in tbody.find_all('tr'):
        first_column = row.find('td')
        a_tag = first_column.find('a')
        if a_tag and 'href' in a_tag.attrs:
            link = 'https://atcoder.jp' + a_tag['href']
            label = a_tag.text.strip()
            links.append((label, link))

    return links


def get_submission_id(html_content: str) -> Optional[int]:
    soup = bs(html_content, 'html.parser')
    first_tr = soup.select_one('tbody > tr')
    data_id_td = first_tr.find(lambda tag: tag.has_attr('data-id'))
    data_id = int(data_id_td['data-id']) if data_id_td else None
    return data_id
