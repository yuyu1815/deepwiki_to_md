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
- 信頼性向上と直接Markdown取得のための直接スクレイピングメソッドを提供
- Markdown ファイルを書式を保持したまま YAML 形式に変換

## 必要要件

- Python 3.6 以上
- 必要な Python パッケージ：
    - requests
    - beautifulsoup4
    - argparse
  - markdownify

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

# スクレイパーインスタンスを作成 (デフォルトでは DirectMarkdownScraper を使用)
scraper = DeepwikiScraper(output_dir="MyDocuments")

# デフォルト (DirectMarkdownScraper) を使用してライブラリをスクレイピング
scraper.scrape_library("python", "https://deepwiki.com/python")

# 別の出力ディレクトリを持つスクレイパーを作成
other_scraper = DeepwikiScraper(output_dir="OtherDocuments")

# 別のライブラリをスクレイピング
other_scraper.scrape_library("javascript", "https://deepwiki.example.com/javascript")

# --- DirectDeepwikiScraper (HTML から Markdown へ) を使用 ---
# DirectDeepwikiScraper を明示的に使用するスクレイパーインスタンスを作成
html_scraper = DeepwikiScraper(
    output_dir="HtmlScrapedDocuments",
    use_direct_scraper=True,  # DirectDeepwikiScraper を有効化
    use_alternative_scraper=False,
    use_direct_md_scraper=False
)
html_scraper.scrape_library("go", "https://deepwiki.com/go")

# --- DirectMarkdownScraper (直接 Markdown 取得) を使用 ---
# DirectMarkdownScraper を明示的に使用するスクレイパーインスタンスを作成
md_scraper = DeepwikiScraper(
    output_dir="DirectMarkdownDocuments",
    use_direct_scraper=False,
    use_alternative_scraper=False,
    use_direct_md_scraper=True  # DirectMarkdownScraper を有効化 (これがデフォルト)
)
md_scraper.scrape_library("rust", "https://deepwiki.com/rust")

# --- 個別の直接スクレイパーを使用 ---
# DirectDeepwikiScraper インスタンスを作成 (HTML から Markdown へ)
direct_html_scraper = DirectDeepwikiScraper(output_dir="DirectHtmlScraped")

# 特定のページを直接スクレイピング (HTML から Markdown へ)
direct_html_scraper.scrape_page(
    "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
    "python_bytecode",
    save_html=True  # オプションで元のHTMLを保存
)

# DirectMarkdownScraper インスタンスを作成 (直接 Markdown 取得)
direct_md_scraper = DirectMarkdownScraper(output_dir="DirectMarkdownFetched")

# 特定のページを直接Markdownとしてスクレイピング
direct_md_scraper.scrape_page(
    "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
    "python_bytecode"
)

# run メソッドを使用して複数の直接スクレイピングを実行することも可能 (DirectDeepwikiScraper 用)
# direct_html_results = direct_html_scraper.run([
#     {"name": "page1", "url": "url1"},
#     {"name": "page2", "url": "url2"}
# ])

# run メソッドを使用して複数の直接スクレイピングを実行することも可能 (DirectMarkdownScraper 用)
# direct_md_results = direct_md_scraper.run([
#     {"name": "page1", "url": "url1"},
#     {"name": "page2", "url": "url2"}
# ])
```

サンプルスクリプトを実行するには：

```
python example.py
```

### コマンドライン引数

- `library_url`: スクレイピング対象のライブラリの URL（位置引数として指定可能）。
- `--library`, `-l`: スクレイピング対象のライブラリ名と URL。複数指定可能。形式: `--library NAME URL`。
- `--output-dir`, `-o`: Markdown ファイルの出力ディレクトリ（デフォルト: `Documents`）。
- `--use-direct-scraper`: `DirectDeepwikiScraper` を使用（HTML から Markdown への変換）。両方が指定された場合、
  `--use-direct-md-scraper` を上書きします。
- `--no-direct-scraper`: `DirectDeepwikiScraper` を無効化。
- `--use-alternative-scraper`: 主要なメソッドが失敗した場合に `direct_scraper.py` の `scrape_deepwiki`
  関数をフォールバックとして使用（デフォルト: True）。
- `--no-alternative-scraper`: 代替スクレイパーのフォールバックを無効化。
- `--use-direct-md-scraper`: `DirectMarkdownScraper` を使用（Markdown を直接取得）。スクレイパータイプが明示的に指定されていない場合の
  **デフォルト動作**です。
- `--no-direct-md-scraper`: `DirectMarkdownScraper` を無効化。

**スクレイパーの優先順位:**

1. `--use-direct-scraper` が指定された場合、`DirectDeepwikiScraper` (HTML から Markdown へ) が使用されます。
2. `--use-direct-md-scraper` が指定された場合 (かつ `--use-direct-scraper` が指定されていない場合)、
   `DirectMarkdownScraper` (直接 Markdown) が使用されます。
3. `--use-direct-scraper` も `--use-direct-md-scraper` も指定されていない場合、**デフォルト**で `DirectMarkdownScraper` (
   直接 Markdown) が使用されます。
4. `--use-alternative-scraper` フラグは、選択された主要スクレイパー内のフォールバックメカニズムを制御します。

### 使用例

1. **簡易的な使い方 (デフォルトで DirectMarkdownScraper を使用):**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python"
   ```

