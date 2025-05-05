# Deepwiki to Markdown コンバーター

> **English version of this document is available at [README.md](./README.md).**

Deepwikiサイトのコンテンツをスクレイピングし、Markdown形式に変換するPythonツールです。多様なスクレイピング戦略と、スクレイピングしたデータを処理するためのユーティリティ機能を提供します。

## 特徴

- 複数の戦略を使用してDeepwikiサイトからコンテンツをスクレイピング：
    - 直接Markdownフェッチング（デフォルト）
    - HTML直接スクレイピングと変換
    - シンプルな静的フォールバック
- 指定されたUI要素からナビゲーション項目を抽出してライブラリを横断
- `markdownify`を使用してHTMLコンテンツをMarkdown形式に変換
- 変換されたファイルを整理されたディレクトリ構造で保存
- 一度の実行で複数のライブラリをスクレイピング可能
- ドメイン検証、到達可能性チェック、リトライメカニズムを含むエラーハンドリング
- フォーマットを保持したままMarkdownファイルをYAML形式に変換するユーティリティを提供
- スクレイピングされたMarkdownファイル内のリンクを修正するユーティリティを提供
- Seleniumを使用したチャットインターフェースからのレスポンススクレイピングをサポート

## 要件

- Python 3.6以上
- 必要なPythonパッケージ（`requirements.txt`を参照）：
    - `requests`
    - `beautifulsoup4`
    - `argparse`
    - `markdownify`
    - `selenium`（チャットスクレイピング機能に必要）
    - `webdriver-manager`（チャットスクレイピング機能に必要）
    - `pyyaml`（MarkdownからYAMLへの変換機能に必要）

## インストール

### 方法1：PyPIからインストール

```bash
pip install deepwiki-to-md
```

これにより、setup.pyにリストされているコア依存関係がインストールされます。selenium、webdriver-manager、pyyamlはrequirements.txtにリストされていますが、setup.pyのinstall_requiresには含まれていないことに注意してください。チャットスクレイピングやYAML変換機能が必要な場合は、これらを手動でインストールするか、requirements.txtを含むソースからインストールする必要があります。

### 方法2：ソースからインストール

このリポジトリをクローンします：

```bash
git clone https://github.com/yourusername/deepwiki_to_md.git
cd deepwiki_to_md
```

requirements.txtからすべての依存関係を含め、開発モードでパッケージをインストールします：

```bash
pip install -e . -r requirements.txt
```

## 使用方法

### 基本的な使用法（コマンドライン）

PyPIからインストールした場合、コマンドラインツールを使用できます：

```bash
deepwiki-to-md "https://deepwiki.com/library_path"
```

または明示的なパラメータを使用：

```bash
deepwiki-to-md --library "library_name" "https://deepwiki.example.com/library_path"
```

ソースからインストールした場合、スクリプトを直接実行できます：

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/library_path"
```

または明示的なパラメータを使用：

```bash
python -m deepwiki_to_md.run_scraper --library "library_name" "https://deepwiki.example.com/library_path"
```

注意：出力ディレクトリは、コマンドが実行される現在の作業ディレクトリに作成されます（パッケージのインストールディレクトリではありません）。

### Python APIの使用

DeepwikiScraperクラスを直接Pythonコードで使用することもできます：

```python
from deepwiki_to_md import DeepwikiScraper
# 直接使用するために特定のスクレイパークラスをインポート（必要に応じて）
from deepwiki_to_md.direct_scraper import DirectDeepwikiScraper  # HTML -> MDの場合
from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper  # 直接MDの場合

# スクレイパーインスタンスを作成（デフォルトではDirectMarkdownScraperが使用される）
scraper = DeepwikiScraper(output_dir="MyDocuments")

# デフォルト（DirectMarkdownScraper）を使用してライブラリをスクレイプ
scraper.scrape_library("python", "https://deepwiki.com/python/cpython")

# 別の出力ディレクトリを持つ別のスクレイパーを作成
other_scraper = DeepwikiScraper(output_dir="OtherDocuments")

# 別のライブラリをスクレイプ（デフォルトではDirectMarkdownScraperを使用）
other_scraper.scrape_library("javascript", "https://deepwiki.example.com/javascript")

# --- DirectDeepwikiScraperを明示的に使用（HTMLからMarkdownへ）---
# DirectDeepwikiScraperを明示的に使用するスクレイパーインスタンスを作成
# このスクレイパーはHTMLをフェッチしてMarkdownに変換します
html_scraper = DeepwikiScraper(
    output_dir="HtmlScrapedDocuments",
    use_direct_scraper=True,  # DirectDeepwikiScraperを有効化
    use_alternative_scraper=False,  # 明確にするためにフォールバックを無効化
    use_direct_md_scraper=False  # DirectMarkdownScraperを無効化
)
html_scraper.scrape_library("go", "https://deepwiki.com/go")

