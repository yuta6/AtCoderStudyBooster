from dataclasses import dataclass

import requests

from atcdr.util.parse import get_problem_urls_from_tasks


class Contest:
    def __init__(self, name: str, session: requests.Session):
        if not name:
            raise ValueError('nameは必須です')
        self.name = name

        self.url = f'https://atcoder.jp/contests/{name}/tasks'
        response = session.get(self.url)
        if not response.ok:
            raise ValueError(f'コンテストの {name} のURL見つかりません')

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
