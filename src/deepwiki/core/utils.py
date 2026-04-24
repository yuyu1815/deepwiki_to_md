import re


def normalize_deepwiki_url(raw):
    """Normalize DeepWiki URLs.

    If a path-like string is given (e.g., /owner/repo or owner/repo), convert it to
    https://deepwiki.com/<owner>/<repo>. Otherwise, return the input as-is.
    """
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    # Convert path-like strings (/owner/repo or owner/repo) into full URLs
    if raw.startswith("/") or ("/" in raw and " " not in raw):
        return f"https://deepwiki.com/{raw.strip('/')}"
    return raw


def sanitize_filename(name: str) -> str:
    """Normalize a string to be safe for use as a filename.

    Args:
        name: The input string to normalize.

    Returns:
        A string safe to use as a filename.
    """
    # Replace spaces with underscores
    name = name.replace(' ', '_')

    # Remove or replace invalid characters for filenames
    # This pattern allows only alphanumeric, underscores, hyphens, dots
    name = re.sub(r'[^\w\-_.]', '', name)

    # Ensure the filename is not empty
    if not name:
        name = "unnamed"

    return name
