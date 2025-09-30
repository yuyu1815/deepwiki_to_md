from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict

# Keep the module small and dependency‑free so it can be reused from both
# CLI and library code. Network access is done with urllib to avoid extra deps.

API_URL = "https://api.devin.ai/ada/list_public_indexes"

__all__ = ["search_repositories", "API_URL"]


def search_repositories(search_term: str = "Gemini") -> Dict[str, Any]:
    """Search public indexes by repository term.

    Args:
        search_term: Value for the `search_repo` query parameter.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        RuntimeError: On non-200 HTTP status, network errors, or JSON parsing failures.
    """
    params = {"search_repo": search_term}
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
            status = getattr(resp, "status", 200)
            if status != 200:
                raise RuntimeError(f"HTTP error! status: {status}")
            data = resp.read()
            try:
                return json.loads(data.decode("utf-8"))
            except Exception as e:  # JSON decode error
                logging.exception("Failed to parse JSON from repository search API")
                raise RuntimeError("Invalid JSON from API") from e
    except urllib.error.HTTPError as e:
        logging.error("HTTP error when calling repository search API: %s", e)
        raise RuntimeError(f"HTTP error! status: {e.code}") from e
    except urllib.error.URLError as e:
        logging.error("Network error when calling repository search API: %s", e)
        raise RuntimeError(f"Network error: {e}") from e
