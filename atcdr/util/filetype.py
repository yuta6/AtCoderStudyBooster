import os
from enum import Enum
from typing import Dict, List, Optional, TypeAlias

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
FILE_EXTENSIONS: Dict[Lang, str] = {
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

# ドキュメント言語のリスト
DOCUMENT_LANGUAGES: List[Lang] = [
	Lang.HTML,
	Lang.MARKDOWN,
	Lang.JSON,
]

# コンパイル型言語のリスト
COMPILED_LANGUAGES: List[Lang] = [
	Lang.JAVA,
	Lang.C,
	Lang.CPP,
	Lang.CSHARP,
	Lang.GO,
	Lang.RUST,
]

# インタプリター型言語のリスト
INTERPRETED_LANGUAGES: List[Lang] = [
	Lang.PYTHON,
	Lang.JAVASCRIPT,
	Lang.RUBY,
	Lang.PHP,
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


def detect_language(path: str) -> Optional[Lang]:
	ext = os.path.splitext(path)[1]  # ファイルの拡張子を取得
	lang = next(
		(lang for lang, extension in FILE_EXTENSIONS.items() if extension == ext), None
	)
	return lang
