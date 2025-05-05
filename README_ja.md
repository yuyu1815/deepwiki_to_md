# Deepwiki to Markdown コンバーター

> **この文書の英語版は [README.md](./README.md) で入手できます。**

Deepwikiサイトからコンテンツをスクレイピングし、Markdown形式に変換するためのPythonツールです。様々なスクレイピング戦略と、スクレイピングされたデータを処理するためのユーティリティ関数を提供します。

## 特徴

- 複数の戦略を使用してDeepwikiサイトからコンテンツをスクレイピング：
  - 直接Markdownフェッチング（デフォルト）
  - 直接HTMLスクレイピングと変換
  - シンプルな静的フォールバック
- 指定されたUI要素からナビゲーション項目を抽出してライブラリを横断
- `markdownify`を使用してHTMLコンテンツをMarkdown形式に変換
- 変換されたファイルを整理されたディレクトリ構造で保存
- 一度の実行で複数のライブラリをスクレイピング可能
- ドメイン検証、到達可能性チェック、再試行メカニズムによるエラー処理
- フォーマットを保持しながらMarkdownファイルをYAML形式に変換するユーティリティ
- スクレイピングされたMarkdownファイル内のリンクを修正するユーティリティ
- Seleniumを使用したチャットインターフェースからのレスポンスのスクレイピングをサポート

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

### オプション1：PyPIからインストール

```bash
pip install deepwiki-to-md
```

これにより、setup.pyにリストされているコア依存関係がインストールされます。selenium、webdriver-manager、pyyamlはrequirements.txtにリストされていますが、setup.pyのinstall_requiresには含まれていません。チャットスクレイピングやYAML変換機能が必要な場合は、これらを手動でインストールするか、requirements.txtを含むソースからインストールする必要があるかもしれません。

### オプション2：ソースからインストール

このリポジトリをクローンします：

```bash
git clone https://github.com/yourusername/deepwiki_to_md.git
cd deepwiki_to_md
```

開発モードでパッケージをインストールし、requirements.txtからすべての依存関係を含めます：

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

注意：出力ディレクトリは、コマンドが実行されるカレントワーキングディレクトリに作成され、パッケージのインストールディレクトリには作成されません。

### リポジトリ作成ツール

このパッケージには、メールを設定してフォームを送信することによってリポジトリリクエストを作成するツールも含まれています：

PyPIからインストールした場合、コマンドラインツールを使用できます：

```bash
deepwiki-create --url "https://example.com/repository/create" --email "user@example.com"
```

ヘッドレスモードで実行する場合（ブラウザウィンドウを開かない）：

```bash
deepwiki-create --url "https://example.com/repository/create" --email "user@example.com" --headless
```

ソースからインストールした場合、スクリプトを直接実行できます：

```bash
python -m deepwiki_to_md.create --url "https://example.com/repository/create" --email "user@example.com"
```

### Python APIの使用

DeepwikiScraperクラスをPythonコードで直接使用することもできます：

