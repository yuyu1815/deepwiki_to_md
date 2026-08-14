# deepwiki-to-md

English README. 日本語はこちら → [README_JP.md](README_JP.md)

CLI and Python library for extracting Markdown from Next.js/DeepWiki HTML. The core extractor uses only the Python standard library. Chat support is an optional extra.

- CLI: `deepwiki-to-md`
- Requirements: Python 3.8.1+

## Install

Core extractor:

```bash
pip install deepwiki-to-md
```

Chat support (`requests` and `websockets`):

```bash
pip install "deepwiki-to-md[chat]"
```

## Usage

### Extract from an HTML string

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

### Extract from a URL and save Markdown

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

Files are saved only for URL input.

### Search public repository indexes

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

### Chat with the Devin API

Install the chat extra first and prepare a config JSON:

```bash
pip install "deepwiki-to-md[chat]"
```

The config file is required. It must contain both a `headers` object and a `body_template` object with the settings required by the Devin API. Request-specific values such as `user_query`, `repo_names`, `query_id`, and `use_deep_research` are populated by the client.

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
  --chat "What is the purpose of this repository?" \
  --config-file ./config.json
```

Chat options:

- `--chat MESSAGE`: message to send; a DeepWiki URL is required as positional input.
- `--deep-research`: enable deep research mode.
- `--config-file PATH`: required prepared config JSON path (default: `./config.json`).
- `--devlog`: print a human-readable response and reference files.

Python example:

```python
import asyncio
import json

from chat import ChatResult, load_config, send_chat_message


async def main() -> None:
    config = load_config("config.json")
    if not config:
        raise SystemExit("A complete config.json is required")

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

`ChatResult` inherits from `dict`, supports attribute access such as `result.response_message`, and provides `to_dict()`.

## More documentation

- [Python API and CLI guide](deepwiki_to_md.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
