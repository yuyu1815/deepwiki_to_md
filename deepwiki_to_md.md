# deepwiki_to_md ライブラリ使い方ガイド（Python API）

バージョン: v2.0.3 / 最終更新日: 2026-08-14

## 1. 概要

`deepwiki-to-md` は Next.js/DeepWiki 由来の HTML や RSC データから Markdown を抽出します。コア抽出機能は標準ライブラリのみで動作し、Devin API Chat のみ optional extra を使用します。

```bash
pip install deepwiki-to-md
pip install "deepwiki-to-md[chat]"  # Chat を使う場合
```

## 2. 主な公開 API

`deepwiki` パッケージから次の API を利用できます。

- `ContentExtractor`
  - `extract_from_html(html: str, source: Optional[str] = None) -> str`
  - `extract_from_url(url: str) -> str`
- `split_markdown_by_h1(md: str) -> List[Dict[str, str]]`
- `sanitize_filename(name: str) -> str`
- `save_markdown_to_library(markdown: str, url: str, base_dir: str) -> Dict[str, Any]`

リポジトリ検索 API はトップレベルモジュールからインポートします。`deepwiki` からは re-export されていません。

```python
from search_repository import API_URL, search_repositories
```

## 3. HTML 文字列から抽出

```python
from deepwiki import ContentExtractor

html = """
<!doctype html>
<html>...</html>
"""

extractor = ContentExtractor()
markdown = extractor.extract_from_html(html)
print(markdown)
```

## 4. URL から抽出して保存

```bash
deepwiki-to-md https://deepwiki.com/microsoft/vscode/some-page --path ./.deepwiki
```

```python
from deepwiki import ContentExtractor, save_markdown_to_library

url = "https://deepwiki.com/microsoft/vscode/some-page"
base_dir = "./.deepwiki"

extractor = ContentExtractor()
markdown = extractor.extract_from_url(url)
result = save_markdown_to_library(markdown, url, base_dir)

for path in result["saved_files"]:
    print(path)
print(result["library_file"])
```

保存時は H1 ごとに Markdown を分割し、ファイル名を安全な形式に変換します。URL が不正な場合などは `ConfigError` が送出されます。

## 5. 公開リポジトリ検索

```python
from search_repository import API_URL, search_repositories

print(API_URL)
result = search_repositories("Gemini")
for item in result.get("indices", [])[:5]:
    print(item.get("repo_name"), item.get("stargazers_count"))
```

HTTP エラー、ネットワーク障害、JSON 解析失敗では `RuntimeError` が送出されます。

## 6. Devin API Chat

Chat には `requests` と `websockets` が必要です。

```bash
pip install "deepwiki-to-md[chat]"
```

設定 JSON は必須で、`headers` と `body_template` の両オブジェクトを含めます。`user_query`、`repo_names`、`query_id`、`use_deep_research` は送信時に上書きされます。

```json
{
  "headers": {
    "Accept": "*/*",
    "Origin": "https://deepwiki.com",
    "Referer": "https://deepwiki.com/"
  },
  "body_template": {
    "engine_id": "multihop",
    "keywords": [],
    "additional_context": "",
    "use_notes": false,
    "generate_summary": false
  }
}
```

```python
import asyncio
import json

from chat import ChatResult, load_config, send_chat_message


async def main() -> None:
    config = load_config("wiki_tests/config.json")
    if not config:
        raise SystemExit("完全な設定ファイルが必要です")

    result: ChatResult = await send_chat_message(
        wiki_url="https://deepwiki.com/microsoft/vscode",
        message="What is the purpose of this repository?",
        config=config,
        use_deep_research=False,
    )
    print(result)
    print(result.response_message)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
```

`ChatResult` は `dict` を継承し、次の主な属性を提供します。

- `sent_message`
- `response_message`
- `status_code`
- `reference_files`
- `reference_file_contents`
- `wiki_url`
- `use_deep_research`
- `to_dict()`

## 7. サンプルスクリプト

リポジトリ直下で `PYTHONPATH=src` を設定して実行します。

- `wiki_tests/extract_from_html_string.py`: ローカル HTML から抽出
- `wiki_tests/extract_from_url_and_save.py`: URL から抽出して保存
- `wiki_tests/search_repositories_example.py`: 公開インデックス検索
- `wiki_tests/chat_example.py`: Devin API Chat（`[chat]` と設定 JSON が必要）

PowerShell の例:

```powershell
$env:PYTHONPATH="src"
python wiki_tests/extract_from_html_string.py
```

## 8. ライセンス

MIT License