```python
from deepwiki_to_md import DeepwikiScraper
# 直接使用する場合は特定のスクレイパークラスをインポート
from deepwiki_to_md.direct_scraper import DirectDeepwikiScraper  # HTML -> MD用
from deepwiki_to_md.direct_md_scraper import DirectMarkdownScraper  # 直接MD用
# リポジトリ作成用のRepositoryCreatorクラスをインポート
from deepwiki_to_md.create import RepositoryCreator

# スクレイパーインスタンスを作成（デフォルトではDirectMarkdownScraperが使用される）
scraper = DeepwikiScraper(output_dir="MyDocuments")

# デフォルト（DirectMarkdownScraper）を使用してライブラリをスクレイプ
scraper.scrape_library("python", "https://deepwiki.com/python/cpython")

# 別の出力ディレクトリを持つ別のスクレイパーを作成
other_scraper = DeepwikiScraper(output_dir="OtherDocuments")

# 別のライブラリをスクレイプ（依然としてデフォルトではDirectMarkdownScraperを使用）
other_scraper.scrape_library("javascript", "https://deepwiki.example.com/javascript")

# --- DirectDeepwikiScraperを明示的に使用（HTMLからMarkdownへ）---
# DirectDeepwikiScraperを明示的に使用するスクレイパーインスタンスを作成
# このスクレイパーはHTMLを取得してMarkdownに変換します
html_scraper = DeepwikiScraper(
    output_dir="HtmlScrapedDocuments",
    use_direct_scraper=True,  # DirectDeepwikiScraperを有効化
  use_alternative_scraper=False,  # 明確にするために代替フォールバックを無効化
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

# --- 個々の直接スクレイパーを直接使用 ---
# これらのクラスは特定のページまたはページのリストを独立してスクレイピングするために使用できます

# DirectDeepwikiScraperインスタンスを作成（HTMLからMarkdown）
direct_html_scraper = DirectDeepwikiScraper(output_dir="DirectHtmlScraped")

# 特定のページを直接スクレイプ（HTMLからMarkdown）
direct_html_scraper.scrape_page(
    "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
  "python_bytecode",  # 出力フォルダ用のライブラリ名/パス部分
    save_html=True  # オプションで元のHTMLを保存
)

# DirectMarkdownScraperインスタンスを作成（直接Markdownフェッチング）
direct_md_scraper = DirectMarkdownScraper(output_dir="DirectMarkdownFetched")

# 特定のページを直接Markdownとしてスクレイプ
direct_md_scraper.scrape_page(
  "https://deepwiki.com/python/cpython/2.1-bytecode-interpreter-and-optimization",
  "python_bytecode"  # 出力フォルダ用のライブラリ名/パス部分
)

# --- リポジトリ作成リクエスト用のRepositoryCreatorを使用 ---
# RepositoryCreatorインスタンスを作成
creator = RepositoryCreator(headless=False)  # ブラウザUIなしで実行する場合はheadless=True

try:
  # リポジトリ作成リクエストを送信
  success = creator.create(
    url="https://example.com/repository/create",
    email="user@example.com"
  )

  if success:
    print("リポジトリ作成リクエストが正常に送信されました")
  else:
    print("リポジトリ作成リクエストの送信に失敗しました")
finally:
  # 完了したら必ずブラウザを閉じる
  creator.close()
```

## コマンドライン引数

`deepwiki-to-md`または`python -m deepwiki_to_md.run_scraper`の場合：

- `library_url`：スクレイプするライブラリのURL（位置引数として提供可能）。
- `--library`、`-l`：スクレイプするライブラリ名とURL。異なるライブラリに対して複数回指定可能。フォーマット：
  `--library NAME URL`。
- `--output-dir`、`-o`：Markdownファイルの出力ディレクトリ（デフォルト：Documents）。
- `--use-direct-scraper`：DirectDeepwikiScraper（HTMLからMarkdownへの変換）を使用。両方が指定された場合、
  `--use-direct-md-scraper`よりも優先される。
- `--no-direct-scraper`：DirectDeepwikiScraperを無効化。
- `--use-alternative-scraper`：主要な方法が失敗した場合にフォールバックとしてdirect_scraper.pyのscrape_deepwiki関数を使用（デフォルト：True）。
- `--no-alternative-scraper`：代替スクレイパーフォールバックを無効化。
- `--use-direct-md-scraper`：DirectMarkdownScraper（Markdownを直接フェッチ）を使用。スクレイパータイプが明示的に指定されていない場合のデフォルト動作。
- `--no-direct-md-scraper`：DirectMarkdownScraperを無効化。

スクレイパーの優先順位：

- `--use-direct-scraper`が指定されている場合、DirectDeepwikiScraper（HTMLからMarkdown）が使用される。
- `--use-direct-md-scraper`が指定されている場合（かつ`--use-direct-scraper`
  が指定されていない場合）、DirectMarkdownScraper（直接Markdown）が使用される。
- どちらも指定されていない場合、デフォルトでDirectMarkdownScraper（直接Markdown）が使用される。
- `--use-alternative-scraper`フラグは、選択された主要スクレイパー内のフォールバックメカニズムを制御する。

`deepwiki-create`または`python -m deepwiki_to_md.create`の場合：
- `--url`（必須）：リポジトリ作成ページのURL。
- `--email`（必須）：通知先のメールアドレス。
- `--headless`：ブラウザをヘッドレスモードで実行（UIなし）。

## 例（コマンドライン）

簡略化された使用法（デフォルトでDirectMarkdownScraperを使用）：

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
python -m deepwiki_to_md.run_scraper --library "python" "https://deepwiki.com/python/cpython" --library "microsoft/vscode" "https://deepwiki.com/microsoft/vscode"
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

代替スクレイパーフォールバックを無効化：

