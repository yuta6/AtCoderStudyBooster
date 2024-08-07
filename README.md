# AtCoderStudyBooster

## 概要

AtCoderStudyBoosterはAtCoderの問題をローカルにダウンロード、テスト、提出、解答の作成をサポートするツールです。Pythonが入っていることが必須で、Pythonが入っている環境なら、`pip install AtCoderStudyBooster`でインストールできます。

## 利用ケース

### B問題の練習したい場合

ABCコンテストの223から226のB問題だけを集中的に練習したい場合、次のコマンドを実行します。

```sh
atcdr d B 223..226
```

コマンドを実行すると,次のようなフォルダーを作成して、各々のフォルダーに問題をダウンロードします。

```css
B
├── 223
│   └── StringShifting.html
├── 224
│   └── Mongeness.html
├── 225
│   └── StarorNot.html
└── 226
    └── CountingArrays.html
```

HTMLファイルをブラウザーやVS CodeのHTMLレビュワーで開くと問題を確認できます。VS Codeで開くと左側にテキストエディターを表示して,右側で問題をみながら問題に取り組めます。

### テストケースをチェックしたい場合

問題をダウンロードしたフォルダーに移動します。

```sh
cd B/223
```

ディレクトリーで解答ファイルを作成後


```sh
atcdr t
```

と実行すると作成したソースコードをテストして、HTMLに書かれているテストケースを読み込んで実行し, Passするかを判定します。

## コマンドの使い方


## ライセンス

MIT License
