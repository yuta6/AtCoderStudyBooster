from typing import List, Optional

import requests

from atcdr.util.parse import get_problem_urls_from_tasks


class Contest:
    def __init__(self, name: str, number: Optional[int] = None):
        if not name:
            raise ValueError('nameは必須です')
        self._name = name
        self._number = number
        if number and number > 0:
            self._contest = f'{name}{number:03}'
        else:
            self._contest = name

    @property
    def contest(self) -> str:
        return self._contest

    @property
    def number(self) -> Optional[int]:
        return self._number

    @property
    def url(self) -> str:
        return f'https://atcoder.jp/contests/{self.contest}/tasks'

    def __str__(self) -> str:
        return f'{self.contest}'

    def __repr__(self) -> str:
        return f'Contest(name={self._name}, number={self._number})'

    def problems(self, session: Optional[requests.Session] = None) -> List['Problem']:
        session = session or requests.Session()
        response = session.get(self.url)

        if response.status_code != 200:
            return []

        return [
            Problem(self, label=label, url=url)
            for label, url in get_problem_urls_from_tasks(response.text)
        ]


class Diff(str):
    def __new__(cls, diff: str) -> 'Diff':
        if isinstance(diff, str) and len(diff) == 1 and diff.isalpha():
            return super().__new__(cls, diff.upper())
        raise ValueError('diffは英大文字または小文字の1文字である必要があります')

    def __repr__(self) -> str:
        return f"Diff('{self}')"


class Problem:
    def __init__(
        self,
        contest: Contest,
        difficulty: Optional[Diff] = None,
        label: Optional[str] = None,
        url: Optional[str] = None,
    ):
        self._contest = contest
        if difficulty:
            self._label = difficulty.upper()
            self._url = contest.url + f'/{contest}_{difficulty.lower()}'
        elif label and url:
            self._label = label
            self._url = url
        else:
            raise ValueError('labelとurlは両方必須かdifficultyが必要です')

    @property
    def contest(self) -> Contest:
        return self._contest

    @property
    def label(self) -> str:
        return self._label

    @property
    def url(self) -> str:
        return self._url

    def __repr__(self) -> str:
        return f'Problem(contest={self.contest}, label={self.label}, url={self.url})'

    def __str__(self) -> str:
        return f'{self.contest} {self.label}'