2. **明示的なパラメータを使用した単一のライブラリをスクレイピング (デフォルトで DirectMarkdownScraper を使用):**
   ```
   python -m deepwiki_to_md.run_scraper --library "python" "https://deepwiki.example.com/python"
   ```

3. **複数ライブラリをスクレイピング (デフォルトで DirectMarkdownScraper を使用):**
   ```
   python -m deepwiki_to_md.run_scraper --library "python" "https://deepwiki.example.com/python" --library "javascript" "https://deepwiki.example.com/javascript"
   ```

4. **カスタム出力ディレクトリを指定:**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python" --output-dir "MyDocuments"
   ```

5. **DirectMarkdownScraper (直接 Markdown) を明示的に使用:**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python" --use-direct-md-scraper
   ```

6. **DirectDeepwikiScraper (HTML から Markdown へ) を明示的に使用:**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python" --use-direct-scraper
   ```

7. **代替スクレイパーのフォールバックを無効化:**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python" --no-alternative-scraper
   ```

8. **DirectDeepwikiScraper を使用し、代替フォールバックを無効化:**
   ```
   python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python" --use-direct-scraper --no-alternative-scraper
   ```

## 出力構成

変換された Markdown ファイルは以下のようなディレクトリ構成で保存されます：

```
<output_dir>/
├── <library_name1>/
│   └── md/
│       ├── <page_name1>.md
│       ├── <page_name2>.md
│       └── ...
├── <library_name2>/
│   └── md/
│       ├── <page_name1>.md
│       ├── <page_name2>.md
│       └── ...
└── ...
```

- `<output_dir>` は `--output-dir` で指定されたディレクトリです (デフォルト: `Documents`)。
- `<library_name>` はライブラリに提供された名前です。
- Deepwiki サイトの各ページは、`md` サブディレクトリ内に個別の `.md` ファイルとして保存されます。

## 仕組み

このツールは異なるスクレイピング戦略を提供します：

### 1. 直接 Markdown スクレイピング (`DirectMarkdownScraper` - デフォルト)

- **優先度:** 最高 (デフォルトで使用)。
- **方法:** サーバーの内部 API またはデータ構造から直接生の Markdown コンテンツを取得するために最適化された特殊なヘッダーを使用して
  Deepwiki サイトに接続します。
- **プロセス:**
    1. Markdown データを取得するように設計されたリクエストを送信します。
    2. レスポンス (多くの場合 JSON または特定のテキスト形式) を解析して Markdown コンテンツを抽出します。
    3. 抽出された Markdown をクリーンアップします (メタデータやスクリプトタグなどの潜在的なアーティファクトを削除)。
    4. クリーンアップされた Markdown コンテンツを直接ファイルに保存します。
- **利点:** 最高忠実度の Markdown、元の書式を保持、HTML 変換エラーを回避。

### 2. 直接 HTML スクレイピング (`DirectDeepwikiScraper`)

- **優先度:** 中 (`--use-direct-scraper` が指定された場合に使用)。
- **方法:** レンダリングされた HTML ページを取得するためにブラウザリクエストを模倣したヘッダーを使用して Deepwiki
  サイトに接続します。
