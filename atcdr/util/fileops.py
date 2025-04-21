import functools
import glob
import os
from typing import List, Tuple

import questionary as q
import rich_click as click

from atcdr.util.filetype import FILE_EXTENSIONS, Lang


def collect_files(
    patterns: Tuple[str, ...],
    exts: Tuple[str, ...],
    recursive: bool,
) -> List[str]:
    # 1) ベース候補
    if recursive:
        candidates = []
        for root, _, files in os.walk('.'):
            for f in files:
                candidates.append(os.path.join(root, f))
    else:
        candidates = [f for f in os.listdir('.') if os.path.isfile(f)]

    # 2) パターン＋glob 展開
    matched = set()
    pats = patterns or ['*']
    for pat in pats:
        for m in glob.glob(pat, recursive=recursive):
            if os.path.isfile(m):
                matched.add(m)
        if '*' not in pat and os.path.isfile(pat):
            matched.add(pat)

    if exts:
        matched = {f for f in matched if os.path.splitext(f)[1] in exts}

    return sorted(matched)


def select_files_interactively(files: List[str]) -> List[str]:
    target_file = q.select(
        message='複数のファイルが見つかりました.ファイルを選択してください:',
        choices=[q.Choice(title=file, value=file) for file in files],
        instruction='\n 十字キーで移動, [enter]で実行',
        pointer='❯',
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
    return target_file


def add_file_selector(
    arg_name: str,
    filetypes: list[Lang],
):
    def decorator(f):
        @click.argument(arg_name, nargs=-1, type=click.STRING)
        @click.pass_context
        @functools.wraps(f)
        def wrapper(ctx: click.Context, **kwargs):
            # Click から渡される元のパターン一覧を取得
            patterns: tuple[str, ...] = kwargs.pop(arg_name)

            # 1) 拡張子リストを作成
            exts = [FILE_EXTENSIONS[lang] for lang in filetypes]

            # 2) ファイル収集 (非再帰固定)
            files = collect_files(patterns, tuple(exts), recursive=False)
            if not files:
                click.echo('対象ファイルが見つかりません。')
                ctx.exit(1)

            # 3) 候補が1つなら即実行
            if len(files) == 1:
                return ctx.invoke(f, **{arg_name: files}, **kwargs)

            # 4) 引数なしなら対話選択、それ以外はまとめて渡す
            if not patterns:
                selected = select_files_interactively(files)
                if not selected:
                    click.echo('ファイルが選択されませんでした。')
                    ctx.exit(1)
                selected_list = [selected]
                return ctx.invoke(f, **{arg_name: selected_list}, **kwargs)

            # 5) patterns 指定ありならマッチ全件を渡す
            return ctx.invoke(f, **{arg_name: files}, **kwargs)

        return wrapper

    return decorator
