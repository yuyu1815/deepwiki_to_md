# Deepwiki to Markdown コンバーター

> **The English version of this document is [README.md](./README.md) here.**

Deepwiki サイトからコンテンツをスクレイピングし、Markdown 形式に変換する Python ツールです。

## 特徴

- Deepwiki サイトからコンテンツをスクレイピング
- 指定した UI 要素からナビゲーション項目を抽出
- HTML コンテンツを Markdown 形式に変換
- 変換後のファイルを整理されたディレクトリ構造で保存
- 複数のライブラリのスクレイピングに対応
- 静的リクエストによるスクレイピングに対応

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
from deepwiki_to_md.direct_scraper import DirectDeepwikiScraper
from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper

# スクレイパーインスタンスを作成
scraper = DeepwikiScraper(output_dir="MyDocuments")

# ライブラリをスクレイピング
scraper.scrape_library("python", "https://deepwiki.com/python")

# 別の出力ディレクトリを持つスクレイパーを作成
other_scraper = DeepwikiScraper(output_dir="OtherDocuments")

# 別のライブラリをスクレイピング
other_scraper.scrape_library("javascript", "https://deepwiki.example.com/javascript")

# DirectDeepwikiScraper インスタンスを作成
direct_scraper = DirectDeepwikiScraper(output_dir="DirectScraped")

# 特定のページを直接スクレイピング
direct_scraper.scrape_page(
    "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
    "python_bytecode",
    save_html=True
)

# DirectMarkdownScraper インスタンスを作成（Markdownを直接取得）
direct_md_scraper = DirectMarkdownScraper(output_dir="DirectMarkdownDocuments")

# 特定のページを直接Markdownとしてスクレイピング
direct_md_scraper.scrape_page(
    "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
    "python_bytecode"
)

# DirectMarkdownScraper を有効にした DeepwikiScraper も使用可能
md_scraper = DeepwikiScraper(
    output_dir="DirectMarkdownDocuments",
    use_direct_scraper=False,
    use_alternative_scraper=False,
    use_direct_md_scraper=True  # 直接Markdownスクレイピングを有効化
)
md_scraper.scrape_library("python", "https://deepwiki.com/python/cpython")

# run メソッドを使用して複数の直接スクレイピングを実行することも可能
# direct_results = direct_scraper.run([
#     {"name": "page1", "url": "url1"},
#     {"name": "page2", "url": "url2"}
# ])
```

サンプルスクリプトを実行するには：

```
python example.py
```

### コマンドライン引数

- `library_url`: スクレイピング対象のライブラリの URL（位置引数として指定可能）
- `--library`, `-l`: スクレイピング対象のライブラリ名と URL。複数指定可能。
- `--output-dir`, `-o`: Markdown ファイルの出力ディレクトリ（デフォルト: Documents）
- `--use-direct-scraper`: DirectDeepwikiScraper を使用（デフォルト: True）
- `--no-direct-scraper`: DirectDeepwikiScraper を無効化
- `--use-alternative-scraper`: ナビゲーション項目がないページに代替スクレイパーを使用（デフォルト: True）
- `--no-alternative-scraper`: ナビゲーション項目がないページの代替スクレイパーを無効化
- `--use-direct-md-scraper`: DirectMarkdownScraper を使用して直接Markdownを取得（デフォルト: False）
- `--no-direct-md-scraper`: DirectMarkdownScraper を無効化

### 使用例

1. 簡易的な使い方：
   ```
   python run_scraper.py "https://deepwiki.com/python"
   ```

2. 明示的なパラメータを使用した単一のライブラリをスクレイピング：
   ```
   python run_scraper.py --library "python" "https://deepwiki.example.com/python"
   ```

3. 直接スクレイパーを使用してMarkdownを直接取得：
   ```
   python run_direct_scraper.py "https://deepwiki.com/python"
   ```

4. HTMLも保存する直接スクレイパーの使用：
   ```
   python run_direct_scraper.py --library "python" "https://deepwiki.example.com/python" --save-html
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

