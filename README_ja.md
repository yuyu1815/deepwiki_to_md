# Deepwiki to Markdown コンバーター

> **The English version of this document is [README.md](./README.md) here.**

Deepwiki サイトからコンテンツをスクレイピングし、Markdown 形式に変換する Python ツールです。

## 特徴

- Deepwiki サイトからコンテンツをスクレイピング
- 指定した UI 要素からナビゲーション項目を抽出
- HTML コンテンツを Markdown 形式に変換
- 変換後のファイルを整理されたディレクトリ構造で保存
- 複数のライブラリのスクレイピングに対応

## 必要要件

- Python 3.6 以上
- 必要な Python パッケージ：
    - requests
    - beautifulsoup4
    - argparse

## インストール方法

### 方法1: PyPI からインストール

```
pip install deepwiki-to-md
```

### 方法2: ソースコードからインストール

1. リポジトリをクローンします：
   ```
   git clone https://github.com/yourusername/deepwiki_to_md.git
   cd deepwiki_to_md
   ```

2. 開発モードでパッケージをインストールします：
   ```
   pip install -e .
   ```

## 使い方

### 基本的な使い方

PyPI からインストールした場合、コマンドラインツールとして使用できます：

```
deepwiki-to-md "https://deepwiki.com/library_path"
```

または明示的なパラメータを使用：

```
deepwiki-to-md --library "library_name" "https://deepwiki.example.com/library_path"
```

ソースコードからインストールした場合、スクリプトを直接実行します：

```
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/library_path"
```

または明示的なパラメータを使用：

```
python -m deepwiki_to_md.run_scraper --library "library_name" "https://deepwiki.example.com/library_path"
```

**注意**：出力ディレクトリはコマンドを実行したカレントディレクトリに作成されます。パッケージのインストール先ではありません。

### Python API を使う

`DeepwikiScraper` クラスを直接使用することも可能です。完全な例は `example.py` を参照してください：

```python
from deepwiki_to_md import DeepwikiScraper

# スクレイパーインスタンスを作成
scraper = DeepwikiScraper(output_dir="MyDocuments")

# ライブラリをスクレイピング
scraper.scrape_library("python", "https://deepwiki.com/python")

# または、別の出力ディレクトリを指定してスクレイパーインスタンスを作成
other_scraper = DeepwikiScraper(output_dir="OtherDocs")
other_scraper.scrape_library("javascript", "https://deepwiki.example.com/javascript")
```

サンプルスクリプトを実行するには：

```
python example.py
```

### コマンドライン引数

- `library_url`: スクレイピング対象のライブラリの URL（位置引数として指定可能）
- `--library`, `-l`: スクレイピング対象のライブラリ名と URL。複数指定可能。
- `--output-dir`, `-o`: Markdown ファイルの出力ディレクトリ（デフォルト: Documents）

### 使用例

1. 簡易的な使い方：
   ```
   python run_scraper.py "https://deepwiki.com/python"
   ```

2. 明示的なパラメータを使用した単一のライブラリをスクレイピング：
   ```
   python run_scraper.py --library "python" "https://deepwiki.example.com/python"
   ```

3. 複数ライブラリをスクレイピング：
   ```
   python run_scraper.py --library "python" "https://deepwiki.example.com/python" --library "javascript" "https://deepwiki.example.com/javascript"
   ```

4. カスタム出力ディレクトリを指定してスクレイピング（簡易的な使い方）：
   ```
   python run_scraper.py "https://deepwiki.com/python" --output-dir "MyDocuments"
   ```

5. カスタム出力ディレクトリを指定してスクレイピング（明示的なパラメータを使用）：
   ```
   python run_scraper.py --library "python" "https://deepwiki.example.com/python" --output-dir "MyDocuments"
   ```

## 出力構成

変換された Markdown ファイルは以下のようなディレクトリ構成で保存されます：

```
Documents/
├── library_name1/
│   └── md/
│       ├── page1.md
│       ├── page2.md
│       └── ...
├── library_name2/
│   └── md/
│       ├── page1.md
│       ├── page2.md
│       └── ...
└── ...
```

## 仕組み

1. 指定された deepwiki サイトに接続します。
2. `ul` タグ（class="flex-1 flex-shrink-0 space-y-1 overflow-y-auto py-1"）からナビゲーション項目を抽出します。
3. 各ナビゲーション項目ごとにページコンテンツを取得します。
4. ページからメインコンテンツを抽出します。
5. HTML コンテンツを Markdown 形式に変換します。
6. 指定されたディレクトリ構造で Markdown ファイルとして保存します。

## カスタマイズ

`deepwiki_to_md.py` を編集することで以下をカスタマイズできます：

- コンテンツ抽出に使用する HTML セレクタ
- HTML から Markdown への変換ロジック
- 出力ファイルの命名規則
- リクエスト間の遅延時間

## ライセンス

このプロジェクトは MIT ライセンスのもとで公開されています。詳細は LICENSE ファイルをご覧ください。
