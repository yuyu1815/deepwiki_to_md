# deepwiki-to-md

Next.js/DeepWiki 由来のHTMLからMarkdownテキストを抽出するゼロ依存のCLIツール。

- CLI: `deepwiki-to-md`
- 必要要件: Python 3.8+
- 依存関係: 標準ライブラリのみ（オプション機能は extras）

## インストール

```bash
pip install deepwiki-to-md
```

## 使い方

- ローカルHTML/文字列から（CLI と Python の両方）:
```bash
# CLI
echo "<html>...</html>" | deepwiki-to-md
```
```python
# Python API
from deepwiki_to_md import ContentExtractor

html = """
<!doctype html>
<html>...</html>
"""

extractor = ContentExtractor()
md = extractor.extract_from_html(html)
print(md)
```

- URLから（保存は URL 入力時のみ）:
```bash
# CLI
# URL 入力のときのみ、.deepwiki 配下に分割保存されます
deepwiki-to-md https://deepwiki.com/microsoft/vscode/some-page --path ./.deepwiki
```
```python
# Python API（CLI と同等の動作）
from deepwiki_to_md import ContentExtractor, save_markdown_to_library

url = "https://deepwiki.com/microsoft/vscode/some-page"
base_dir = "./.deepwiki"  # --path に相当（省略可）

extractor = ContentExtractor()
md = extractor.extract_from_url(url)

result = save_markdown_to_library(md, url, base_dir)
print("saved files:")
for p in result["saved_files"]:
    print(" -", p)
print("library index:", result["library_file"])  # .deepwiki/<username>/<library>.md
```

- 検索機能（公開リポジトリ・インデックス）:
```bash
# CLI（既定は JSON 出力）
deepwiki-to-md --search "Gemini"

# 人間可読な開発ログ形式
deepwiki-to-md --search "Gemini" --devlog
```
```python
# Python API（CLI と同等の検索機能）
from search_repository import search_repositories, API_URL

print(API_URL)  # => https://api.devin.ai/ada/list_public_indexes
result = search_repositories("Gemini")
indices = result.get("indices", [])
print("indices:", len(indices))
```

- Chat（CLI）:
```bash
# 位置引数には DeepWiki の URL を指定（既定は JSON 出力）
deepwiki-to-md https://deepwiki.com/microsoft/vscode --chat "このリポジトリの目的は？"

# 開発ログ向けの人間可読出力
deepwiki-to-md https://deepwiki.com/microsoft/vscode --chat "主な特徴を要約して" --devlog
```
Chat 用オプション（deepwiki-to-md 経由）:
- `--chat MESSAGE`: 送信するメッセージ。位置引数に DeepWiki の URL が必須。
- `--deep-research`: Deep Research モードを有効化。
- `--config-file PATH`: チャット用の設定 JSON のパス（既定: ./config.json）。ファイルは事前に用意し、必要項目を記載してください。
- `--devlog`: --chat と併用で、応答本文と参照ファイルを人間可読で表示。

## ライセンス

MIT License

## 詳細ドキュメント

- ライブラリ（Python API と CLI の併記例を含む）: [deepwiki_to_md.md](deepwiki_to_md.md)

### Chat (Devin API) の結果オブジェクト: ChatResult

chat ヘルパー（src/chat.py）の send_chat_message は、辞書ではなく「オブジェクト型」の ChatResult を返します。

- 特長
  - dict を継承しているため json.dumps(result) がそのまま使えます。
  - 便利な属性アクセス（result.response_message など）と to_dict() を提供します。
  - print(result) で人間が読みやすい要約が表示されます。

- 主なプロパティ
  - sent_message: 送信したメッセージ（str）
  - response_message: 応答本文（Optional[str]）
  - status_code: ステータスコード（Any）
  - reference_files: 参照ファイルのリスト（List[str]）
  - reference_file_contents: 参照ファイルの内容（Dict[str, str]）

- 例（簡易抜粋）
```python
import asyncio
import json
from chat import load_or_create_config, send_chat_message, ChatResult

async def main() -> None:
    config = load_or_create_config('./config.json')
    if not config:
        raise SystemExit('config missing')
    result: ChatResult = await send_chat_message(
        wiki_url='https://deepwiki.com/microsoft/vscode',
        message='What is the purpose of this repository?',
        config=config,
        use_deep_research=False,
    )

    print(result)  # __str__ による要約
    print(result.response_message)  # プロパティアクセス
    print(json.dumps(result, indent=2, ensure_ascii=False))  # dict 継承のためそのまま JSON 出力

if __name__ == '__main__':
    asyncio.run(main())
```
