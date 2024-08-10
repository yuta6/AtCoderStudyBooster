# AtCoderStudyBooster

## 概要

AtCoderStudyBoosterはAtCoderの学習を加速させるためのツールです。問題をローカルにダウンロード、テスト、解答の作成をサポートするツールです。Pythonが入っていることが必須です。Pythonが入っている環境なら、`pip install AtCoderStudyBooster`でインストールできます。

## 利用ケース

### B問題の練習したい場合

ABCコンテストの223から226のB問題だけを集中的に練習したい場合、次のコマンドを実行します。

```sh
atcdr download B 223..226
```

コマンドを実行すると,次のようなフォルダーを作成して、各々のフォルダーに問題をダウンロードします。

```css
B
├── 223
│   ├── StringShifting.html
│   └── StringShifting.md
├── 224
│   ├── Mongeness.html
│   └── Mongeness.md
├── 225
│   ├── StarorNot.html
│   └── StarorNot.md
└── 226
    ├── CountingArrays.html
    └── CountingArrays.md
```

MarkdownファイルあるいはHTMLファイルをVS CodeのHTML Preview, Markdown Previewで開くと問題を確認できます。VS Codeで開くと左側にテキストエディターを表示して、右側で問題をみながら問題に取り組めます。

![demo画像](./.images/demo1.png)

### サンプルをローカルでテストする

問題をダウンロードしたフォルダーに移動します。

```sh
cd B/224
```

移動したフォルダーで解答ファイルを作成後を実行すると, 自動的にテストします。

```sh
▷ ~/.../B/224
atcdr t
```

```sh
solution.pyをテストします。
--------------------

Sample 1 of Test:
✓ Accepted !! Time: 24 ms

Sample 2 of Test:
✓ Accepted !! Time: 15 ms
```

と実行すると作成したソースコードをテストして、HTMLに書かれているテストケースを読み込んで実行し, Passするかを判定します。
