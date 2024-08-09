# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境の作成
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "仮想環境 'venv' が作成されました。"
else
    echo "仮想環境 'venv' は既に存在します。"
fi

# 仮想環境をアクティブ化
source venv/bin/activate

# 必要なパッケージをインストール
pip install --upgrade pip
pip install -r requirements.txt
pip install -e '.[dev]'

# pre-commitのインストールと設定
pre-commit clean
pre-commit install
pre-commit autoupdate

echo "開発環境のセットアップが完了しました。仮想環境が有効になっています。"
