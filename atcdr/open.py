import glob
import os
import webbrowser

from bs4 import BeautifulSoup as bs


def find_link_from(html: str) -> str | None:
    soup = bs(html, "html.parser")
    meta_tag = soup.find("meta", property="og:url")
    if meta_tag and "content" in meta_tag.attrs:
        return meta_tag["content"]
    return None


def open_html(file: str | None = None) -> None:
    if file is None:
        html_files = glob.glob("*.html") + glob.glob("*.htm")
        if html_files:
            file = html_files[0]  # 最初に見つかったHTMLファイルを使用
        else:
            print("HTMLファイルが見つかりません。")
            return

    if file and not os.path.splitext(file)[1]:
        file += ".html"

    try:
        with open(file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"HTMLファイル '{file}' が見つかりません。")
        return

    url = find_link_from(html_content)
    if url:
        webbrowser.open(url)
    else:
        print("URLが見つかりませんでした。")
