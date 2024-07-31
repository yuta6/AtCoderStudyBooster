from atcdr.util.operate_gpt import ChatGPT, set_api_key


class ProblemStruct:
    def __init__(self) -> None:
        self.problem_block = None
        self.condition_block = None
        self.test_block = None

    def parse_html(self) -> None:
        pass


# ChatGPTクラスを利用して競技プログラムの問題を解く
# generateのオプション --with-no-test
# atcdr generate
def generate() -> None:

    if set_api_key():
        return
    ChatGPT(
        system_prompt="You are a genius programmer. Your job is to generate the correct code for the problem.",
    )

    # カレントディレクトリの問題文のHTMLファイルを読み込む

    # 読み込んだHTMLファイルをparseして3つの情報を取得する
    # 問題文, 変数の制約, テストケース

    # 適切なプロンプトを作成してGPTに与える

    # GPTからの返答に対して解答ファイルを作成する

    # 解答ファイルをテストする

    # テスト結果をパスした場合はパスしたファイルを保存する
    # しなかった場合は, その結果をプロンプトに与えて,再度ファイルをGPTに解答ファイルをつくってもらう

    pass
