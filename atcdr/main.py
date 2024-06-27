from typing import Union,Tuple

import fire

from atcdr.download_problem import download
from atcdr.check_samplecase import test

MAP_COMMANDS = {
    '-t': test,
    '--test': test,
    '-d': download,
    '--download': download
}

def main():
    fire.Fire(MAP_COMMANDS)

if __name__ == "__main__":
    main()