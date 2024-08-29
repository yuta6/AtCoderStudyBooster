from importlib.metadata import metadata

import fire  # type: ignore
from rich.traceback import install

from atcdr.download import download
from atcdr.generate import generate
from atcdr.markdown import markdown
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
	'markdown': markdown,
	'md': markdown,
	'--version': get_version,
	'-v': get_version,
}


def main():
	install()
	fire.Fire(MAP_COMMANDS)


if __name__ == '__main__':
	main()
