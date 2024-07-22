from dataclasses import dataclass


@dataclass
class Option:
    pass


def generate(problem_paragrah: str, option: Option) -> str:
    return problem_paragrah + str(Option)
