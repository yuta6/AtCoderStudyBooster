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
    html = remove_unnecessary_emptylines(html)
    return html


def get_title_from_html(html: str) -> str:
    title: Optional[Match[str]] = re.search(r'<title>([^<]*)</title>', html)
    return title.group(1).strip() if title else ''


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


def title_to_filename(title: str) -> str:
    title = re.sub(r'[\\/*?:"<>| !@#$%^&()+=\[\]{};,\']', '', title)
    title = re.sub(r'.*?-', '', title)
    return title


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


def remove_unnecessary_emptylines(text):
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = text.strip()
    return text


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
    title = get_title_from_html(html_content)
    problem_part = abstract_problem_part(html_content, lang)
    problem_md = custom_markdownify(problem_part)
    problem_md = f'# {title}\n{problem_md}'
    problem_md = remove_unnecessary_emptylines(problem_md)
    return problem_md


def get_csrf_token(html_content: str) -> str:
    soup = bs(html_content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    return csrf_token if csrf_token else ''


def get_problem_url_from_tasks(html_content: str) -> list[tuple[str, str]]:
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
