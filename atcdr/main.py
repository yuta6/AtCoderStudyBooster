import fire

from atcdr.download import download
from atcdr.generate import generate
from atcdr.open import open_html
from atcdr.test import test

MAP_COMMANDS: dict = {
    "test": test,
    "t": test,
    "download": download,
    "d": download,
    "open": open_html,
    "o": open_html,
    "generate": generate,
    "g": generate,
}


def main():
    fire.Fire(MAP_COMMANDS)


if __name__ == "__main__":
    main()
