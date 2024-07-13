from typing import Union,Tuple

import fire

from atcdr.download import download
from atcdr.test import test
from atcdr.generate import generate

MAP_COMMANDS = {
    '-t': test,
    '--test': test,
    '-d': download,
    '--download': download,
    '-g' : generate,
    '--generate' : generate,
    '-h' : lambda: fire.Fire(MAP_COMMANDS),
    '--help': lambda: fire.Fire(MAP_COMMANDS)
}

def main():
    fire.Fire(MAP_COMMANDS)

if __name__ == "__main__":
    main()