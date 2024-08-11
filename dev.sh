# 仮想環境の作成
python3 -m venv venv

# 仮想環境をアクティブ化
source venv/bin/activate

# 必要なパッケージをインストール
python -m pip install -e .\[dev\]

# pre-commitのインストールと設定
pre-commit
pre-commit clean
pre-commit install
pre-commit autoupdate