```bash
python -m deepwiki_to_md.run_scraper "https://deepwiki.com/python/cpython" --no-alternative-scraper
```

リポジトリ作成ツールの使用：

```bash
deepwiki-create --url "https://example.com/repository/create" --email "user@example.com"
```

ヘッドレスモードでリポジトリ作成ツールを使用：

```bash
deepwiki-create --url "https://example.com/repository/create" --email "user@example.com" --headless
```

### run_direct_scraper.pyの使用

run_direct_scraper.pyスクリプトも使用できます。これは特にDirectDeepwikiScraper（HTMLからMarkdown）用の簡略化されたエントリーポイントです：

```bash
python -m deepwiki_to_md.run_direct_scraper "https://deepwiki.com/python/cpython"
# または明示的なパラメータを使用：
python -m deepwiki_to_md.run_direct_scraper --library "python" "https://deepwiki.com/python/cpython"
# HTMLも保存する場合：
python -m deepwiki_to_md.run_direct_scraper "https://deepwiki.com/python/cpython" --save-html
```

run_direct_scraper.pyの引数：
- `library_url`：ライブラリのURL（位置引数）。
- `--library`、`-l`：ライブラリ名とURL（複数可）。
- `--output-dir`、`-o`：出力ディレクトリ（デフォルト：DynamicDocuments）。
- `--save-html`：Markdownと一緒に元のHTMLファイルを保存。

## 出力構造

変換されたMarkdownファイルは以下のディレクトリ構造で保存されます：

```
<output_dir>/
├── <library_name1>/
│   └── md/
│       ├── <page_name1>.md
│       ├── <page_name2>.md
│       └── ...
│   └── html/ # DirectDeepwikiScraperで--save-htmlが使用された場合のみ
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

- `<output_dir>`は、`--output-dir`で指定されたディレクトリ（デフォルト：run_scraper.pyではDocuments、run_direct_scraper.pyではDynamicDocuments）。
- `<library_name>`はライブラリに提供された名前（または、URLパスから推測された名前）。
- DeepwikiサイトからのEachページは、mdサブディレクトリ内の個別の.mdファイルとして保存される。
- DirectDeepwikiScraperで`--save-html`オプションが使用されている場合、元のHTMLはhtmlサブディレクトリに保存される。

## 仕組み

このツールは、互換性と出力品質を最大化するために異なるスクレイピング戦略を提供します：

### 1. 直接Markdownスクレイピング（DirectMarkdownScraper - デフォルト）

- **優先度**：最高（他のスクレイパーが明示的に選択されない場合、デフォルトで使用される）。
- **方法**
  ：Deepwikiサイトの基礎となるデータソースまたはAPIから生のMarkdownコンテンツを直接取得しようとします。これは、内部アプリケーションリクエストを模倣する特殊なヘッダーを使用したリクエストを送信することで行われます。
- **プロセス**：
  - Markdownデータを取得するように設計されたリクエストを送信（特定のAcceptヘッダーまたはクエリパラメータを使用）
  - レスポンスを解析してMarkdownコンテンツを抽出
  - 抽出されたMarkdownに最小限のクリーニングを実行
  - レベル2の見出し（##）に基づいてコンテンツを複数のファイルに分割
  - クリーニングおよび分割されたMarkdownコンテンツを直接.mdファイルに保存
- **利点**：著者が意図したとおりの元のフォーマットと構造を保持した、最高品質のMarkdownを生成します。

### 2. 直接HTMLスクレイピング（DirectDeepwikiScraper）

- **優先度**：中（`--use-direct-scraper`が指定されている場合に使用される）。
- **方法**：標準的なブラウザリクエストを模倣するヘッダーを使用してDeepwikiサイトに接続し、完全にレンダリングされたHTMLページを取得します。
- **プロセス**：
  - scrape_deepwiki関数を使用してページの完全なHTMLを取得
  - BeautifulSoupを使用してHTMLを解析
  - 潜在的なCSSセレクタのリストを使用してメインコンテンツ領域を識別
  - markdownifyライブラリを使用して選択されたHTMLコンテンツをMarkdownに変換
  - 変換されたMarkdownを保存
- **利点**：直接Markdownフェッチングが失敗するか利用できない場合、基本的な静的スクレイピングよりも堅牢。

### 3. 代替スクレイパーフォールバック

- **優先度**：最低（`--use-alternative-scraper`が有効な場合のフォールバックとして使用される）。
- **方法**：ページのHTMLを確実に取得するように設計された特定のヘッダーを持つよりシンプルな静的リクエストメカニズム。

## MarkdownからYAMLへの変換ユーティリティ

このツールは、フォーマットを保持しながらMarkdownファイルをYAML形式に変換するユーティリティを提供します。これは特に、スクレイピングされたコンテンツをLLM用に処理する際に便利です。

### 変換ツールの使用（コマンドライン）
```bash
python -m deepwiki_to_md.chat convert --md "path/to/markdown/file.md"
# またはコンソールスクリプトエントリーポイントがインストールされている場合：
# deepwiki-chat convert --md "path/to/markdown/file.md"
```

カスタム出力ディレクトリを指定する場合：

```bash
python -m deepwiki_to_md.chat convert --md "path/to/markdown/file.md" --output "path/to/output/directory"
```

### Python APIの使用（MarkdownからYAML）
```python
from deepwiki_to_md.md_to_yaml import convert_md_file_to_yaml, markdown_to_yaml

