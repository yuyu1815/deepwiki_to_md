import re
from typing import Set

_WINDOWS_RESERVED_NAMES: Set[str] = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
_MAX_FILENAME_LENGTH = 120


def normalize_deepwiki_url(raw: str) -> str:
    """Convert an owner/repository path to a DeepWiki URL."""
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    if raw.startswith("/") or ("/" in raw and " " not in raw):
        return f"https://deepwiki.com/{raw.strip('/')}"
    return raw


def sanitize_filename(name: str, max_length: int = _MAX_FILENAME_LENGTH) -> str:
    """Return a portable filename component without path separators."""
    name = name.rstrip(". ")
    name = name.replace(" ", "_")
    name = re.sub(r"[^\w\-_.]", "", name)

    if not name:
        name = "unnamed"

    stem = name.split(".", 1)[0].upper()
    if stem in _WINDOWS_RESERVED_NAMES:
        name = f"_{name}"

    name = name[:max_length].rstrip(". ")
    return name or "unnamed"
