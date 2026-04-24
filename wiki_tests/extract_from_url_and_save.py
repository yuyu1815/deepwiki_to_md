"""Example: Extract from URL and save split Markdown files under .deepwiki.

How to run:
  PYTHONPATH=src python wiki_tests/extract_from_url_and_save.py \
    --url https://deepwiki.com/microsoft/vscode \
    --path ./.deepwiki

Notes:
- This example performs real network access.
- Files are saved only for URL inputs (project policy). Local/STDIN inputs should print to stdout instead.
"""
from __future__ import annotations

import argparse
from typing import Dict, Any

from deepwiki import ContentExtractor, save_markdown_to_library


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract from URL and save to .deepwiki")
    p.add_argument(
        "--url",
        default="https://deepwiki.com/microsoft/vscode",
        help="DeepWiki page URL (default: https://deepwiki.com/microsoft/vscode)",
    )
    p.add_argument("--path", default=".deepwiki", help="Base output directory (default: .deepwiki)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    extractor = ContentExtractor()
    md = extractor.extract_from_url(args.url)

    result: Dict[str, Any] = save_markdown_to_library(md, args.url, args.path)

    print("saved files:")
    for p in result.get("saved_files", []):
        print(" -", p)
    print("library index:", result.get("library_file"))


if __name__ == "__main__":
    main()
