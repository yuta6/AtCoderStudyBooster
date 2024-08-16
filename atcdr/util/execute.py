import os
from typing import Callable, List

import questionary as q
from rich import print

from atcdr.util.filetype import FILE_EXTENSIONS, Filename, Lang


def execute_files(
	*args: str, func: Callable[[Filename], None], target_filetypes: List[Lang]
) -> None:
	target_extensions = [FILE_EXTENSIONS[lang] for lang in target_filetypes]

	files = [
		file
		for file in os.listdir('.')
		if os.path.isfile(file) and os.path.splitext(file)[1] in target_extensions
	]

	if not files:
		print(
			'対象のファイルが見つかりません.\n対象ファイルが存在するディレクトリーに移動してから実行してください。'
		)
		return

	if not args:
		if len(files) == 1:
			func(files[0])
		else:
			target_file = q.select(
				message='複数のファイルが見つかりました.ファイルを選択してください:',
				choices=[q.Choice(title=file, value=file) for file in files],
				instruction='\n 十字キーで移動, [enter]で実行',
				pointer='❯❯❯',
				qmark='',
				style=q.Style(
					[
						('qmark', 'fg:#2196F3 bold'),
						('question', 'fg:#2196F3 bold'),
						('answer', 'fg:#FFB300 bold'),
						('pointer', 'fg:#FFB300 bold'),
						('highlighted', 'fg:#FFB300 bold'),
						('selected', 'fg:#FFB300 bold'),
					]
				),
			).ask()
			list(map(func, [target_file]))
	else:
		target_files = set()
		for arg in args:
			if arg == '*':
				target_files.update(files)
			elif arg.startswith('*.'):
				ext = arg[1:]  # ".py" のような拡張子を取得
				target_files.update(file for file in files if file.endswith(ext))
			else:
				if arg in files:
					target_files.add(arg)
				else:
					print(f'エラー: {arg} は存在しません。')

		list(map(func, target_files))
