from atcdr.util.filename import FileExtension, Filename, execute_files
from atcdr.util.gpt import ChatGPT, set_api_key
from atcdr.util.problem import make_problem_markdown


def solve_problem(file: Filename, lang: str) -> None:

    with open(file, "r") as f:
        html_content = f.read()
    html_content


def generate_code(file: Filename, lang: str) -> None:

    with open(file, "r") as f:
        html_content = f.read()
    if set_api_key():
        return
    ChatGPT(
        system_prompt="You are a genius programmer. Your job is to generate the correct code for the problem.",
    )
    html_content


def generate_template(file: Filename, lang: str) -> None:

    with open(file, "r") as f:
        html_content = f.read()
    md = make_problem_markdown(html_content, "en")
    md


def generate(
    *source: str,
    lang: str = "python",
    without_test: bool = False,
    template: bool = False
) -> None:

    if template:
        execute_files(
            *source,
            func=lambda file: generate_template(file, lang),
            target_filetypes=[FileExtension.HTML]
        )
    elif without_test:
        execute_files(
            *source,
            func=lambda file: generate_code(file, lang),
            target_filetypes=[FileExtension.HTML]
        )
    else:
        execute_files(
            *source,
            func=lambda file: solve_problem(file, lang),
            target_filetypes=[FileExtension.HTML]
        )

    # 適切なプロンプトを作成してGPTに与える

    # GPTからの返答に対して解答ファイルを作成する

    # 解答ファイルをテストする

    # テスト結果をパスした場合はパスしたファイルを保存する
    # しなかった場合は, その結果をプロンプトに与えて,再度ファイルをGPTに解答ファイルをつくってもらう

    pass
