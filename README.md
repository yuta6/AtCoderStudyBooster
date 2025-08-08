# AtCoderStudyBooster

## 概要

🚧 このプロジェクトはまだ実験段階です。日々のAtCoder学習に役立つ機能を順次追加しています。

AtCoderStudyBoosterはAtCoderの学習を加速させるためのCLIツールです。問題をローカルにダウンロードし、テスト、提出、解答の作成をサポートするツールです。Pythonが入っていることが必須です。Pythonが入っている環境なら、

```sh
pip install AtCoderStudyBooster
```

でインストールできます。(Python3.8以上が必要です)

キャプチャ認証が導入されたあとでも、CLIから半自動でログイン＆提出できます。ただしキャプチャをGUIから人力で解く必要があります。キャプチャー認証をバイパスするものではありません。

このツールは以下のプロジェクトに強く影響を受けています。
- [online-judge-tools](https://github.com/online-judge-tools)
- [atcoder-cli](https://github.com/Tatamo/atcoder-cli)

## 利用ケース

まずは`download`コマンドを利用して問題をローカルにダウンロードしてみましょう。

### 1. 特定のコンテストをダウンロードする

1つのコンテストの問題をダウンロードしたい場合の例です。

#### ABC350の全問題をダウンロード
```sh
❯ atcdr download abc350
```

#### ABC350のA〜D問題をダウンロード
```sh
❯ atcdr download abc350 {A..D}
```

#### 競プロ典型90問のダウンロード
```sh
❯ atcdr download typical90
```

### 2. 複数のコンテストを一括でダウンロードする

複数のコンテストを一度にダウンロードしたい場合の例です。bashのブレース展開を活用します。

#### ABC001〜ABC010までの全問題
```sh
❯ atcdr download abc{001..010}
```

#### ABC320〜ABC325までのA〜C問題
```sh
❯ atcdr download abc{320..325} {A..C}
```

次のようなフォルダー構造が生成されます：

```
abc320/
├── A/
│   ├── Problem.html
│   └── Problem.md
├── B/
│   ├── Problem.html
│   └── Problem.md
└── C/
    ├── Problem.html
    └── Problem.md
abc321/
├── A/
...（以下同様）
```

### 3. 特定の問題（A問題、B問題など）を集中的に演習したい場合

特定の難易度の問題だけを集めて練習したい場合は、**問題ラベルを先に指定**すると便利です。

#### B問題だけを集中的に練習
```sh
❯ atcdr download B abc{250..260}
```

問題ラベルを先に指定すると、問題ラベルごとにフォルダが作成され、その中にコンテスト名のフォルダが配置されます。

```
B/
├── abc250/
│   ├── Problem.html
│   └── Problem.md
├── abc251/
│   ├── Problem.html
│   └── Problem.md
├── abc252/
│   ├── Problem.html
│   └── Problem.md
└── ...（以下同様）
```

A問題とB問題を集める場合（`{A,B} abc{300..302}`）：

```
A/
├── abc300/
│   ├── Problem.html
│   └── Problem.md
├── abc301/
│   ├── Problem.html
│   └── Problem.md
└── abc302/
    ├── Problem.html
    └── Problem.md
B/
├── abc300/
│   ├── Problem.html
│   └── Problem.md
├── abc301/
│   ├── Problem.html
│   └── Problem.md
└── abc302/
    ├── Problem.html
    └── Problem.md
```
このディレクトリ構造により、同じ難易度の問題を一箇所に集めて効率的に演習できます。

### 問題を解く

MarkdownファイルあるいはHTMLファイルをVS CodeのHTML Preview, Markdown Previewで開くと問題を確認できます。VS Codeで開くと左側にテキストエディターを表示して、右側で問題をみながら問題に取り組めます。

![demo画像](./.images/demo1.png)

### サンプルをローカルでテストする

問題をダウンロードしたフォルダーに移動します。

```sh
❯ cd abc224/B
```

移動したフォルダーで解答ファイルを作成後、testコマンドを実行すると、サンプルケースをテストします。

```sh
~/.../abc224/B
❯ atcdr t
```

![demo画像](./.images/demo2.png)

WAの場合は以下のような表示になります。

![demo画像](./.images/demo3.png)

### 提出する

```sh
~/.../abc224/B
❯ atcdr s
```

を実行すると、提出することができます。提出にはAtCoderのサイトへのログインが必要です。

### 解答をGPTで生成する

```sh
~/.../abc224/B
❯ atcdr g
```

で解答をGPTで生成します。Chat GPTのAPIキーが必要です。さらに、生成されたファイルはサンプルケースが自動でテストされ、**テストをパスしなかった場合、テスト結果がGPTにフィードバックされ解答が再生成**されます。

GPTとプログラムとのやり取りのログはJSONファイルで保存されます。

## 解答生成機能generateコマンドに関する注意点

[AtCoder生成AI対策ルール](https://info.atcoder.jp/entry/llm-rules-ja)によるとAtCoder Beginner Contest（以下、ABCとする）および AtCoder Regular Contest (Div. 2) においてに問題文を生成AIに直接与えることは禁止されています。ただし、このルールは過去問を練習している際には適用されません。該当のコンテスト中にこの機能を使用しないでください。

## その他の機能

### markdownコマンド

完全なCLI環境方向けのコマンドです。

```sh
~/.../abc224/B
❯ atcdr md
```

を実行すると、問題をプリントします。

![demo画像](./.images/demo4.png)

### 複数のファイルを一度にテスト

```sh
~/.../abc224/B
❯ atcdr t *.py
```

でフォルダー内にあるすべてのPythonファイルを一度にテストします。

```sh
~/.../abc224/B
❯ atcdr t mon.py mon.c mon.cpp
```

フォルダー内に複数ファイルある場合は、インタラクティブに選択できます。

```sh
~/.../abc224/B
❯ atcdr t
```

```sh
~/.../abc224/B
❯ atcdr t
複数のファイルが見つかりました.ファイルを選択してください:
 十字キーで移動, [enter]で実行
❯❯❯ mon.py
    mon.c
    mon.cpp
```

### プログラミング言語を指定してコードを生成

`--lang`オプションを使うと、生成したいプログラミング言語を指定できます。

```sh
~/.../abc224/B
❯ atcdr generate --lang rust
```

### テストをせずにコードのみ生成

デフォルトで`atcdr generate`コマンドは生成されたコードをテストしますが、テストせずにコードのみ生成できます。

```sh
~/.../abc224/B
❯ atcdr generate --lang rust --without_test
```
