from enum import Enum
from typing import Dict, List, TypeAlias

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
		'cs': Lang.CSHARP,
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
