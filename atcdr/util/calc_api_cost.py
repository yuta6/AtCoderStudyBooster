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

class calc_api_cost:
    def __init__(self, text: str, cost_type: str) -> None:
        self.text = text
        self.cost_type = cost_type

        ticker = yf.Ticker("JPY=X")
        exchange_rate = ticker.history(period="1d")['Close'].iloc[0]
        gpt4o_model = tiktoken.encoding_for_model("gpt-4o")
        self.token_count = len(gpt4o_model.encode(self.text))

        if self.cost_type == COST_TYPE_INPUT:
            cost_usd = self.token_count * GPT4o_Input_Rate
        elif self.cost_type == COST_TYPE_OUTPUT:
            cost_usd = self.token_count * GPT4o_Output_Rate
        else:
            raise ValueError("Invalid cost type. Choose 'input' or 'output'.")
        
        self.usd = cost_usd
        self.jpy = cost_usd * exchange_rate

    def __str__(self) -> str:
        return f"token count: {self.token_count} \n{self.cost_type} cost: ${self.usd} {self.jpy}円"
    
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
    print(calc_api_cost(text, COST_TYPE_INPUT))
if __name__ == "__main__":
    main()