# deepwiki-to-md

English README. 日本語はこちら → [README_JP.md](README_JP.md)

Zero-dependency CLI and Python library to extract Markdown from Next.js/DeepWiki HTML. Includes a small search helper for public repository indexes and an optional chat helper.

- CLI: `deepwiki-to-md`
- Requirements: Python 3.8+
- Dependencies: Standard library only (optional extras for dev/docs)

## Install

```bash
pip install deepwiki-to-md
```

## Usage

- From local HTML/string (CLI and Python):
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

- From URL (files are saved only when the input is a URL):
```bash
# CLI
# Files under .deepwiki are created only for URL input
deepwiki-to-md https://deepwiki.com/microsoft/vscode/some-page --path ./.deepwiki
```
```python
# Python API (same behavior as the CLI)
from deepwiki_to_md import ContentExtractor, save_markdown_to_library

url = "https://deepwiki.com/microsoft/vscode/some-page"
base_dir = "./.deepwiki"  # equivalent to --path (optional)

extractor = ContentExtractor()
md = extractor.extract_from_url(url)

result = save_markdown_to_library(md, url, base_dir)
print("saved files:")
for p in result["saved_files"]:
    print(" -", p)
print("library index:", result["library_file"])  # .deepwiki/<username>/<library>.md
```

- Search public repository indexes:
```bash
# CLI (JSON by default)
deepwiki-to-md --search "Gemini"

# Human-readable development-log style
deepwiki-to-md --search "Gemini" --devlog
```
```python
# Python API (same search capability)
from search_repository import search_repositories, API_URL

print(API_URL)  # => https://api.devin.ai/ada/list_public_indexes
result = search_repositories("Gemini")
indices = result.get("indices", [])
print("indices:", len(indices))
```

## License

MIT License

## More documentation

- Library reference (includes both Python API and CLI examples): [deepwiki_to_md.md](deepwiki_to_md.md)

### Chat (Devin API) result object: ChatResult

The chat helper (src/chat.py) returns a ChatResult object instead of a plain dict.

- Highlights
  - Inherits from dict → works with json.dumps(result) directly.
  - Convenient attribute access (e.g., result.response_message) and to_dict().
  - print(result) shows a human-readable summary.

- Main properties
  - sent_message: str
  - response_message: Optional[str]
  - status_code: Any
  - reference_files: List[str]
  - reference_file_contents: Dict[str, str]

- Example (excerpt)
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

    print(result)  # human-readable summary via __str__
    print(result.response_message)  # attribute access
    print(json.dumps(result, indent=2, ensure_ascii=False))  # still a dict

if __name__ == '__main__':
    asyncio.run(main())
```

