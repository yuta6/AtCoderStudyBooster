import webbrowser

from bs4 import BeautifulSoup as bs

from atcdr.util.filename import FileExtension, execute_files


def find_link_from(html: str) -> str | None:
    soup = bs(html, "html.parser")
    meta_tag = soup.find("meta", property="og:url")
    if meta_tag and "content" in meta_tag.attrs:
        return meta_tag["content"]
    return None


def open_html(file: str) -> None:
    try:
        with open(file, "r") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"HTMLファイル '{file}' が見つかりません。")
        return

    url = find_link_from(html_content)
    if url:
        webbrowser.open(url)
    else:
        print("URLが見つかりませんでした。")


def open_files(*args: str) -> None:
    execute_files(*args, func=open_html, target_filetypes=[FileExtension.HTML])
