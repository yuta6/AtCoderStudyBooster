import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import requests

class Diff(Enum):
    A = 'a'
    B = 'b'
    C = 'c'
    D = 'd'
    E = 'e'
    F = 'f'

@dataclass
class Problem:
    number: int
    difficulty: Diff

def get_problem_html(problem: Problem) -> Optional[str]:
    url = f"https://atcoder.jp/contests/abc{problem.number}/tasks/abc{problem.number}_{problem.difficulty.value}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"[Error] abc{problem.number} {problem.difficulty.value}に対応するHTMLファイルをみつけられたません")
        return None

def repair_html(html: str) -> str:
    html=html.replace('//img.atcoder.jp', 'https://img.atcoder.jp')
    html=html.replace('<meta http-equiv="Content-Language" content="en">' ,'<meta http-equiv="Content-Language" content="ja">')
    html=html.replace('LANG = "en"', 'LANG="ja"')
    return html

def mkdir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[+] フォルダー: {path} を作成しました")

def generate_problem_directory(base_path: str, problems: List[Problem]) -> None:
    for problem in problems:
        # ディレクトリパスを生成
        dir_path = os.path.join(base_path, problem.difficulty.name, str(problem.number))
        
        # 問題のHTMLを取得して修正
        html = get_problem_html(problem)
        if html:
            mkdir(dir_path)
            repaired_html = repair_html(html)
            
            # ファイルパスを生成して保存
            title = re.search(r'<title>(?:.*?-\s*)?([^<]*)</title>', repaired_html, re.IGNORECASE | re.DOTALL)
            if title:
                title = title.group(1).replace(" ", "")
                title = re.sub(r'[\\/*?:"<>| ]', '', title)
            else:
                title = f"problem{problem.number}"
                print("[Error] タイトルが取得できませんでした")
            file_path = os.path.join(dir_path, f"{title}.html")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(repaired_html)
            print(f"[+] 問題を保存しました :{file_path}")

def main() :
    print("At Coderの問題のHTMLファイルをダウンロードします")
    print("""
    1. 番号の範囲を指定してダウンロードする
    2. 1ファイルだけダウンロードする
    q: 終了
          """)

    choice = input("選択してください: ")

    if choice == '1':
        start_end = input("開始と終了のコンテストの番号をスペースで区切って指定してください (例: 223 230): ")
        start, end = map(int, start_end.split(' '))
        difficulty = Diff[input("ダウンロードする問題の難易度を指定してください (例: a, b, c): ").upper()]
        problem_list = [Problem(number, difficulty) for number in range(start, end + 1)]
        generate_problem_directory(".", problem_list)
    elif choice == '2':
        number = int(input("コンテストの番号を指定してください: "))
        difficulty = Diff[input("ダウンロードする問題の難易度を指定してください (例: a, b, c): ").upper()]
        generate_problem_directory(".", [Problem(number, difficulty)])
    elif choice == 'q':
        print("終了します")
    else:
        print("無効な選択です")

if __name__ == "__main__":
    main()