# --- DirectMarkdownScraperを明示的に使用（直接Markdownフェッチング）---
# DirectMarkdownScraperを明示的に使用するスクレイパーインスタンスを作成
# これはすでにデフォルトですが、明確にするため、または他のデフォルトが変更された場合に指定できます
md_scraper = DeepwikiScraper(
    output_dir="DirectMarkdownDocuments",
    use_direct_scraper=False,
    use_alternative_scraper=False,
    use_direct_md_scraper=True  # DirectMarkdownScraperを有効化（これがデフォルト）
)
md_scraper.scrape_library("rust", "https://deepwiki.com/rust")

# --- 個別の直接スクレイパーを直接使用 ---
# これらのクラスは特定のページまたはページのリストをスクレイピングするために独立して使用できます

# DirectDeepwikiScraperインスタンスを作成（HTMLからMarkdown）
direct_html_scraper = DirectDeepwikiScraper(output_dir="DirectHtmlScraped")

# 特定のページを直接スクレイプ（HTMLからMarkdown）
direct_html_scraper.scrape_page(
    "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
    "python_bytecode",  # 出力フォルダのライブラリ名/パス部分
    save_html=True  # オプションで元のHTMLを保存
)

# DirectMarkdownScraperインスタンスを作成（直接Markdownフェッチング）
direct_md_scraper = DirectMarkdownScraper(output_dir="DirectMarkdownFetched")

# 特定のページを直接Markdownとしてスクレイプ
direct_md_scraper.scrape_page(
    "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
    "python_bytecode"  # 出力フォルダのライブラリ名/パス部分
)
```

### コマンドライン引数

`deepwiki-to-md`または`python -m deepwiki_to_md.run_scraper`の場合：

- `library_url`：スクレイプするライブラリのURL（位置引数として指定可能）。
- `--library`, `-l`：スクレイプするライブラリの名前とURL。異なるライブラリに対して複数回指定できます。形式：
  `--library NAME URL`。
- `--output-dir`, `-o`：Markdownファイルの出力ディレクトリ（デフォルト：`Documents`）。
- `--use-direct-scraper`：DirectDeepwikiScraper（HTMLからMarkdownへの変換）を使用。両方が指定された場合、
  `--use-direct-md-scraper`よりも優先されます。
- `--no-direct-scraper`：DirectDeepwikiScraperを無効にする。
- `--use-alternative-scraper`：プライマリメソッドが失敗した場合、direct_scraper.pyからscrape_deepwiki関数をフォールバックとして使用（デフォルト：True）。
- `--no-alternative-scraper`：代替スクレイパーのフォールバックを無効にする。
- `--use-direct-md-scraper`：DirectMarkdownScraper（Markdownを直接フェッチ）を使用。スクレイパータイプが明示的に指定されていない場合のデフォルト動作です。
- `--no-direct-md-scraper`：DirectMarkdownScraperを無効にする。

#### スクレイパーの優先順位：

1. `--use-direct-scraper`が指定されている場合、DirectDeepwikiScraper（HTMLからMarkdown）が使用されます。
2. `--use-direct-md-scraper`が指定されている場合（かつ`--use-direct-scraper`
   が指定されていない場合）、DirectMarkdownScraper（直接Markdown）が使用されます。
3. どちらも指定されていない場合、デフォルトではDirectMarkdownScraper（直接Markdown）が使用されます。
4. `--use-alternative-scraper`フラグは、選択されたプライマリスクレイパー内のフォールバックメカニズムを制御します。

### 例（コマンドライン）

簡略化した使用法（デフォルトではDirectMarkdownScraperを使用）：

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython"
# または、pipでインストールした場合：deepwiki-to-md "https://deepwiki.com/python/cpython"
```

明示的なパラメータを使用して単一のライブラリをスクレイプ：

```bash
python -m deepwiki_to_md.run_scraper --library "python" "https://deepwiki.com/python/cpython"
```

複数のライブラリをスクレイプ：

```bash
python -m deepwiki_to_md.run_scraper --library "python" "https://deepwiki.com/python/cpython" --library "vscode" "https://deepwiki.com/microsoft/vscode"
```

カスタム出力ディレクトリを指定：

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython" --output-dir "MyDocuments"
```

明示的にDirectMarkdownScraper（直接Markdown）を使用：

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython" --use-direct-md-scraper
```

