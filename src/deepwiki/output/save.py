import os
import logging
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

from deepwiki.core.errors import ConfigError
from deepwiki.core.utils import normalize_deepwiki_url, sanitize_filename
from deepwiki.parsing.markdown import split_markdown_by_h1


def save_markdown_to_library(md: str, source_url: str, base_dir: str = ".deepwiki", pages: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Split Markdown by H1 and save as files under .deepwiki/<username>/<library>/.

    - Also creates/overwrites a library index file: .deepwiki/<username>/<library>.md
    - Returns a dict with paths and metadata.
    - Raises ConfigError if source_url does not include /<username>/<library>.

    Parameters:
        md: The markdown content extracted from a DeepWiki/Next.js page.
        source_url: The original URL used for extraction (used to derive save path).
        base_dir: Base directory for saving outputs (default: ".deepwiki").

    Note:
        The source_url is normalized via normalize_deepwiki_url() so that
        path-like inputs such as "owner/repo" or "/owner/repo" also work.
        DeepWiki full URLs and non-DeepWiki full URLs are preserved as-is per policy.
    """
    if not source_url:
        raise ConfigError("source_url is required to determine save location")
    # Normalize according to shared policy (no-op for full deepwiki URLs and non-deepwiki URLs)
    normalized_url = normalize_deepwiki_url(source_url)
    try:
        parsed_url = urlparse(normalized_url)
    except Exception as e:
        raise ConfigError(f"Invalid source_url: {e}")
    path_parts = [p for p in (parsed_url.path or "").split('/') if p]
    if len(path_parts) < 2:
        raise ConfigError("source_url must include '/<username>/<library>' path components")
    username, library_name = path_parts[0], path_parts[1]

    output_dir = os.path.join(base_dir, username, library_name)
    os.makedirs(output_dir, exist_ok=True)

    saved_files: List[str] = []
    page_titles: List[str] = []

    if pages:
        for page in pages:
            filename = page["slug"] + ".md"
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(page["content"])
            saved_files.append(file_path)
            page_titles.append(page["title"])
    else:
        sections = split_markdown_by_h1(md)
        for section in sections:
            title = section["title"]
            section_content = section["content"]
            filename = sanitize_filename(title) + ".md"
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(section_content)
            saved_files.append(file_path)
            page_titles.append(title)

    library_file_path = os.path.join(base_dir, username, f"{library_name}.md")
    with open(library_file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {library_name} Documentation Index\n\n")
        f.write("This file contains links to all extracted documents.\n")
        f.write("Please refer to the files below for detailed information.\n\n")
        for file_path, title in zip(saved_files, page_titles):
            filename = os.path.basename(file_path)
            f.write(f"- [{title}]({library_name}/{filename})\n")

    logging.info("Saved %d sections under %s", len(saved_files), output_dir)
    return {
        "username": username,
        "library_name": library_name,
        "output_dir": output_dir,
        "saved_files": saved_files,
        "library_file": library_file_path,
    }
