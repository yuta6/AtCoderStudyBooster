import time
from dataclasses import dataclass
from enum import Enum

from rich import print

from atcdr.util.session import load_session


class Diff(Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    G = 'G'


@dataclass
class Problem:
    number: int
    difficulty: Diff


class ProblemDownloader:
    def __init__(self) -> None:
        self.session = load_session()

    def get(self, problem: Problem) -> str:
        url = f'https://atcoder.jp/contests/abc{problem.number}/tasks/abc{problem.number}_{problem.difficulty.value.lower()}'
        session = self.session
        retry_attempts = 3
        retry_wait = 1  # 1 second

        for _ in range(retry_attempts):
            response = session.get(url)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                print(
                    f'[bold yellow][Error {response.status_code}][/bold yellow] 再試行します。abc{problem.number} {problem.difficulty.value}'
                )
                time.sleep(retry_wait)
            elif 300 <= response.status_code < 400:
                print(
                    f'[bold yellow][Error {response.status_code}][/bold yellow] リダイレクトが発生しました。abc{problem.number} {problem.difficulty.value}'
                )
            elif 400 <= response.status_code < 500:
                print(
                    f'[bold red][Error {response.status_code}][/bold red] 問題が見つかりません。abc{problem.number} {problem.difficulty.value}'
                )
                break
            elif 500 <= response.status_code < 600:
                print(
                    f'[bold red][Error {response.status_code}][/bold red] サーバーエラーが発生しました。abc{problem.number} {problem.difficulty.value}'
                )
                break
            else:
                print(
                    f'[bold red][Error {response.status_code}][/bold red] abc{problem.number} {problem.difficulty.value}に対応するHTMLファイルを取得できませんでした。'
                )
                break
        return ''