- **プロセス:**
    1. ページの完全な HTML を取得します。
    2. BeautifulSoup を使用して HTML を解析します。
    3. さまざまな CSS セレクターを使用してメインコンテンツ領域を特定します。
    4. `markdownify` ライブラリを使用して、選択された HTML コンテンツブロックを Markdown に変換します。
    5. 変換された Markdown を保存します。
- **利点:** 直接 Markdown 取得が失敗した場合や利用できない場合に、基本的な静的スクレイピングよりも堅牢です。
- **欠点:** HTML 構造と変換品質に依存します。

### 3. 代替スクレイパーフォールバック (`direct_scraper.py` の `scrape_deepwiki`)

- **優先度:** 最低 (`--use-alternative-scraper` が有効な場合 (デフォルト)、主要スクレイパー内のフォールバックとして使用)。
- **方法:** 主要なメソッドが問題 (例: 複雑なナビゲーションや予期しないページ構造) に遭遇した場合に使用される可能性のある、より単純な静的リクエストメカニズム。
- **プロセス:** HTML を取得し、基本的なコンテンツ抽出を試みます。

### ナビゲーションと階層

- `DirectMarkdownScraper` と `DirectDeepwikiScraper` の両方が、取得したコンテンツ (Markdown または HTML)
  内のナビゲーションリンク (目次やサイドバーなど) を特定しようとします。
- これらのリンクを再帰的にたどり、ライブラリ全体の構造をスクレイピングします。

### エラー処理

このツールには堅牢なエラー処理が含まれています：

- スクレイピング前にドメインを検証します。
- ドメインの到達可能性を確認します。
- 明確なエラーメッセージを提供します。
- 一時的なネットワークエラーに対して指数バックオフを使用した再試行メカニズムを実装しています。
- 設定されており、主要なメソッドが失敗した場合に代替スクレイパーにフォールバックします。

## カスタマイズ

Python スクリプト (`deepwiki_to_md/deepwiki_to_md.py`, `deepwiki_to_md/direct_scraper.py`,
`deepwiki_to_md/direct_md_scraper.py`) を編集することで以下をカスタマイズできます：

- コンテンツ抽出に使用する HTML セレクタ (`DirectDeepwikiScraper` 内)。
- Markdown の解析/クリーニングロジック (`DirectMarkdownScraper` 内)。
- HTML から Markdown への変換オプション (`markdownify` の設定)。
- 出力ファイルの命名規則。
- リクエストヘッダーと遅延。

## Markdown から YAML への変換

このツールは、Markdown ファイルを書式を保持したまま YAML 形式に変換する機能も提供しています。これは特に
LLM（大規模言語モデル）にとって最適な読み込み形式である YAML を生成するのに役立ちます。

### 変換ツールの使用方法

コマンドラインインターフェースを使用して Markdown ファイルを YAML に変換できます：

```
python -m deepwiki_to_md.test_chat convert --md "path/to/markdown/file.md"
```

カスタム出力ディレクトリを指定するには：

```
python -m deepwiki_to_md.test_chat convert --md "path/to/markdown/file.md" --output "path/to/output/directory"
```

### Python API の使用

Python コード内で変換関数を直接使用することもできます：

```python
from deepwiki_to_md.md_to_yaml import convert_md_file_to_yaml

# Markdown ファイルを YAML に変換
yaml_file_path = convert_md_file_to_yaml("path/to/markdown/file.md")

# カスタム出力ディレクトリを指定して Markdown ファイルを YAML に変換
yaml_file_path = convert_md_file_to_yaml("path/to/markdown/file.md", "path/to/output/directory")
```

### YAML 形式

変換された YAML ファイルには以下が含まれます：

- `timestamp`: 変換時刻
- `title`: Markdown ファイルの最初のヘッダーから抽出されたタイトル
- `content`: 書式が保持された完全な Markdown コンテンツ
- `links`: Markdown から抽出されたリンクのリスト
- `metadata`: 以下を含む追加情報：
    - `headers`: Markdown 内のすべてのヘッダーのリスト
    - `paragraphs_count`: 段落の数
    - `lists_count`: リストの数
    - `tables_count`: テーブルの数

この構造化された形式により、元の Markdown 書式を保持しながら、LLM がコンテンツを処理し理解しやすくなります。

## ライセンス

このプロジェクトは MIT ライセンスのもとで公開されています。詳細は LICENSE ファイルをご覧ください。
