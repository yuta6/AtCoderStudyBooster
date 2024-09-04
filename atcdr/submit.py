from atcdr.util.execute import execute_files
from atcdr.util.filetype import COMPILED_LANGUAGES, INTERPRETED_LANGUAGES


def submit_source(path: str) -> None:
    pass


def submit(*args: str) -> None:
    execute_files(
        *args,
        func=submit_source,
        target_filetypes=COMPILED_LANGUAGES + INTERPRETED_LANGUAGES,
    )
