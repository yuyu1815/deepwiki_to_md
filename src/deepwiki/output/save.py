import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from deepwiki.core.errors import ConfigError
from deepwiki.core.utils import normalize_deepwiki_url, sanitize_filename
from deepwiki.parsing.markdown import split_markdown_by_h1


def _unique_filename(name: str, used_names: Set[str]) -> str:
    path = Path(name)
    stem = path.stem
    suffix = path.suffix
    candidate = name
    counter = 2
    while candidate.casefold() in used_names:
        candidate = f"{stem}_{counter}{suffix}"
        counter += 1
    used_names.add(candidate.casefold())
    return candidate


def _safe_output_path(output_dir: str, filename: str) -> str:
    if Path(filename).name != filename or filename in {".", ".."}:
        raise ConfigError(f"Unsafe output filename: {filename!r}")

    root = Path(output_dir).resolve()
    destination = (root / filename).resolve()
    try:
        destination.relative_to(root)
    except ValueError as exc:
        raise ConfigError(f"Output path escapes destination: {filename!r}") from exc
    return str(destination)


def save_markdown_to_library(
    md: str,
    source_url: str,
    base_dir: str = ".deepwiki",
    pages: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Save extracted Markdown under ``base_dir/<owner>/<repository>``."""
    if not source_url:
        raise ConfigError("source_url is required to determine save location")

    parsed_url = urlparse(normalize_deepwiki_url(source_url))
    path_parts = [part for part in parsed_url.path.split("/") if part]
    if len(path_parts) < 2:
        raise ConfigError(
            "source_url must include '/<username>/<library>' path components"
        )

    username = sanitize_filename(path_parts[0])
    library_name = sanitize_filename(path_parts[1])
    output_dir = os.path.join(base_dir, username, library_name)
    os.makedirs(output_dir, exist_ok=True)

    saved_files: List[str] = []
    page_titles: List[str] = []
    used_names: Set[str] = set()

    if pages:
        entries = [
            (
                str(page.get("title", "Untitled")),
                str(page.get("content", "")),
                str(page.get("slug", "unnamed")),
            )
            for page in pages
        ]
    else:
        entries = [
            (section["title"], section["content"], section["title"])
            for section in split_markdown_by_h1(md)
        ]

    for title, content, raw_filename in entries:
        safe_stem = sanitize_filename(raw_filename)
        filename = _unique_filename(f"{safe_stem}.md", used_names)
        file_path = _safe_output_path(output_dir, filename)
        with open(file_path, "w", encoding="utf-8", newline="\n") as file:
            file.write(content)
        saved_files.append(file_path)
        page_titles.append(title)

    library_file_path = os.path.join(base_dir, username, f"{library_name}.md")
    os.makedirs(os.path.dirname(library_file_path), exist_ok=True)
    with open(library_file_path, "w", encoding="utf-8", newline="\n") as file:
        file.write(f"# {library_name} Documentation Index\n\n")
        file.write("This file contains links to all extracted documents.\n\n")
        for file_path, title in zip(saved_files, page_titles):
            filename = os.path.basename(file_path)
            file.write(f"- [{title}]({library_name}/{filename})\n")

    logging.info("Saved %d sections under %s", len(saved_files), output_dir)
    return {
        "username": username,
        "library_name": library_name,
        "output_dir": output_dir,
        "saved_files": saved_files,
        "library_file": library_file_path,
    }