# MarkdownファイルをYAMLに変換
yaml_file_path = convert_md_file_to_yaml("path/to/markdown/file.md")

# カスタム出力ディレクトリを指定してMarkdownファイルをYAMLに変換
yaml_file_path = convert_md_file_to_yaml("path/to/markdown/file.md", "path/to/output/directory")

# またはMarkdown文字列を直接YAML文字列に変換
markdown_string = "# マイドキュメント\n\nこれはコンテンツです。"
yaml_string = markdown_to_yaml(markdown_string)
print(yaml_string)
```

### YAML形式

変換されたYAMLファイルには、元のMarkdownコンテンツを埋め込みながら、文書の構造化された表現が含まれます：

```yaml
timestamp: 'YYYY-MM-DD HH:MM:SS'  # 変換のタイムスタンプ
title: 抽出されたドキュメントタイトル    # 最初のH1/H2ヘッダーから抽出されたタイトル
content: |
  # オリジナルタイトル
  ## セクション1

  セクション1のコンテンツ。

  * リストアイテム1
  * リストアイテム2

  print("コード")

  [リンクテキスト](url)

  ## セクション2

  セクション2のコンテンツ。
  ...                              # 元のMarkdownコンテンツは完全に保存される
links:
  - text: リンクテキスト
    url: url                       # Markdownから抽出されたリンクのリスト
images: [ ]                         # 抽出された画像のリスト（現在は空）
metadata:
  headers: # すべてのヘッダーテキストのリスト
    - オリジナルタイトル
    - セクション1
    - セクション2
    ...
  paragraphs_count: 5              # 段落の数
  lists_count: 1                   # リストの数
  tables_count: 0                  # テーブルの数
```

## Markdownリンク修正ユーティリティ

このツールは、生成された.mdファイルにリンク修正ユーティリティを自動的に実行します。このユーティリティは、[テキスト](URL)
形式のMarkdownリンクを見つけて、[テキスト]()に置き換えます。

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

このツールには、Seleniumを使用してチャットインターフェースとやり取りし、レスポンスを保存する機能が含まれています。

### チャットスクレイパーの使用（コマンドライン）
```bash
python -m deepwiki_to_md.chat --url "https://deepwiki.com/some_chat_page" --message "あなたのメッセージをここに" --wait 10 --debug --format "html,md,yaml" --output "MyChatResponses" --deep
```

chat.pyの引数：
- `--url`：チャットインターフェースのURL。
- `--message`：送信するメッセージ。
- `--selector`：チャット入力のCSSセレクタ（デフォルト：textarea）。
- `--button`：送信ボタンのCSSセレクタ（デフォルト：button）。
- `--wait`：レスポンス待機時間（秒）（デフォルト：30）。
- `--debug`：デバッグモードを有効化。
- `--output`：出力ディレクトリ（デフォルト：ChatResponses）。
- `--deep`：「Deep Research」モードを有効化（特定のインターフェース向け）。
- `--headless`：ブラウザをヘッドレスモードで実行。
- `--format`：出力形式：html、md、yaml、またはカンマ区切りリスト（デフォルト：html）。

注意：チャットスクレイパーはSeleniumを使用しており、互換性のあるブラウザがインストールされている必要があります。

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細はLICENSEファイルをご覧ください。