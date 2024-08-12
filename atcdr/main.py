from importlib.metadata import metadata

import fire  # type: ignore

from atcdr.download import download
from atcdr.generate import generate
from atcdr.open import open_files
from atcdr.test import test


def get_version() -> None:
	meta = metadata('AtCoderStudyBooster')
	print(meta['Name'], meta['Version'])


MAP_COMMANDS: dict = {
	'test': test,
	't': test,
	'download': download,
	'd': download,
	'open': open_files,
	'o': open_files,
	'generate': generate,
	'g': generate,
	'--version': get_version,
	'-v': get_version,
}


def main():
	fire.Fire(MAP_COMMANDS)


if __name__ == '__main__':
	main()
