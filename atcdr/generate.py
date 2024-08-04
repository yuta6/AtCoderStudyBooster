import re

from bs4 import BeautifulSoup as bs
from markdownify import MarkdownConverter

from atcdr.util.gpt import ChatGPT, set_api_key


class CustomMarkdownConverter(MarkdownConverter):

    def convert_var(self, el, text, convert_as_inline):
        var_text = el.text.strip()
        return f"\\({var_text}\\)"

    def convert_pre(self, el, text, convert_as_inline):
        pre_text = el.text.strip()
        return f"```\n{pre_text}\n```"


def custom_markdownify(html, **options):
    return CustomMarkdownConverter(**options).convert(html)


def remove_unnecessary_newlines(md_text):
    md_text = re.sub(r"\n\s*\n\s*\n+", "\n\n", md_text)
    md_text = md_text.strip()
    return md_text


def make_problem_markdown(html_content: str, lang: str) -> str:
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


# ChatGPTクラスを利用して競技プログラムの問題を解く
# generateのオプション --with-no-test
# atcdr generate
def generate(*args: str, without_test: bool = False) -> None:

    if set_api_key():
        return
    ChatGPT(
        system_prompt="You are a genius programmer. Your job is to generate the correct code for the problem.",
    )

    # カレントディレクトリの問題文のHTMLファイルを読み込む
    # open.pyと似たロジックなのでコンポーネント化したい。

    # 適切なプロンプトを作成してGPTに与える

    # GPTからの返答に対して解答ファイルを作成する

    # 解答ファイルをテストする

    # テスト結果をパスした場合はパスしたファイルを保存する
    # しなかった場合は, その結果をプロンプトに与えて,再度ファイルをGPTに解答ファイルをつくってもらう

    pass
