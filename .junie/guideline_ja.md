# Project Development Guidelines (deepwiki_to_md)

本ドキュメントは、このリポジトリで開発を行う上でのプロジェクト固有の知見をまとめたものです。一般的なPythonのベストプラクティスは既存の規約に従い、本書では本プロジェクト特有のビルド/設定、テスト実行、実装上の注意点を中心に記載します。

---

## 1. Build / Configuration

- パッケージング/ビルド
  - PEP 517/518 対応。pyproject.toml で setuptools build_meta を使用。
  - Zero external dependencies（標準ライブラリのみ）を前提に設計。
  - 配布物は dist/ にホイール/ソース配布を生成可能。
  - ビルド例:
    - python -m build が入っていない場合は、python -m pip install build
    - python -m build

- インストール（開発）
  - ソースを import 可能にするには以下のいずれかを推奨。
    - 一時的に PYTHONPATH に src を通す: PYTHONPATH=src python -c "import deepwiki_to_md; print(deepwiki_to_md.__name__)"
    - or editable install: python -m pip install -e .[dev]
  - CLI エントリポイント:
    - deepwiki-to-md = "cli:main"（pyproject.toml の [project.scripts]）
    - ローカルから直接呼び出す例: python -m cli input.html

- 実行時ディレクトリ/出力
  - URL入力時は、.deepwiki/<username>/<library>/<section>.md に分割保存し、.deepwiki/<username>/<library>.md にインデックスを生成（src/cli.py）。
  - ローカル HTML 入力時 or stdin 入力時は標準出力へ Markdown を出力（ファイル保存しない）。

- Chat 機能（Devin API 連携）
  - コマンド例:
    - deepwiki-to-md chat --url https://deepwiki.com/microsoft/WSL --message "Explain WSLg Wayland and RDP" --deep-research --config-file config.json
  - 設定ファイル生成ロジック（src/chat.py: load_or_create_config）
    - 指定パスの JSON が存在しなければ、カレントにある deepResearch or test という名前の XML ログから最小限のヘッダ/テンプレートを自動抽出し config.json を作成。
    - 抽出できないときは失敗するため、最初の実行時は必ず該当ログファイルを用意すること。
  - 送受信は HTTP POST と WebSocket を利用。ネットワーク依存のため、CI ではモック化が望ましい。

---

## 2. Testing

- テスト実行ツール
  - pytest と pytest-cov が optional-deps に定義（[project.optional-dependencies].test/dev）。
  - まず開発環境を用意: python -m venv .venv && source .venv/bin/activate
  - 依存導入（最小）: python -m pip install -e .[test]
  - 依存導入（開発一式）: python -m pip install -e .[dev]

- テストディレクトリの注意点（重要）
  - pyproject.toml の pytest 設定では testpaths = ["tests"] となっています。
  - しかし本リポジトリの既存のテスト資材は test/ ディレクトリ配下に存在します（例: test/chat.py）。
  - そのため、デフォルトの pytest 実行では tests/ を探索してテストが見つからない警告が出ます。
  - 対応策は次のいずれか:
    1) 実行時に testpaths を無視して明示ディレクトリを指定: pytest test
    2) 一時的に PYTHONPATH=src を指定して import を解決しつつ、再帰探索に任せる
    3) もしくは tests/ ディレクトリを作り、そこにテストを置く（推奨運用）

- import の解決
  - 本プロジェクトは src レイアウト。テスト実行時に deepwiki_to_md, cli, chat を import するために、
    - PYTHONPATH=src をセットするか、
    - pip install -e . を行う必要があります。

- カバレッジ設定の注意
  - [tool.pytest.ini_options] addopts に --cov=src.html_formatter, --cov=src.deepwiki_to_md が含まれます。
  - src/html_formatter.py は存在しないため、CoverageWarning が出ます。必要に応じて設定を更新してください。

- 参考: 動作確認した最小テストの実行例
  - 一時的に tests/test_smoke.py を作成し、以下コマンドで成功を確認（実行後ファイルは削除済）。
    - 作成テスト（概要）:
      - deepwiki_to_md の import ができること
      - cli.main(["--help"]) が SystemExit(0) を返し、ヘルプに "Extract Markdown" が含まれること
    - 実行コマンド:
      - PYTHONPATH=src pytest -q
    - 実行結果（抜粋）:
      - 2 passed in 0.04s

- 既存 test/ ディレクトリのファイルについて
  - test/chat.py はネットワークアクセス（requests, websockets）を前提としています。CI ではモック化が必須です。
  - test/config.json, test/out.json は補助データ。実行環境によっては存在しない/無効な可能性があるため、単体テストには依存しない設計が望ましいです。

- 新しいテストの追加指針
  - 単体テストでは HTTPClient.fetch_url, StrategyManager.extract_content, split_markdown_by_h1, sanitize_filename 等の純粋ロジックを優先的に検証。
  - ネットワークや I/O はモック（unittest.mock / pytest-mock）で代替。例:
    - monkeypatch で HTTPClient.fetch_url をスタブ化
    - tmp_path を使って CLI のファイル出力を検証

---

## 3. Additional Development Information

- コードスタイル/静的解析
  - black/isort/mypy/flake8 を採用（設定は pyproject.toml）。
  - mypy は厳しめ（disallow_untyped_defs など）。公開関数は型注釈必須。
  - ログには logging を使用。print は極力避ける（CLI のユーザ出力は許容）。

- 設計方針
  - 合成優先（StrategyManager と複数の ExtractionStrategy 実装）。
  - 例外は独自例外（ExtractorError/HTTPError/ContentError/ConfigError）で明示化。
  - HTML/JSON 解析は失敗に強い正規表現/構造チェックを併用。

- CLI の出力設計
  - URL 入力時のみファイル保存。ファイル名は sanitize_filename で安全化、Markdown は H1 区切りで分割（split_markdown_by_h1）。
  - deepwiki.com/<username>/<library> のパス構造を前提にドキュメントを配置し、ライブラリインデックスを生成。

- 既知の落とし穴
  - pytest の testpaths=tests と実ファイル test/ の不整合。
  - Coverage 設定が実ファイル構成と一致していない（src.html_formatter）。
  - chat 機能は外部サービス依存で、ログ XML からの初期設定生成が必要。

- 推奨ワークフロー
  - 仮想環境: python -m venv .venv && source .venv/bin/activate
  - 依存導入: python -m pip install -e .[dev]
  - フォーマット/静的解析: black . && isort . && flake8 && mypy src
  - テスト: PYTHONPATH=src pytest -q または pytest test -q

---

## 4. Python 規約（本プロジェクト適用の要点）

- 明快・清潔なコード、PEP8準拠（black/flake8）
- with でリソース管理、例外は明示的に捕捉
- Dict/List 等は typing を明示
- 継承より合成、関数は短く明確に
- 公開コードは英語 docstring、必要部分にテスト
- 可変グローバルは NG、仮想環境推奨
- enumerate()/zip()、内包表記、f-string 活用
- dataclass 活用、命名規則: snake_case / PascalCase / UPPER_CASE
- 循環 import 回避、標準ライブラリ優先
- 例外は logging で出力、print() は避ける（CLI 出力は可）
- 修正は慎重に、影響・実行確認を必須
- バグ時は原因・妥当性を分析
- データ行数/バイト数が多い場合は処理回避
- コメントは日本語
- コードと README はセットで更新

- コメント
  - コメントで編集する際は、削除した項目についての言及や言い回しを避ける。
  - 新たに開発に参加する人がすぐ理解できる、簡潔で具体的なコメントを心がける。
