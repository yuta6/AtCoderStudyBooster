import fire

from atcdr.download import download
from atcdr.generate import generate
from atcdr.open import open_files
from atcdr.test import test

MAP_COMMANDS: dict = {
	'test': test,
	't': test,
	'download': download,
	'd': download,
	'open': open_files,
	'o': open_files,
	'generate': generate,
	'g': generate,
}


def main():
	fire.Fire(MAP_COMMANDS)


if __name__ == '__main__':
	main()
