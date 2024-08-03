from enum import Enum
from typing import Optional

from bs4 import BeautifulSoup as bs


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
