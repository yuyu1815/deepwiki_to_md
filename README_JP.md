# deepwiki-to-md

Next.js/DeepWiki 由来の HTML から Markdown を抽出する CLI / Python ライブラリです。コア抽出機能は Python 標準ライブラリのみで動作し、Chat 機能は optional extra として提供します。

- CLI: `deepwiki-to-md`
- 必要要件: Python 3.8.1+

## インストール

コア抽出機能:

```bash
pip install deepwiki-to-md
```

Chat 機能（`requests` と `websockets` を含む）:

```bash
pip install "deepwiki-to-md[chat]"
```

## 使い方

### HTML 文字列から抽出

```bash
echo "<html>...</html>" | deepwiki-to-md
```

```python
from deepwiki import ContentExtractor

html = """
<!doctype html>
<html>...</html>
"""

extractor = ContentExtractor()
print(extractor.extract_from_html(html))
```

### URL から抽出して保存

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

ファイル保存は URL 入力時のみ行われます。

### 公開リポジトリ・インデックスを検索

```bash
deepwiki-to-md --search "Gemini"
deepwiki-to-md --search "Gemini" --devlog
```

```python
from search_repository import API_URL, search_repositories

print(API_URL)
result = search_repositories("Gemini")
print("indices:", len(result.get("indices", [])))
```

### Devin API Chat

最初に Chat extra をインストールし、設定 JSON を用意してください。

```bash
pip install "deepwiki-to-md[chat]"
```

設定ファイルは必須です。Devin API に必要な設定を持つ `headers` オブジェクトと `body_template` オブジェクトの両方を記載してください。`user_query`、`repo_names`、`query_id`、`use_deep_research` など、リクエストごとに変わる値はクライアントが設定します。

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

```bash
deepwiki-to-md https://deepwiki.com/microsoft/vscode \
  --chat "このリポジトリの目的は？" \
  --config-file ./config.json
```

Chat オプション:

- `--chat MESSAGE`: 送信メッセージ。位置引数に DeepWiki URL が必須です。
- `--deep-research`: Deep Research モードを有効化します。
- `--config-file PATH`: 用意済み設定 JSON のパス（既定: `./config.json`）。
- `--devlog`: 応答と参照ファイルを人間可読形式で表示します。

Python 例:

```python
import asyncio
import json

from chat import ChatResult, load_config, send_chat_message


async def main() -> None:
    config = load_config("config.json")
    if not config:
        raise SystemExit("完全な config.json が必要です")

    result: ChatResult = await send_chat_message(
        wiki_url="https://deepwiki.com/microsoft/vscode",
        message="このリポジトリの目的は？",
        config=config,
        use_deep_research=False,
    )
    print(result)
    print(result.response_message)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
```

`ChatResult` は `dict` を継承し、`result.response_message` のような属性アクセスと `to_dict()` を提供します。

## 詳細ドキュメント

- [Python API / CLI ガイド](deepwiki_to_md.md)

## ライセンス

MIT License。詳細は [LICENSE](LICENSE) を参照してください。
