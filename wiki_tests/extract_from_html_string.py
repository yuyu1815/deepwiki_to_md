"""Example: Extract Markdown from a local HTML file using ContentExtractor.

How to run:
  PYTHONPATH=src python wiki_tests/extract_from_html_string.py
  # On Windows (PowerShell):
  #   $env:PYTHONPATH="src"; python wiki_tests/extract_from_html_string.py

This script reads wiki_tests/test_deepwiki.html and prints extracted Markdown.
"""

from __future__ import annotations

from pathlib import Path

from deepwiki import ContentExtractor


def read_text(file_path: Path, encoding: str = "utf-8") -> str:
    """Read text from file path with explicit encoding.

    Keep I/O logic tiny and explicit for clarity.
    """
    with file_path.open("r", encoding=encoding) as f:
        return f.read()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    html_path = repo_root / "wiki_tests" / "test_deepwiki.html"
    if not html_path.exists():
        raise FileNotFoundError(f"Input HTML not found: {html_path}")

    html = read_text(html_path)

    extractor = ContentExtractor()
    md = extractor.extract_from_html(html)

    # Print to stdout; do not save files for local/STDIN input per project policy.
    print(md)


if __name__ == "__main__":
    main()