6. DirectDeepwikiScraper を使用：
   ```
   python run_scraper.py "https://deepwiki.com/python" --use-direct-scraper
   ```

7. DirectDeepwikiScraper を無効化：
   ```
   python run_scraper.py "https://deepwiki.com/python" --no-direct-scraper
   ```

8. ナビゲーション項目がないページの代替スクレイパーを無効化：
   ```
   python run_scraper.py "https://deepwiki.com/python" --no-alternative-scraper
   ```

9. 代替スクレイパーを明示的に有効化（デフォルトで有効）：
   ```
   python run_scraper.py "https://deepwiki.com/python" --use-alternative-scraper
   ```

10. DirectMarkdownScraper を使用して直接Markdownを取得：
   ```
   python run_scraper.py "https://deepwiki.com/python" --use-direct-md-scraper
   ```

11. カスタム出力ディレクトリを指定してDirectMarkdownScraperを使用：
   ```
   python run_scraper.py "https://deepwiki.com/python" --use-direct-md-scraper --output-dir "DirectMarkdownDocuments"
   ```

12. DirectMarkdownScraperのみを使用（他のスクレイパーを無効化）：
   ```
   python run_scraper.py "https://deepwiki.com/python" --use-direct-md-scraper --no-direct-scraper --no-alternative-scraper
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

### 静的ページスクレイピング（デフォルト）

1. requests ライブラリを使用して指定された deepwiki サイトに接続します。
2. `ul` タグ（class="flex-1 flex-shrink-0 space-y-1 overflow-y-auto py-1"）からナビゲーション項目を抽出します。
3. 各ナビゲーション項目ごとにページコンテンツを取得します。
4. ページからメインコンテンツを抽出します。
5. HTML コンテンツを Markdown 形式に変換します。
6. 指定されたディレクトリ構造で Markdown ファイルとして保存します。

### 直接スクレイピング機能

#### DirectDeepwikiScraper

直接スクレイピング機能では、DeepWikiから直接コンテンツを取得できます：

1. 特殊なヘッダーを使用してDeepWikiサイトに接続します
2. レスポンスからHTMLコンテンツを抽出します
3. 左側のURLを取得するために必要なHTML構造を保持します（オプション）
4. HTMLをMarkdownに変換します
5. ページからナビゲーション項目を抽出し、階層的にスクレイピングします
6. 指定されたディレクトリ構造でMarkdownファイルとして保存します

この方法は、標準的なスクレイピング方法よりも信頼性の高いコンテンツ抽出を提供します。

#### DirectMarkdownScraper（新機能）

新しい直接Markdownスクレイピング機能では、HTML変換なしでDeepWikiから直接Markdownコンテンツを取得できます：

1. Markdownコンテンツに最適化された特殊なヘッダーを使用してDeepWikiサイトに接続します
2. サーバーから直接Markdownコンテンツを取得します
3. ページからナビゲーション項目を抽出し、階層的にスクレイピングします
4. 指定されたディレクトリ構造でMarkdownファイルとして保存します

この方法は、HTMLからMarkdownへの変換プロセスを完全にスキップし、適切な書式と構造を持つ最高品質のMarkdownコンテンツを提供します。

### エラー処理

このツールには、一般的な問題に対処するための堅牢なエラー処理が含まれています：

1. スクレイピングを試みる前にドメインを検証します（example.comのようなプレースホルダードメインを拒否）
2. 接続を試みる前にドメインが到達可能かどうかを確認します
3. ドメインに到達できない場合に明確なエラーメッセージを提供します
4. 主要な方法が失敗した場合に代替スクレイピング方法に適切にフォールバックします
5. 一時的なエラーに対して指数バックオフを使用した再試行メカニズムを実装しています


## カスタマイズ

`deepwiki_to_md.py` を編集することで以下をカスタマイズできます：

- コンテンツ抽出に使用する HTML セレクタ
- HTML から Markdown への変換ロジック
- 出力ファイルの命名規則
- リクエスト間の遅延時間

## ライセンス

このプロジェクトは MIT ライセンスのもとで公開されています。詳細は LICENSE ファイルをご覧ください。