明示的にDirectDeepwikiScraper（HTMLからMarkdown）を使用：

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython" --use-direct-scraper
```

代替スクレイパーのフォールバックを無効にする：

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython" --no-alternative-scraper
```

### run_direct_scraper.pyの使用

run_direct_scraper.pyスクリプトを使用することもできます。これは、DirectDeepwikiScraper（HTMLからMarkdown）専用の簡略化されたエントリーポイントです：

```bash
python -m deepwiki_to_md.run_direct_scraper "https://deepwiki.com/python/cpython"
# または明示的なパラメータを使用：
python -m deepwiki_to_md.run_direct_scraper --library "python" "https://deepwiki.com/python/cpython"
# HTMLも保存する場合：
python -m deepwiki_to_md.run_direct_scraper "https://deepwiki.com/python/cpython" --save-html
```

run_direct_scraper.pyの引数：

- `library_url`：ライブラリのURL（位置引数）。
- `--library`, `-l`：ライブラリ名とURL（複数可）。
- `--output-dir`, `-o`：出力ディレクトリ（デフォルト：DynamicDocuments）。
- `--save-html`：MarkdownとともにオリジナルのHTMLファイルを保存。

## 出力構造

変換されたMarkdownファイルは次のディレクトリ構造で保存されます：

```
<output_dir>/
├── <library_name1>/
│   └── md/
│       ├── <page_name1>.md
│       ├── <page_name2>.md
│       └── ...
│   └── html/ # DirectDeepwikiScraperで--save-htmlを使用した場合のみ
│       ├── <page_name1>.html
│       ├── <page_name2>.html
│       └── ...
├── <library_name2>/
│   └── md/
│       ├── <page_name1>.md
│       ├── <page_name2>.md
│       └── ...
└── ...
```

- `<output_dir>`は`--output-dir`で指定されたディレクトリ（デフォルト：run_scraper.pyの場合は`Documents`
  、run_direct_scraper.pyの場合は`DynamicDocuments`）。
- `<library_name>`はライブラリに提供された名前（またはURLパスから推測されたもの）。
- Deepwikiサイトの各ページは、mdサブディレクトリ内の個別の.mdファイルとして保存されます。
- DirectDeepwikiScraperで`--save-html`オプションを使用した場合、元のHTMLはhtmlサブディレクトリに保存されます。

## 動作の仕組み

このツールは、互換性と出力品質を最大化するために異なるスクレイピング戦略を提供します：

### 1. 直接Markdownスクレイピング（DirectMarkdownScraper - デフォルト）

**優先度：** 最高（他のスクレイパーが明示的に選択されていない場合のデフォルト）。

**方法：** Deepwikiサイトの基盤となるデータソースまたはAPIから生のMarkdownコンテンツを直接フェッチします。これは、内部アプリケーションリクエストを模倣した特殊なヘッダーを持つリクエストを送信することで行われます。

**プロセス：**

- Markdownデータを取得するように設計されたリクエストを送信（特定のAcceptヘッダーやクエリパラメータを使用）
- レスポンスを解析してMarkdownコンテンツを抽出
- 抽出されたMarkdownに最小限のクリーニングを実行
- レベル2の見出し（##）に基づいてコンテンツを複数のファイルに分割
- クリーニングされ分割されたMarkdownコンテンツを直接.mdファイルに保存

**利点：** 著者が意図した通りの元のフォーマットと構造を保持し、最高品質のMarkdownを生成します。

### 2. 直接HTMLスクレイピング（DirectDeepwikiScraper）

**優先度：** 中（`--use-direct-scraper`が指定されている場合に使用）。

**方法：** 標準ブラウザリクエストを模倣するヘッダーを使用してDeepwikiサイトに接続し、完全にレンダリングされたHTMLページをフェッチします。

**プロセス：**

- `scrape_deepwiki`関数を使用してページの完全なHTMLをフェッチ
- BeautifulSoupを使用してHTMLを解析
- 潜在的なCSSセレクタのリストを使用してメインコンテンツ領域を特定
- markdownifyライブラリを使用して選択されたHTMLコンテンツをMarkdownに変換
- 変換されたMarkdownを保存

**利点：** 直接Markdownフェッチングが失敗または利用できない場合、基本的な静的スクレイピングよりも堅牢です。

### 3. 代替スクレイパーフォールバック

**優先度：** 最低（`--use-alternative-scraper`が有効な場合にフォールバックとして使用）。

**方法：** ページHTMLを確実にフェッチするように設計された、特定のヘッダーを持つシンプルな静的リクエストメカニズム。

