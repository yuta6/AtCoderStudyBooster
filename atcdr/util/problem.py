import time
from dataclasses import dataclass

import requests

from atcdr.util.parse import get_problem_urls_from_tasks


class Contest:
    def __init__(self, name: str, session: requests.Session):
        if not name:
            raise ValueError('nameは必須です')
        self.name = name

        self.url = f'https://atcoder.jp/contests/{name}/tasks'
        retry_attempts = 2
        retry_wait = 0.30
        for _ in range(retry_attempts):
            response = session.get(self.url)
            if response.ok:
                break
            else:
                time.sleep(retry_wait)

        self.problems = [
            Problem(url=url, contest=self, label=label)
            for label, url in get_problem_urls_from_tasks(response.text)
        ]

    def __str__(self) -> str:
        return f'{self.name}'

    def __repr__(self) -> str:
        return f'Contest(name={self.name})'


@dataclass
class Problem:
    url: str
    contest: Contest
    label: str

    def __str__(self) -> str:
        return f'{self.label} - {self.contest.name}'

    def __repr__(self) -> str:
        return f'Problem(url={self.url}, contest={self.contest}, label={self.label})'
