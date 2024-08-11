import os
from enum import Enum
from typing import Callable, Dict, List, TypeAlias

# ファイル名と拡張子の型エイリアスを定義
Filename: TypeAlias = str
Extension: TypeAlias = str


class Lang(Enum):
	PYTHON = 'Python'
	JAVASCRIPT = 'JavaScript'
	JAVA = 'Java'
	C = 'C'
	CPP = 'C++'
	CSHARP = 'C#'
	RUBY = 'Ruby'
	PHP = 'php'
	GO = 'Go'
	RUST = 'Rust'
	HTML = 'HTML'
	MARKDOWN = 'markdown'
	JSON = 'json'


# ファイル拡張子と対応する言語の辞書
FILE_EXTENSIONS: Dict[Lang, Extension] = {
	Lang.PYTHON: '.py',
	Lang.JAVASCRIPT: '.js',
	Lang.JAVA: '.java',
	Lang.C: '.c',
	Lang.CPP: '.cpp',
	Lang.CSHARP: '.cs',
	Lang.RUBY: '.rb',
	Lang.PHP: '.php',
	Lang.GO: '.go',
	Lang.RUST: '.rs',
	Lang.HTML: '.html',
	Lang.MARKDOWN: '.md',
	Lang.JSON: '.json',
}

DOCUMENT_LANGUAGES: List[Lang] = [
	Lang.HTML,
	Lang.MARKDOWN,
	Lang.JSON,
]

# ソースコードファイルと言語のリスト
SOURCE_LANGUAGES: List[Lang] = [
	Lang.PYTHON,
	Lang.JAVASCRIPT,
	Lang.JAVA,
	Lang.C,
	Lang.CPP,
	Lang.CSHARP,
	Lang.RUBY,
	Lang.PHP,
	Lang.GO,
	Lang.RUST,
]


def str2lang(lang: str) -> Lang:
	lang_map = {
		'py': Lang.PYTHON,
		'python': Lang.PYTHON,
		'js': Lang.JAVASCRIPT,
		'javascript': Lang.JAVASCRIPT,
		'java': Lang.JAVA,
		'c': Lang.C,
		'cpp': Lang.CPP,
		'c++': Lang.CPP,
		'csharp': Lang.CSHARP,
		'c#': Lang.CSHARP,
		'rb': Lang.RUBY,
		'ruby': Lang.RUBY,
		'php': Lang.PHP,
		'go': Lang.GO,
		'rs': Lang.RUST,
		'rust': Lang.RUST,
		'html': Lang.HTML,
		'md': Lang.MARKDOWN,
		'markdown': Lang.MARKDOWN,
		'json': Lang.JSON,
	}
	return lang_map[lang.lower()]


def lang2str(lang: Lang) -> str:
	return lang.value


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
			print('複数のファイルが見つかりました。以下のファイルから選択してください:')
			for i, file in enumerate(files):
				print(f'{i + 1}. {file}')
			choice = int(input('ファイル番号を入力してください: ')) - 1
			if 0 <= choice < len(files):
				func(files[choice])
			else:
				print('無効な選択です')
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
