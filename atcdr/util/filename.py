import os
from typing import Callable, List, TypeAlias

# ファイル名と拡張子の型エイリアスを定義
Filename: TypeAlias = str
Extension: TypeAlias = str


class FileExtension:
    # ドキュメントファイル
    HTML: Extension = ".html"
    MARKDOWN: Extension = ".md"
    TXT: Extension = ".txt"
    JSON: Extension = ".json"
    DOCUMENT_EXTENSIONS: List[Extension] = [HTML, MARKDOWN, TXT, JSON]

    # ソースコードファイル
    PYTHON: Extension = ".py"
    JAVASCRIPT: Extension = ".js"
    JAVA: Extension = ".java"
    C: Extension = ".c"
    CPP: Extension = ".cpp"
    CSHARP: Extension = ".cs"
    RUBY: Extension = ".rb"
    PHP: Extension = ".php"
    GO: Extension = ".go"
    RUST: Extension = ".rs"
    SOURCE_EXTENSIONS: List[Extension] = [
        PYTHON,
        JAVASCRIPT,
        JAVA,
        C,
        CPP,
        CSHARP,
        RUBY,
        PHP,
        GO,
        RUST,
    ]

    # 実行形式ファイル
    EXE: Extension = ".exe"
    OUT: Extension = ".out"


def execute_files(
    *args: str, func: Callable[[Filename], None], target_filetypes: List[Extension]
) -> None:
    files = [
        file
        for file in os.listdir(".")
        if os.path.isfile(file) and os.path.splitext(file)[1] in target_filetypes
    ]

    if not files:
        print(
            "対象のファイルが見つかりません.\n対象ファイルが存在するディレクトリーに移動してから実行してください。"
        )
        return

    if not args:
        if len(files) == 1:
            func(files[0])
        else:
            print("複数のファイルが見つかりました。以下のファイルから選択してください:")
            for i, file in enumerate(files):
                print(f"{i + 1}. {file}")
            choice = int(input("ファイル番号を入力してください: ")) - 1
            if 0 <= choice < len(files):
                func(files[choice])
            else:
                print("無効な選択です")
    else:
        target_files = set()
        for arg in args:
            if arg == "*":
                target_files.update(files)
            elif arg.startswith("*."):
                ext = arg[1:]  # ".py" のような拡張子を取得
                target_files.update(file for file in files if file.endswith(ext))
            else:
                if arg in files:
                    target_files.add(arg)
                else:
                    print(f"エラー: {arg} は存在しません。")

        list(map(func, target_files))
