# deepwiki_to_md ライブラリ使い方ガイド（Python API）

バージョン: v2.0.0 / 最終更新日: 2025-09-19

本書は deepwiki_to_md を Python ライブラリとして利用する方法を、日本語で丁寧に解説します。必要に応じて CLI 例も本書内に併記します。

---

## 1. 概要

- 目的: Next.js/DeepWiki 由来の HTML/スクリプトから、人が読めるテキストを抽出する。
- 特長:
  - 複数の抽出戦略（Strategy パターン）で堅牢に対応。
  - 依存は標準ライブラリのみ。
  - 小さなヘルパー関数群で、H1 分割やファイル名のサニタイズを提供。

---

## 2. 主な公開 API

- ContentExtractor
  - `extract_from_html(html: str, source: Optional[str] = None) -> str`
  - `extract_from_url(url: str) -> str`
- split_markdown_by_h1
  - `split_markdown_by_h1(md: str) -> List[Dict[str, str]]`
- sanitize_filename
  - `sanitize_filename(name: str) -> str`
- リポジトリ検索（Devin API）
  - `search_repositories(search_term: str = "Gemini") -> Dict[str, Any]`
  - 定数: `API_URL`
  - インポートは以下の2通りが可能です。
    - `from search_repository import search_repositories, API_URL`
    - `from deepwiki import search_repositories, API_URL`（re-export）

---

## 3. クイックスタート

### 3.1 HTML 文字列から抽出
```python
from deepwiki import ContentExtractor

html = """
<!doctype html>
<html>...</html>
"""

extractor = ContentExtractor()
md = extractor.extract_from_html(html)
print(md)
```

### 3.2 URL から抽出
```python
from deepwiki import ContentExtractor

url = "https://deepwiki.com/microsoft/vscode"
#url = "/microsoft/vscode" or "microsoft/vscode"
extractor = ContentExtractor()
md = extractor.extract_from_url(url)
print(md)
```

## 4. MD をファイルに保存する例（Python API）

CLI の次のコマンドと同等のことを Python から実行できます。

CLI 例:
```sh
# URL 入力のときのみ、.deepwiki 配下に分割保存されます
deepwiki-to-md https://deepwiki.com/microsoft/vscode/some-page --path ./.deepwiki
```

Python 例:

```python
from deepwiki import ContentExtractor, save_markdown_to_library

url = "https://deepwiki.com/microsoft/vscode"
# url = "/microsoft/vscode" or "microsoft/vscode"
base_dir = ""  # --path に相当（省略可）

extractor = ContentExtractor()
md = extractor.extract_from_url(url)

result = save_markdown_to_library(md, url, base_dir)
print("saved files:")
for p in result["saved_files"]:
    print(" -", p)
print("library index:", result["library_file"])  # .deepwiki/<username>/<library>.md
```

注意事項:
- URL から抽出した場合のみ、ファイルへ保存する設計を推奨（CLI と同じ思想）。
- 保存時は H1 ごとに分割し、ファイル名は sanitize_filename() で安全化されます。
- 保存先のルートは base_dir（デフォルト .deepwiki）。実際の出力先は .deepwiki/<username>/<library>/ になります。
- ライブラリレベルの索引ファイル .deepwiki/<username>/<library>.md も生成されます。
- エラー時（URL 形式不正など）は ConfigError を送出します。

## 6. リポジトリ検索 API（Devin 公開インデックス）

公開インデックスを検索する小さなユーティリティを提供しています。CLI の `search` サブコマンドで利用されているものと同等です。

```python
# どちらの import でも動作します。
from deepwiki import search_repositories, API_URL
# from search_repository import search_repositories, API_URL

print(API_URL)  # => https://api.devin.ai/ada/list_public_indexes

result = search_repositories("Gemini")
indices = result.get("indices", [])
print(len(indices), "results")
for item in indices[:5]:
    # 代表的なフィールド（APIの仕様に依存）
    print(item.get("repo_name"), item.get("stargazers_count"))
```

エラー時の挙動:
- HTTP ステータスが 200 以外、ネットワーク障害、JSON 解析失敗のいずれかで `RuntimeError` を送出します。

---

## 7. 例外とログ

- ライブラリは、主に `ExtractorError`（およびその派生）を用いて例外を明示します。
- ネットワーク/JSON 失敗などは `RuntimeError` を送出します（search_repositories）。
- 自動処理時は `logging` で警告/例外を記録し、ユーザー向けの標準出力は必要最低限にしてください。

---

## 8. 設計メモ（メンテ用の短い要点）

- Strategy パターンで実装（例: NextJSPushStrategy）。
- 早期リターンでネストを浅くし、6ヶ月先でも読みやすい構造を維持します。
- 新規戦略の追加手順（概要）:
  1) `ExtractionStrategy` を継承
  2) `can_handle()` と `extract_content()` を実装
  3) `StrategyManager` のデフォルト登録に追加

---

## 9. ライセンス

MIT License


---

## 10. サンプルスクリプト（wiki_tests 配下）

以下は、Python から1つずつ丁寧に動かせる最小サンプルです。実行時はリポジトリ直下で PYTHONPATH=src を指定してください。

- extract_from_html_string.py（ローカルHTML→Markdown 抽出）
  - 入力: wiki_tests/test_deepwiki.html
  - 実行例:
    - macOS/Linux: PYTHONPATH=src python wiki_tests/extract_from_html_string.py
    - Windows (PowerShell): $env:PYTHONPATH="src"; python wiki_tests/extract_from_html_string.py

- extract_from_url_and_save.py（URL から抽出→.deepwiki に分割保存）
  - 実行例:
    - PYTHONPATH=src python wiki_tests/extract_from_url_and_save.py \
      --url https://deepwiki.com/microsoft/vscode/some-page \
      --path ./.deepwiki

- search_repositories_example.py（公開インデックス検索: search_repositories）
  - 実行例:
    - PYTHONPATH=src python wiki_tests/search_repositories_example.py --search Gemini [--devlog]

- chat_example.py（Devin API チャット）
  - 事前条件: config.json を用意、依存: pip install requests websockets
  - 実行例:
    - PYTHONPATH=src python wiki_tests/chat_example.py \
      --url https://deepwiki.com/microsoft/vscode/some-page \
      --message "質問内容" \
      --config-file ./config.json \
      --deep-research

### ChatResult（チャット結果オブジェクト）

chat ヘルパーの send_chat_message は ChatResult（dict 継承）を返します。JSON のままだと見づらいという要望に応え、オブジェクト型での属性アクセスを提供しています。

- 主なプロパティ
  - sent_message: 送信したメッセージ（str）
  - response_message: 応答本文（Optional[str]）
  - status_code: ステータスコード（Any）
  - reference_files: 参照ファイルのリスト（List[str]）
  - reference_file_contents: 参照ファイルの内容（Dict[str, str]）
  - to_dict(): 辞書として取得（互換目的）

- 利用例

```python
import asyncio
import json
from chat import load_config, send_chat_message, ChatResult


async def main() -> None:
    config = load_config('wiki_tests/config.json')
    if not config:
        raise SystemExit('config missing')
    result: ChatResult = await send_chat_message(
        # wiki_url = "/microsoft/vscode" or "microsoft/vscode",
        wiki_url='https://deepwiki.com/microsoft/vscode',
        message='What is the purpose of this repository?',
        config=config,
        use_deep_research=False,
    )

    # オブジェクト表示（推奨）
    print(result)  # __str__ により要約表示
    print(result.response_message or '<empty>')  # プロパティアクセス

    # JSON でのデバッグ/相互運用も可能
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
```