## MarkdownからYAMLへの変換ユーティリティ

このツールは、フォーマットを保持したままMarkdownファイルをYAML形式に変換するユーティリティを提供します。これは、スクレイピングされたコンテンツをLLM（大規模言語モデル）向けに処理する際に特に便利です。

### 変換ツールの使用（コマンドライン）

```bash
python -m deepwiki_to_md.chat convert --md "path/to/markdown/file.md"
# またはエントリポイントが設定されている場合：
python -m deepwiki_to_md.test_chat convert --md "path/to/markdown/file.md"
```

カスタム出力ディレクトリを指定するには：

```bash
python -m deepwiki_to_md.chat convert --md "path/to/markdown/file.md" --output "path/to/output/directory"
```

### Python APIの使用（MarkdownからYAML）

```python
from deepwiki_to_md.md_to_yaml import convert_md_file_to_yaml, markdown_to_yaml

# MarkdownファイルをYAMLに変換
yaml_file_path = convert_md_file_to_yaml("path/to/markdown/file.md")

# カスタム出力ディレクトリを使ってMarkdownファイルをYAMLに変換
yaml_file_path = convert_md_file_to_yaml("path/to/markdown/file.md", "path/to/output/directory")

# または、Markdown文字列を直接YAML文字列に変換
markdown_string = "# 私のドキュメント\n\nこれはコンテンツです。"
yaml_string = markdown_to_yaml(markdown_string)
print(yaml_string)
```

### YAML形式

変換されたYAMLファイルには、元のMarkdownコンテンツを埋め込みながらドキュメントの構造化された表現が含まれます：

```yaml
timestamp: 'YYYY-MM-DD HH:MM:SS'  # 変換のタイムスタンプ
title: 抽出されたドキュメントタイトル  # 最初のH1/H2ヘッダーから抽出されたタイトル
content: |
  # オリジナルタイトル
  ## セクション1

  セクション1の内容。

  * リストアイテム1
  * リストアイテム2

  print("コード")

  [リンクテキスト](url)

  ## セクション2

  セクション2の内容。
  ...                              # 元のMarkdownコンテンツがすべて保持されます
links:
  - text: リンクテキスト
    url: url                       # Markdownから抽出されたリンクのリスト
images: [ ]                         # 抽出された画像のリスト（現在は空）
metadata:
  headers: # すべての見出しテキストのリスト
    - オリジナルタイトル
    - セクション1
    - セクション2
    ...
  paragraphs_count: 5              # 段落の数
  lists_count: 1                   # リストの数
  tables_count: 0                  # テーブルの数
```

## Markdownリンク修正ユーティリティ

このツールは、生成された.mdファイルに対してリンク修正ユーティリティを自動的に実行します。このユーティリティは`[Text](URL)`
形式のMarkdownリンクを見つけ、それを`[Text]()`に置き換えます。

### リンク修正ツールの使用（コマンドライン）

```bash
python -m deepwiki_to_md.fix_markdown_links "path/to/your/markdown/directory"
```

### Python APIの使用（リンク修正）

```python
from deepwiki_to_md.fix_markdown_links import fix_markdown_links

# ディレクトリ内のすべてのmarkdownファイルのリンクを修正
fix_markdown_links("path/to/your/markdown/directory")
```

## チャットスクレイピング機能（Seleniumが必要）

このツールには、Seleniumを使用してチャットインターフェースと対話し、レスポンスを保存する機能が含まれています。

### チャットスクレイパーの使用（コマンドライン）

```bash
python -m deepwiki_to_md.chat --url "https://deepwiki.com/some_chat_page" --message "あなたのメッセージ" --wait 10 --debug --format "html,md,yaml" --output "MyChatResponses" --deep
```

chat.pyの引数：

- `--url`：チャットインターフェースのURL。
- `--message`：送信するメッセージ。
- `--selector`：チャット入力のCSSセレクタ（デフォルト：textarea）。
- `--button`：送信ボタンのCSSセレクタ（デフォルト：button）。
- `--wait`：レスポンスを待つ時間（秒）（デフォルト：30）。
- `--debug`：デバッグモードを有効にする。
- `--output`：出力ディレクトリ（デフォルト：ChatResponses）。
- `--deep`：「ディープリサーチ」モードを有効にする（特定のインターフェースに特化）。
- `--headless`：ヘッドレスモードでブラウザを実行。
- `--format`：出力形式：html、md、yaml、またはカンマ区切りリスト（デフォルト：html）。

注意：チャットスクレイパーはSeleniumを使用するため、互換性のあるブラウザがインストールされている必要があります。

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細については、LICENSEファイルを参照してください。