import fire

from atcdr.download import download
from atcdr.open import open_html
from atcdr.test import test

MAP_COMMANDS: dict = {
    "-t": test,
    "--test": test,
    "-d": download,
    "--download": download,
    "-o": open_html,
    "--open": open_html,
    "-h": lambda: fire.Fire(MAP_COMMANDS),
    "--help": lambda: fire.Fire(MAP_COMMANDS),
}


def main():
    fire.Fire(MAP_COMMANDS)


if __name__ == "__main__":
    main()
