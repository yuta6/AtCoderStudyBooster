import tiktoken
import yfinance as yf

GPT4o_Input_Rate = 5/1000**2
GPT4o_Output_Rate = 15/1000**2 

COST_TYPE_INPUT = "input"
COST_TYPE_OUTPUT = "output"

def count_tokens(text: str) -> int:
    gpt4o_model = tiktoken.encoding_for_model("gpt-4o")
    gpt4_model = tiktoken.encoding_for_model("gpt-4")
    print(f"{gpt4o_model.name} : {len(gpt4o_model.encode(text))}, {gpt4_model.name} : {len(gpt4_model.encode(text))}")

import tiktoken
import yfinance as yf

# グローバル定数の定義
COST_TYPE_INPUT = "input"
COST_TYPE_OUTPUT = "output"

# トークンレート (USD)
GPT4o_Input_Rate = 5 / 1000**2
GPT4o_Output_Rate = 15 / 1000**2

class CalcApiCost:
    def __init__(self, text: str, cost_type: str) -> None:
        self._text = text
        self._cost_type = cost_type

        # 為替レートを取得
        ticker = yf.Ticker("JPY=X")
        self._exchange_rate = ticker.history(period="1d")['Close'].iloc[0]
        
        # トークンモデルを取得
        self._gpt4o_model = tiktoken.encoding_for_model("gpt-4o")

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text: str):
        self._text = new_text
        self._calculate_cost()

    @property
    def cost_type(self):
        return self._cost_type

    @cost_type.setter
    def cost_type(self, new_cost_type: str):
        if new_cost_type not in [COST_TYPE_INPUT, COST_TYPE_OUTPUT]:
            raise ValueError("Invalid cost type. Choose 'input' or 'output'.")
        self._cost_type = new_cost_type
        self._calculate_cost()

    @property
    def usd(self):
        self._calculate_cost()
        return self._usd

    @property
    def jpy(self):
        self._calculate_cost()
        return self._jpy

    def _calculate_cost(self):
        self._token_count = len(self._gpt4o_model.encode(self._text))

        if self._cost_type == COST_TYPE_INPUT:
            cost_usd = self._token_count * GPT4o_Input_Rate
        elif self._cost_type == COST_TYPE_OUTPUT:
            cost_usd = self._token_count * GPT4o_Output_Rate

        self._usd = cost_usd
        self._jpy = cost_usd * self._exchange_rate

    def __str__(self) -> str:
        return f"token count: {self._token_count} \n{self.cost_type} cost: ${self.usd} {self.jpy}円"
    
    def __repr__(self) -> str:
        return f"calc_api_cost({self.text},{self.cost_type})"
    

def main():
    text=f"""
    抽象クラスを実装するメリットは、抽象クラスの特徴１に書いた、"抽象クラスを継承したサブクラスは、抽象クラスにある抽象メソッドを必ずオーバーライドしなければならない" です。

    これが意味する具体的なメリットは、、、
    複数人で開発を行う場合に実装レベルのルールを作れる！ です。
    そう言われてもこのメリットは、企業での大規模開発を経験してみないと正直わからないと思います。（私は、さっぱりわかりませんでした:umbrella:）

    では、ここで大規模開発（複数人で開発を行なっていて、コードの量は数千〜数十万行に及ぶような開発）を行なっているとして、単純な機能追加や画面追加によるプログラムの修正が必要になったとしましょう。

    単純な機能追加の場合、メソッドのロジックは少し違えど、やりたいことは既に実装しているクラスと大体処理が同じ場合が多々あります。そんな場合、同じような処理をしているのにクラスによってメソッド名が異なると、何の処理をしているのか把握するのに時間がかかってしまったりします:pensive:

    それが、抽象クラスの特徴である強制的なオーバーライドにより、必ず書かなければいけないようにすることで、以下のような効果が得られます:sparkles::sparkles:

    メソッド名を統一し、ロジックを共通化し、大体何の処理をしているか把握しやすくなる
    共通の処理をいちいち全てのクラスに書き込む必要がなくなり、個別の処理も追加しやすくもなる
    開発者がサブクラスを定義した際に、メソッドの実装忘れやメソッド名に間違いがあればコンパイルエラーが起き、コーディングミスを防ぐ
    抽象クラスを実装すると、このように複数人で開発を行う場合に実装レベルのルールを作れる のです！！
    これが抽象クラスを実装する意図であり理由の1つです。

    それでは、次に抽象クラスを用いるデザインパターンとサンプルプログラムを紹介します。
    """
    print(CalcApiCost(text, COST_TYPE_INPUT))
if __name__ == "__main__":
    main()