import re


class ExtractionConfig:
    """Configuration for content extraction.

    Maintenance tips:
    - Add to CONTENT_MARKERS for new content types.
    - Adjust NOISE_PATTERNS for new frameworks.
    - Revisit MIN/MAX_CHUNK_LENGTH for performance.
    """

    # Core extraction patterns
    STRING_PAYLOAD_PATTERN = re.compile(
        r'self\.__next_f\.push\(\[1,\s*"((?:\\.|[^"\\])*)"]\)',
        re.DOTALL
    )

    # Content filtering settings
    MIN_CHUNK_LENGTH = 8
    MAX_CHUNK_LENGTH = 10000

    # Content markers (expand for new content types)
    CONTENT_MARKERS = (
        "# ", "## ", "### ", "#### ",  # Markdown headings
        "```",                         # Code blocks
        "Sources:",                    # References
        "<details", "<summary",        # HTML details elements
        "mermaid",                     # Diagrams
        "graph ", "flowchart ",        # Graph syntax
        "Note:", "Warning:",           # Admonitions
        "![", "](http",               # Images and links
    )

    # Noise patterns (expand for new frameworks)
    NOISE_PATTERNS = (
        "static/chunks",
        "/_next/static",
        "$Sreact",
        "__webpack",
        "module.exports",
        "require(",
        "import {",
    )

    # RSC prefixes (update for Next.js changes)
    RSC_PREFIXES = ('["%24",', '["$', '["%24%24",')

    # Token pattern for filtering
    TOKEN_PATTERN = re.compile(r"[0-9a-z]{1,3}:[A-Za-z0-9]+,")


class HTTPConfig:
    """HTTP configuration.

    Maintenance tips:
    - Update DEFAULT_HEADERS for newer user-agents.
    - Extend ALLOWED_DOMAINS for security.
    - Tune timeout values for performance.
    """

    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "DNT": "1",
    }

    # セキュリティ: 許可ドメイン（必要に応じて拡張）/ Security: allowed domains (expand as needed)
    ALLOWED_DOMAINS = (
        "deepwiki.com",
        "*.deepwiki.com",
    )
